#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time
from config import radarr, monitored, autosearch, tmdbkey

verbose = True # T
ignore_wanted = False # F
full = False # F
art = False # F
start = 0 # 0

try:
    opts, args = getopt.getopt(sys.argv[1:],"hqdfas:",["help","quiet","down","full","art","start="])
except getopt.GetoptError:
    print('Error in options\n\n run: rcm.py -h for more info')
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        from library import helptext
        for line in helptext: print(line)
        sys.exit()
    elif opt in ("-q", "--quiet"): verbose = False
    elif opt in ("-d", "--down"): ignore_wanted = True
    elif opt in ("-f", "--full"): full = True
    elif opt in ("-a", "--art"): art = True
    elif opt in ("-s", "--start"): start = int(arg)

now = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S") 

if radarr['base_url'] == "off":
    radarr['url'] = "http://%s:%s/api/movie" %(radarr['host'].strip(), radarr['port'].strip())
else:
    radarr['url'] = "http://%s%s/api/movie" %(radarr['host'].strip(), radarr['base_url'].strip())
 
#%%  funcs

def api(host, com = "get", args = {}):
    """
    radarr: get & {} | lookup & {id:} | post & {**data}
    tmdb: get & {end,id}
    """
    if host == "radarr":
        host = host.title()
        url = radarr['url']
        key = {"apikey": radarr['api_key']}
        if com == "lookup":
            url += "/lookup/tmdb"
            key.update({"tmdbid" : int(args['id'])})
        elif com == "post":
            url += "?apikey=" + radarr['api_key']
            response = requests.post(url, data = json.dumps(args))
            return response.status_code
    elif host == "tmdb":
        host = host.upper()
        if   args['end'] == "mov": end = "movie/"
        elif args['end'] == "col": end = "collection/"
        url = "https://api.themoviedb.org/3/" + end + str(args['id'])
        key = {"api_key": tmdbkey }
    
    good = False
    tries = 0 
    while not good:    
                
        response = requests.get(url, params = key )
        response.content.decode("utf-8")
        code = response.status_code
        
        if code in (200,201):           # GOOD
            good = True
            return response.json()
        elif code == 401:               # FATAL
            log("Error Unauthorized - Please check your %s API key" %host)
            sys.exit(2)
        elif code == 404:               # MINOR
            good = True
            return code
        elif code == 429:               # RETRY
            wait = int(response.headers["Retry-After"]) + 1
            if verbose: print("\n" + "Too many requests - waiting %i seconds \n" %wait)
            time.sleep(wait) 
        else:                           # UNKNOWN
            while tries < 5 :           ## RETRY
                tries += 1
                log("Unplanned error from %s API, return code: %i - Retrying, attempt %i \n" %(host,code,tries))
                time.sleep(5) 
            else:                       ## LIMIT
                if not verbose: print("Fatal Error - Retry limit reached - Exiting at item %i \n" %i)
                log("Fatal Error - Retry limit reached - Exiting at item %i \n" %i)
                sys.exit(2)
    
def log(text):
    if verbose: print(text.encode('utf-8', 'replace'))
    try:
        f.write(text.encode('utf-8', 'replace') + '\n')
    except:
        f.write("---- unkown error in logging ---- \n")

#%% Output folder checks
        
if not os.path.exists("logs"):
    os.mkdir("logs")

if not os.path.exists("output"):
    os.mkdir("output")

#%% Opening
        
f = open('logs/log_' + now + '.txt','w')
    
log('Welcome to Radarr Collection Manager by RhinoRhys \n')

data = api("radarr")

if start > len(data):
    if not verbose: print("Fatal Error - Start point too high - Exiting \n")
    log("Fatal Error - Start point too high - Exiting \n")
    sys.exit(2)    

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]

if not full:
    try:
        s = open("skip.dat", "r+")
        skip = s.readlines()[0].strip('[]\n').split(', ')
        skip = [int(skip[i]) for i in range(len(skip))]
        
        log('Running partial scan: only checking movies added since last run\n')
        
    except:
        skip = []
        log('Running full scan: checking all items\n')
else:
    skip = []
    log('Running full scan: checking all items\n')

if ignore_wanted: log("Ignore wanted list active: only checking movies with files\n")

if start != 0: log("Start point specified: skipping %i items\n" %start)

if art: log("Collection Artwork URLs will be saved to output/art.txt\n")
    
get, cols, wanted = [],[],[]

#%% Check loop

for i in range(start,len(data)):
    
    if ignore_wanted and not data[i]['hasFile']: wanted.append(data[i]['tmdbId'])
    
    logtext = datetime.datetime.now().strftime("[ %y-%m-%d %H:%M:%S ] ") + "Radarr ID: %i \t TMDB ID: %i \t\t %s" % (data[i]['id'], data[i]["tmdbId"], data[i]['title'])
    
    if data[i]["tmdbId"] not in skip and data[i]["tmdbId"] not in wanted:
        
        mov_json = api("tmdb", args = {"end": "mov", "id": data[i]["tmdbId"]})
        
        if mov_json == 404: log(logtext + "\t\t Error - Not Found")
        elif mov_json.has_key('belongs_to_collection') == False: log(logtext + "\t\t Error - Collection Key Not Found")
        
        elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
            col_id = mov_json['belongs_to_collection']['id']
            logtext += "\t\t Collection: %i" % col_id
            
            col_json = api("tmdb", args = {"end": "col", "id": col_id})
            if art: cols.append('%s \t\t https://image.tmdb.org/t/p/original%s' %(col_json['name'], col_json['poster_path']))
            parts = [col_json['parts'][j]['id'] for j in range(len(col_json['parts']))]
            parts.remove(int(data[i]["tmdbId"]))
           
            logtext += "\t\t %i other items" % len(parts)
            
            log(logtext)
            
            # Collection Items Check
            for part in parts:
                if part in tmdb_ids:
                    skip.append(part)
                    log("\t\t > %s in library, remembering to skip" % data[tmdb_ids.index(part)]['title'])
                    
                else:
                    lookup_json = api("radarr", com = "lookup", args = {'id': part})
                    log("\t\t > %s \t (TMDB ID: %i) missing, fetching" %(lookup_json['title'], part))
                    
                    post_data = {"qualityProfileId" : data[i]['qualityProfileId'],
                                 "rootFolderPath": os.path.split(data[i]['path'])[0],
                                 "monitored" : monitored,
                                 "addOptions" : {"searchForMovie" : autosearch},
                                 }
                    for dictkey in ["tmdbId","title","titleSlug","images","year"]:
                        post_data.update({dictkey : lookup_json[dictkey]})
                    post = api("radarr", com = "post", args = post_data)
                    code = post == 201
                    log(" >> Added: %s  [code: %s]" %(str(code),str(post)))
                    get.append({'title': post_data['title'], 
                                'year': post_data['year'], 
                                'tmdb id': post_data['tmdbId'],
                                'return code': post})
                    tmdb_ids.append(post_data['tmdbId'])
        else: log(logtext + "\t\t Not in collection") # if mov_json = 404
    else: log(logtext + "\t\t Skipping") # if id in list
        
log("\n Added %i movies \n\n Thank You for using Radarr Collection Manager by RhinoRhys" % len(get))

f.close()

#%% Output files

if len(get) > 0:
    g = open('output/added_%s.txt' %now,'w')
    g.write("Movies added: " + str(len(get)) + "\n\n")
    for item in get:
        g.write(str(item) + '\n')
    g.close()
   

if art:
    cols.sort()
    t = open('output/art.txt', 'w+')
    for line in cols:
        t.write(line.encode("utf-8", "replace") + '\n')
    t.close()

s = open('skip.dat','w')
s.write(str(tmdb_ids))
s.close()

