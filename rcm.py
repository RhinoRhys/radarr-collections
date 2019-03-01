#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time, atexit
from config import radarr, monitored, autosearch, tmdbkey
import library

verbose = True # T
ignore_wanted = False # F
full = False # F
art = False # F
nolog = False # F
cache = False # F
start = 0 # 0

try:
    opts, args = getopt.getopt(sys.argv[1:],"hqdfas:nc",["help","quiet","down","full","art","start=","nolog","cache"])
except getopt.GetoptError:
    print('Error in options\n\n run: rcm.py -h for more info')
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        for line in library.helptext: print(line)
        sys.exit()
    elif opt in ("-q", "--quiet"): verbose = False
    elif opt in ("-d", "--down"): ignore_wanted = True
    elif opt in ("-f", "--full"): full = True
    elif opt in ("-a", "--art"): art = True
    elif opt in ("-s", "--start"): start = int(arg)
    elif opt in ("-n", "--nolog"): nolog = True
    elif opt in ("-c", "--cache"): cache = True

now = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") 

if radarr['base_url'] == "off":
    radarr['url'] = "http://%s:%s/api/movie" %(radarr['host'].strip(), radarr['port'].strip())
else:
    radarr['url'] = "http://%s%s/api/movie" %(radarr['host'].strip(), radarr['base_url'].strip())
 
#%%  API function

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
            log(library.api_auth %host)
            sys.exit(2)
        elif code == 404:               # MINOR
            good = True
            return code
        elif code == 429:               # RETRY
            wait = int(response.headers["Retry-After"]) + 1
            if verbose: print(library.api_wait %wait)
            time.sleep(wait) 
        else:                           # UNKNOWN
            while tries < 5 :           ## RETRY
                tries += 1
                log(library.api_misc %(host,code,tries))
                time.sleep(5) 
            else:                       ## LIMIT
                if not verbose: print(library.api_retry %i)
                log(library.api_retry %i)
                sys.exit(2)
    
#%% Output files

def log(text):
    if verbose: print(text.encode('utf-8', 'replace'))
    if not nolog:
        try:
            f.write(text.encode('utf-8', 'replace') + '\n')
        except:
            f.write("---- unkown error in logging ---- \n")

def datadump():
    
    if len(get) > 0 and cache:
        g = open(os.path.join('output','added_%s.txt' %now),'w+')
        g.write("Movies Found: %i \n\n" %len(get))
        for item in get:
            g.write(str(item) + '\n')
        g.close()
    
    if art:
        cols.sort()
        t = open(os.path.join('output','art_%s.txt' %now), 'w+')
        for line in cols:
            t.write(line.encode("utf-8", "replace") + '\n')
        t.close()
    
    s = open('skip.dat','w+')
    s.write(str(tmdb_ids))
    s.close()
    
    log(library.bye % len(get))

    if not nolog: f.close() 

#%% Output folder checks
        
if not os.path.exists("logs"):
    os.mkdir("logs")

if not os.path.exists("output"):
    os.mkdir("output")

#%% Opening
        
if not nolog: f = open(os.path.join('logs',"log_%s.txt" %now),'w+')

atexit.register(datadump)
    
log(library.hello)
    
data = api("radarr")

if start > len(data):
    if not verbose: print(library.start_err)
    log(library.start_err)
    sys.exit(2)  

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]

if not full:
    try:
        s = open("skip.dat", "r+")
        skip = s.readlines()[0].strip('[]\n').split(', ')
        skip = [int(skip[i]) for i in range(len(skip))]
        
        log(library.partial)
        
    except:
        skip = []
        log(library.full)
else:
    skip = []
    log(library.full)

if ignore_wanted: log(library.wanted)

if start != 0: log(library.start %start)

if art and not nolog: log(library.art)
    
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
                    log("\t\t > %s \t (TMDB ID: %i) missing from library" %(lookup_json['title'], part))
                    
                    post_data = {"qualityProfileId" : data[i]['qualityProfileId'],
                                 "rootFolderPath": os.path.split(data[i]['path'])[0],
                                 "monitored" : monitored,
                                 "addOptions" : {"searchForMovie" : autosearch},
                                 }
                    for dictkey in ["tmdbId","title","titleSlug","images","year"]:
                        post_data.update({dictkey : lookup_json[dictkey]})
                    if not cache:
                        post = api("radarr", com = "post", args = post_data)
                        success = post == 201
                        log(" >> Added: %s  [code: %s]" %(str(success),str(post)))
                        tmdb_ids.append(post_data['tmdbId'])
                    get.append("%s \t TMDB ID: %i \t %s (%i)" %(col_json['name'], post_data['tmdbId'], post_data['title'], post_data['year']))
        else: log(logtext + "\t\t Not in collection") # if mov_json = 404
    else: log(logtext + "\t\t Skipping") # if id in list
        


