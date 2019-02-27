#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, json, datetime
from config import radarr, monitored, autosearch, full, tmdbkey

time = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") 

if radarr['base_url'] == "/":
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
        elif com == "put":
            url += "?apikey=" + radarr['api_key']
            response = requests.put(url, data = json.dumps(args))
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
    f = open('logs/log' + time + '.txt','a')
    print(text)
    try:
        f.write(text.encode('utf-8', 'replace') + '\n')
    except:
        f.write("---- unkown error in logging ---- \n")
    f.close()

#%%

f = open('logs/log' + time + '.txt','w').close()

data = api("radarr")

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]


if full == False:
    s = open('skip.dat','r')
    skip = s.readlines()[0].strip('[]\n').split(', ')
    skip = [int(skip[i]) for i in range(len(skip))]
else:
    skip = []
    

singles = []
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
            cols.append(col_json)
            parts = [col_json['parts'][j]['id'] for j in range(len(col_json['parts']))]
            other = parts[:]
            other.remove(int(data[i]["tmdbId"]))
           
            logtext += "\t\t %i other items" % len(other)
            
            # Single Movie Collections Notifier
            if len(other) == 0:
                logtext += ", added to errors"
                singles.append({"title": mov_json['title'], 
                                "tmdb id": data[i]["tmdbId"], 
                                "collection": col_json['name'],
                                "collection id": col_json['id']
                                })
            log(logtext)
            
            # Collection Items Check
            for part in other:
                if part in tmdb_ids:
                    skip.append(part)
                    log(" > TMDB ID " + str(part) + " in library, remembering to skip")
                    
                else:
                    lookup_json = api("radarr", com = "lookup", args = {'id': part})
                    log(" > " + lookup_json['title'] + " (TMDB ID: " + str(part) + ") missing, fetching")
                    post_data = {"qualityProfileId" : radarr["profile"],
                                 "rootFolderPath": radarr['path'],
                                 "monitored" : monitored,
                                 "addOptions" : {"searchForMovie" : autosearch},
                                 }
                    for dictkey in ["tmdbId","title","titleSlug","images","year"]:
                        post_data.update({dictkey : lookup_json[dictkey]})
                    post = api("radarr", com = "post", args = post_data)
                    code = post == 201
                    log(' >> Added: ' + str(code) + "  [code: " + str(post) + "]")
                    get.append({'title': post_data['title'], 
                                'year': post_data['year'], 
                                'tmdb id': post_data['tmdbId'],
                                'return code': post})
                    tmdb_ids.append(post_data['tmdbId'])
        else:
            logtext += "\t\t" + "Not in collection"
            log(logtext)
    else:
        logtext += "\t\t" + "Skipping - Checked"
        log(logtext)
        
log("\n Added " + str(len(get)) + " items \n\n Thank You")

if len(get) > 0:
    g = open('added ' + time + '.txt','w')
    g.write("Movies added: " + str(len(get)) + "\n\n")
    for item in get:
        g.write(str(item) + '\n')
    g.close()

if len(singles) > 0:
    h = open('singles ' + time + '.txt','w')
    h.write("Movies in single collections \n\n")
    for item in singles:
        h.write(str(item) + '\n')
    h.close()
    log("\n Exported list of single collections")

with open('data.json', 'w') as out:
    json.dump(data, out)
out.close()
   
with open('collection.json', 'w') as outfile:
    json.dump(cols, outfile)
outfile.close()

s = open('skip.dat','w')
s.write(str(tmdb_ids))
s.close()
