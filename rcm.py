#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time, atexit
from config import radarr, monitored, autosearch, tmdbkey
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

now = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") 

if radarr['base_url'] == "off": radarr['url'] = "http://%s:%s/api/movie" %(radarr['host'].strip(), radarr['port'].strip())
else: radarr['url'] = "http://%s%s/api/movie" %(radarr['host'].strip(), radarr['base_url'].strip())
   
#%% Output files

if not os.path.exists("logs"): os.mkdir("logs")
if not os.path.exists("output"): os.mkdir("output")
    
def log(text):
    if verbose: print(text.encode('utf-8', 'replace'))
    if not nolog: f.write(text.encode('utf-8', 'replace') + '\n')

def datadump():
    if len(found) != 0 and cache:
        if fails == 10: log(words.auto_cache %now)
        found.sort()
        g = open(os.path.join('output','found_%s.txt' %now),'w+')
        g.write("Movies Found: %i \n\n" %len(found))
        for item in found: g.write(item.encode("utf-8", "replace") + '\n')
        g.close()
        
    if art:
        cols.sort()
        g = open(os.path.join('output','art_%s.txt' %now), 'w+')
        for line in cols: g.write(line.encode("utf-8", "replace") + '\n')
        g.close()
    
    g = open('skip.dat','w+')
    g.write(str(tmdb_ids))
    g.close()
    
    log(words.bye % len(found))
    if not nolog: f.close() 
 
#%%  API function

def fatal(error, kwargs=None):
    if not verbose: print(error.encode('utf-8', 'replace') %kwargs)
    log(error %kwargs)
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
        url = "https://api.themoviedb.org/3/" + end + str(args['id'])
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
        elif code == 401: fatal(words.api_auth, host)       # FATAL
        elif code == 404:                                   # MINOR
            good = True
            return code
        elif code == 429:                                   # RETRY
            wait = int(response.headers["Retry-After"]) + 1
            if verbose: print(words.api_wait.encode('utf-8', 'replace') %wait)
            time.sleep(wait)
        else:                                               # UNKNOWN
            if tries < 5 :                                     ## RETRY
                tries += 1
                print(words.api_misc.encode('utf-8', 'replace') %(host,code,tries))
                time.sleep(5) 
            else: fatal(words.api_retry, (host,i))           ## LIMITED
                

#%% Opening
        
if not nolog: f = open(os.path.join('logs',"log_%s.txt" %now),'w+')

log(words.hello)
data = api("Radarr")

if start > len(data):
    fatal(words.start_err)

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]
title_top = max([len(data[i]["title"]) for i in range(len(data))]) + 2
rad_top = len(str(data[-1]['id'])) + 1

if not full:
    try:
        s = open("skip.dat", "r+")
        skip = s.readlines()[0].strip('[]\n').split(', ')
        skip = [int(skip[i]) for i in range(len(skip))]
        new = len(data) - len(skip)
        log(words.partial %new)
    except:
        skip = []
        log(words.full)
else:
    skip = []
    log(words.full)

if cache: log(words.cache)
if start != 0: log(words.start %start)
log(words.scan %(len(data)-start))
if ignore_wanted: log(words.wanted)
if art and not nolog: log(words.art)

#%% Check loop

found, cols = [],[]
fails = 0 
atexit.register(datadump)

for i in range(start,len(data)):
    def whitespace(tmdbId, title, year, rad_id):
        w_id, w_title, w_rad = "","",""
        w_id += " "*(10 - len(str(tmdbId)))
        w_title += " "*(title_top - len(title))
        if year == 0: w_title += " "*3
        w_rad += " "*(rad_top - len(str(rad_id)))
        return w_rad, w_id, w_title
    
    def mov_info(index):
        w_rad, w_id, w_title = whitespace(data[index]["tmdbId"], data[index]['title'], data[index]['year'], data[index]['id'])
        return (data[index]['id'], w_rad, data[index]["tmdbId"], w_id, data[index]['title'], data[index]['year'], w_title)
    
    white_dex = ""
    white_dex += " "*(len(str(len(data))) + 1 - len(str(i)))
    logtext = "%i:%s" %(i,white_dex) + datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S] ") \
            + (words.radarr + words.mov_info) %mov_info(i)
    
    if any([not all([ignore_wanted, not data[i]['hasFile']]), not ignore_wanted]) \
    and data[i]["tmdbId"] not in skip:
        mov_json = api("TMDB", args = {"end": "mov", "id": data[i]["tmdbId"]})
      
        if mov_json == 404: log(logtext + "Error - Not Found")
        elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
            col_id = mov_json['belongs_to_collection']['id']
            logtext += "Collection: %i" % col_id
            col_json = api("TMDB", args = {"end": "col", "id": col_id})
            white_name = ""
            if len(col_json['name']) < 50: top_c = 50
            else: top_c = len(col_json['name']) + 5
            white_name += " "*(top_c - len(col_json['name'])) 
            if art: cols.append('%s%s https://image.tmdb.org/t/p/original%s' %(col_json['name'], white_name, col_json['poster_path']))
            parts = [col_json['parts'][j]['id'] for j in range(len(col_json['parts']))]
            log(logtext)
            try: parts.remove(int(data[i]["tmdbId"]))
            except: pass
            log("\n" + words.other %(col_json['name'],len(parts)) + "\n")
            # Collection Items Check
            for part in parts:
                if part in tmdb_ids:
                    skip.append(part) 
                    log(words.in_data %mov_info(tmdb_ids.index(part)))
                else:
                    lookup_json = api("Radarr", com = "lookup", args = {'id': part})
                    w_rad, w_id, w_title = whitespace(part, lookup_json['title'], lookup_json['year'], "")
                    log(words.not_data %(w_rad, part, w_id, lookup_json['title'], lookup_json['year'], w_title))
                    post_data = {"qualityProfileId" : int(data[i]['qualityProfileId']),
                                 "rootFolderPath": os.path.split(data[i]['path'])[0].encode(sys.getfilesystemencoding()),
                                 "monitored" : monitored,
                                 "addOptions" : {"searchForMovie" : autosearch},}
                    for dictkey in ["tmdbId","title","titleSlug","images","year"]: post_data.update({dictkey : lookup_json[dictkey]})
                    if not cache:
                        post = api("Radarr", com = "post", args = post_data)
                        white_yn = ""
                        white_yn += " "*(rad_top + 10)
                        if post != 201:
                            log(words.add_fail %(white_yn,post))
                            fails += 1
                            if fails == 10:
                                cache = True
                                print(words.retry_err.encode('utf-8', 'replace'))
                        else: log(words.add_true %white_yn)
                        tmdb_ids.append(post_data['tmdbId'])
                    white_cid = ""
                    white_cid += " "*(15 - len(str(data[i]["tmdbId"])))
                    found.append(words.found %(col_json['name'], white_name, post_data['tmdbId'], white_cid, post_data['title'], post_data['year']))
            log("")
        else: log(logtext + "Not in collection") # if mov_json == 404
    else: log(logtext + "Skipping") # if id in list
