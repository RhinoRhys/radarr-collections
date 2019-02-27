#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt
from config import radarr, monitored, autosearch, tmdbkey

full = False

try:
    opts, args = getopt.getopt(sys.argv[1:],"hft:c:",["full","tmdbid=","colid="])
except getopt.GetoptError:
    print 'rcm.py -h'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('rcm.py <option> [<id>] \n\n Options: \n -h \t help \n -f \t full scan') #(TO DO) \n -t # \t search single movie ID \n -c # \t search single collection ID
        sys.exit()
    elif opt in ("-f", "--full"):
        full = True
    elif opt in ("-t", "--tmdbid"):
        print("tmdb scan")
    elif opt in ("-c", "--colid"):
        print("collection scan")
        
    

time = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") 

if radarr['base_url'] == "":
    radarr['url'] = "http://" + radarr['host'] + ":" + radarr['port'] + "/api/movie"
else:
    radarr['url'] = "http://" + radarr['host'] + radarr['base_url'] + "/api/movie"


def api(host, com = "get", args = {}):
    """
    radarr: get & {} | lookup & {id:} | post & {**data}
    tmdb: get & {end,id}
    """
    if host == "radarr":
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
        if args['end'] == "mov":
            end = "movie/"
        elif args['end'] == "col":
            end = "collection/"
        url = "https://api.themoviedb.org/3/" + end + str(args['id'])
        key = {"api_key": tmdbkey }
        
    response = requests.get(url, params = key )
    response.content.decode("utf-8")
    return response.json()

def log(text):
    print(text.encode('utf-8', 'replace'))
    try:
        f.write(text.encode('utf-8', 'replace') + '\n')
    except:
        f.write("---- unkown error in logging ---- \n")

#%%
if not os.path.exists("logs"):
    os.mkdir("logs")

if not os.path.exists("output"):
    os.mkdir("output")

#%%
        
f = open('logs/log' + time + '.txt','w')
    
log('Welcome to Radarr Collection Manager by RhinoRhys \n')

data = api("radarr")

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]

if full == False:
    try:
        s = open("skip.dat", "r+")
        skip = s.readlines()[0].strip('[]\n').split(', ')
        skip = [int(skip[i]) for i in range(len(skip))]
        
        log('Running partial scan\n')
        
    except:
        skip = []
        log('Running full scan\n')
else:
    skip = []
    log('Running full scan\n')
    
get = []
cols = []

#%%

for i in range(len(data)):
    
    logtext = datetime.datetime.now().strftime("[ %y-%m-%d %H:%M:%S ] ") + "Radarr ID: %i \t TMDB ID: %i \t\t %s" % (i+1, data[i]["tmdbId"], data[i]['title'])
    
    if data[i]["tmdbId"] not in skip:
        
        mov_json = api("tmdb", args = {"end": "mov", "id": data[i]["tmdbId"]})
        
        if mov_json == {"status_code":34,"status_message":"The resource you requested could not be found."}:
            logtext += "\t\t Error - Not Found"
            log(logtext)
            
        elif mov_json.has_key('belongs_to_collection') == False:
            logtext += "\t\t Error - Collection Key Not Found"
            log(logtext)
        
        elif type(mov_json['belongs_to_collection']) != type(None):
            col_id = mov_json['belongs_to_collection']['id']
            logtext += "\t\t Collection: %i" % col_id
            
            col_json = api("tmdb", args = {"end": "col", "id": col_id})
            cols.append('%s \t\t https://image.tmdb.org/t/p/original%s' %(col_json['name'], col_json['poster_path']))
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
                    post_data = {"qualityProfileId" : radarr["profile"],
                                 "rootFolderPath": radarr['path'],
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
        else: # if mov_json
            logtext += "\t\t" + "Not in collection"
            log(logtext)
    else: # if data
        logtext += "\t\t" + "Skipping - Checked"
        log(logtext)
        
log("\n Added %i movies \n\n Thank You for using Radarr Collection Manager by RhinoRhys" % len(get))

f.close()

#%% Output files

if len(get) > 0:
    g = open('output/added ' + time + '.txt','w')
    g.write("Movies added: " + str(len(get)) + "\n\n")
    for item in get:
        g.write(str(item) + '\n')
    g.close()
   
cols.sort()
t = open('output/art.txt', 'w')
for line in cols:
    t.write(line.encode("utf-8", "replace") + '\n')
t.close()

s = open('skip.dat','w')
s.write(str(tmdb_ids))
s.close()

