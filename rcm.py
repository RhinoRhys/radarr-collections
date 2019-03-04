#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time, atexit
from config import radarr, monitored, autosearch, tmdbkey, force_ignore
import words

verbose = True # T
ignore_wanted = False # F
full = False # F
art = False # F
nolog = False # F
cache = False # F
start = 0 # 0

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hqdfas:nc",["help","quiet","down","full","art","start=","nolog","cache"])
    except getopt.GetoptError:
        print('Error in options\n\n')
        for line in words.helptext: print(line)
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            for line in words.helptext: print(line)
            sys.exit()
        elif opt in ("-q", "--quiet"): verbose = not verbose
        elif opt in ("-d", "--down"): ignore_wanted = not ignore_wanted
        elif opt in ("-f", "--full"): full = not full
        elif opt in ("-a", "--art"): art = not art
        elif opt in ("-s", "--start"): start = int(arg)
        elif opt in ("-n", "--nolog"): nolog = not nolog
        elif opt in ("-c", "--cache"): cache = not nolog

start_time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") 

if radarr['base_url'] == "off": radarr['url'] = "http://{0}:{1}/api/movie".format(radarr['host'].strip(), radarr['port'].strip())
else: radarr['url'] = "http://{0}{1}/api/movie".format(radarr['host'].strip(), radarr['base_url'].strip())

if start != 0: full = True
   
#%% Output files

if not os.path.exists("logs"): os.mkdir("logs")
if not os.path.exists("output"): os.mkdir("output")
    
def log(text):
    global printtime
    if printtime and text not in ("", "\n"): pay = datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S] ") + text.encode('utf-8', 'replace')
    else: pay = text.encode('utf-8', 'replace')
    if verbose: print(pay)
    if not nolog: f.write(pay + '\n')

def whitespace(tmdbId, title, year, rad_id):
    w_id = " "*(10 - len(str(tmdbId)))
    w_title = " "*(title_top - len(title))
    if year == 0: w_title += " "*3
    w_rad = " "*(rad_top - len(str(rad_id)))
    return w_rad, w_id, w_title

def mov_info(index):
    w_rad, w_id, w_title = whitespace(data[index]["tmdbId"], data[index]['title'], data[index]['year'], data[index]['id'])
    return data[index]['id'], w_rad, data[index]["tmdbId"], w_id, data[index]['title'], data[index]['year'], w_title

def datadump():
    if len(found_col) != 0 and cache:
        if fails == 10: log(words.auto_cache.format(start_time))
        found_col.sort()
        g = open(os.path.join('output','found_{0}.txt'.format(start_time)),'w+')
        g.write(words.found_open.format(len(found_col),len(found_col)))
        for item in found_col: g.write(item.encode("utf-8", "replace") + '\n')
        g.close()
        
    if art:
        col_art.sort()
        g = open(os.path.join('output','art_{0}.txt'.format(start_time)), 'w+')
        for line in col_art: g.write(line.encode("utf-8", "replace") + '\n')
        g.close()
    
    g = open('memory.dat','w+')
    g.write(str(tmdb_ids) + "\n")
    g.write(str(col_ids))
    g.close()
    
    global printtime
    printtime = False
    log(words.bye.format(len(found_col)))
    if not nolog: f.close() 
 
#%%  API function

def fatal(error):
    if not verbose: print(error.encode('utf-8', 'replace'))
    log(error)
    sys.exit(2)

def api(host, com = "get", args = {}):
    """
    radarr: get & {} | lookup & {id:} | post & {**data}
    tmdb: get & {end,id}
    """
    if host == "Radarr":
        url = radarr['url']
        key = {"apikey": radarr['api_key']}
        if com == "lookup":
            url += "/lookup/tmdb"
            key.update({"tmdbid" : int(args['id'])})
        elif com == "post":
            url += "?apikey=" + radarr['api_key']
            response = requests.post(url, data = json.dumps(args))
            return response.status_code
    elif host == "TMDB":
        if   args['end'] == "mov": end = "movie/"
        elif args['end'] == "col": end = "collection/"
        url = "https://api.themoviedb.org/3/{0}{1}".format(end, str(args['id']))
        key = {"api_key": tmdbkey }
    
    good = False
    tries = 0
    while not good:    
        response = requests.get(url, params = key )
        response.content.decode("utf-8")
        code = response.status_code 
        
        if code == 200:                                     # GOOD
            good = True
            return response.json()
        elif code == 401: fatal(words.api_auth.format(host))       # FATAL
        elif code == 404:                                   # MINOR
            good = True
            return code
        elif code == 429:                                   # RETRY
            wait = int(response.headers["Retry-After"]) + 1
            if verbose: print(words.api_wait.encode('utf-8', 'replace').format(wait))
            time.sleep(wait)
        elif code in (502,503): fatal(words.offline.format(host,i)) # FATAL
        else:                                               # UNKNOWN
            if tries < 5 :                                     ## RETRY
                tries += 1
                print(words.api_misc.encode('utf-8', 'replace').format(host,code,tries))
                time.sleep(5) 
            else: fatal(words.api_retry.format(host,i))           ## LIMITED
                
#%% Collection Checker

def collection_check(col_id):
    global cache, fails
    col_json = api("TMDB", args = {"end": "col", "id": col_id})
    if len(col_json['name']) < 60: top_c = 60
    else: top_c = len(col_json['name']) + 5
    white_name = " "*(top_c - len(col_json['name'])) 
    if art: col_art.append(words.col_art.format(col_json['name'], white_name, col_json['poster_path']))
    parts = [col_json['parts'][j]['id'] for j in range(len(col_json['parts']))]
    number = len(parts)
    if any([full, all([not full, data[i]["tmdbId"] not in skip])]):
        try: parts.remove(int(data[i]["tmdbId"]))
        except: pass
        log("")
    if full: payload = two_dex, "> ", col_json['name'], col_id, number
    else: payload = str(i) + ":", white_dex, col_json['name'], col_id, number
    log(words.other.format(*payload) + "\n")
    for part in parts:  # Collection Items Check
        if part in tmdb_ids:
            skip.append(part) 
            log(words.in_data.format(*mov_info(tmdb_ids.index(part))))
        else:
            lookup_json = api("Radarr", com = "lookup", args = {'id': part})
            w_rad, w_id, w_title = whitespace(part, lookup_json['title'], lookup_json['year'], "")
            payload = "", w_rad, part, w_id, lookup_json['title'], lookup_json['year'], w_title
            if part in force_ignore: log(words.ignore.format(*payload))
            else:
                log(words.not_data.format(*payload))
                post_data = {"qualityProfileId" : int(data[i]['qualityProfileId']),
                             "rootFolderPath": os.path.split(data[i]['path'])[0].encode(sys.getfilesystemencoding()),
                             "monitored" : monitored,
                             "addOptions" : {"searchForMovie" : autosearch}}
                for dictkey in ["tmdbId","title","titleSlug","images","year"]: post_data.update({dictkey : lookup_json[dictkey]})
                white_cid = " "*(15 - len(str(post_data["tmdbId"])))
                found_col.append(words.found.format(col_json['name'], white_name, post_data['tmdbId'], white_cid, post_data['title'], post_data['year']))
                if not cache:
                    post = api("Radarr", com = "post", args = post_data)
                    white_yn = " "*(rad_top + 10)
                    if post == 201: 
                        log(words.add_true.format(white_yn))
                        tmdb_ids.append(post_data['tmdbId'])
                    else:
                        log(words.add_fail.format(white_yn,post))
                        fails += 1
                        if fails == 10:
                            cache = True
                            print(words.retry_err.encode('utf-8', 'replace')) 
    if any([full, all([not full, data[i]["tmdbId"] not in skip])]): log("")

#%% Opening
        
if not nolog: f = open(os.path.join('logs',"log_{}.txt".format(start_time)),'w+')

printtime = False
log(words.hello)
data = api("Radarr")

if start > len(data): fatal(words.start_err.format(start, int(len(data))))

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]
title_top = max([len(data[i]["title"]) for i in range(len(data))]) + 2
rad_top = len(str(data[-1]['id'])) + 1

found_col, col_art, col_ids = [],[],[]
fails = 0

if cache: log(words.cache)
if art and not nolog: log(words.art)
if start != 0: log(words.start.format(start))

try: 
    s = open("memory.dat", "r+")
    s = s.readlines()
    col_ids = s[1].strip('[]\n').split(', ')
    col_ids = [int(col_ids[i]) for i in range(len(col_ids))]
except: 
    full = True

if full:
    skip = []
    log(words.full.format(len(data) - start))
else:
    skip = s[0].strip('[]\n').split(', ')
    skip = [int(skip[i]) for i in range(len(skip))] 
    log(words.partial.format((len(data) - len(skip)),len(col_ids)))

if ignore_wanted: log(words.wanted)
printtime = True

atexit.register(datadump)

two_dex = " "*len(str(len(data)))

#%%  Database Search

for i in range(start,len(data)):
    white_dex = " "*(len(str(len(data))) + 1 - len(str(i)))
    payload = mov_info(i)
    logtext = "{0}:{1}".format(i, white_dex) + words.radarr.format(*payload) + words.mov_info.format(*payload)
    
    if any([not all([ignore_wanted, not data[i]['hasFile']]), not ignore_wanted]) \
    and data[i]["tmdbId"] not in skip:
        mov_json = api("TMDB", args = {"end": "mov", "id": data[i]["tmdbId"]})
        if mov_json == 404: log(logtext + "Error - Not Found")
        elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
            col_id = mov_json['belongs_to_collection']['id']
            if col_id not in col_ids: col_ids.append(col_id)
            log(logtext + "In Collection")
            collection_check(col_id)            
        else: log(logtext + "Not in Collection") # if mov_json == 404
    elif full: log(logtext + "Skipping") # if id in list
if full: log("")

#%% Collection Monitor
    
if not full:
    printtime = False
    log(words.run_col_mon.format(len(col_ids)))
    printtime= True
    for i, col_id in enumerate(col_ids):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i)))
        collection_check(col_id)
        log("")
    log("")