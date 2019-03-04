#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time, atexit
from config import radarr, monitored, autosearch, tmdbkey, force_ignore, people
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
        elif opt in ("-q", "--quiet"): verbose = False
        elif opt in ("-d", "--down"): ignore_wanted = True
        elif opt in ("-f", "--full"): full = True
        elif opt in ("-a", "--art"): art = True
        elif opt in ("-s", "--start"): start = int(arg)
        elif opt in ("-n", "--nolog"): nolog = True
        elif opt in ("-c", "--cache"): cache = True

start_time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") 

if radarr['base_url'] == "off": radarr['url'] = "http://{0}:{1}/api/movie".format(radarr['host'].strip(), radarr['port'].strip())
else: radarr['url'] = "http://{0}{1}/api/movie".format(radarr['host'].strip(), radarr['base_url'].strip())

if start != 0: full = True
printtime = False
   
#%% Output files

if not os.path.exists("logs"): os.mkdir("logs")
if not os.path.exists("output"): os.mkdir("output")
    
def log(text):
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
    global printtime
    if len(found_col)+len(found_per) != 0 and cache:
        if fails == 10: 
            printtime = False
            log("\n" + words.auto_cache.format(start_time))
        found_col.sort()
        found_per.sort()
        g = open(os.path.join('output','found_{0}.txt'.format(start_time)),'w+')
        payload = len(found_col) + len(found_per), len(found_col), len(found_per)
        g.write(words.found_open.format(*payload) + "\n")
        if len(found_col) != 0: g.write(words.found_start.format(*payload) + "\n")
        for item in found_col: g.write(item.encode("utf-8", "replace") + '\n')
        if len(found_col) != 0: g.write("\n")
        if len(found_per) != 0: g.write(words.found_middle.format(*payload) + "\n")
        for item in found_per: g.write(item.encode("utf-8", "replace") + '\n')
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
    
    printtime = False
    log(words.bye.format(len(found_col) + len(found_per)))
    if not nolog: f.close() 
 
#%%  API function

def fatal(error):
    if not verbose: print(error.encode('utf-8', 'replace'))
    log(error)
    sys.exit(2)

def api(host, com = "get", args = None ):
    """
    radarr: get & {} | lookup & {id:} | post & {**data}
    tmdb: get & com & {id}
    """
    if host == "Radarr":
        url = radarr['url']
        key = {"apikey": radarr['api_key']}
        if com == "lookup":
            url += "/lookup/tmdb"
            key.update({"tmdbid" : int(args)})
        elif com == "post":
            url += "?apikey=" + radarr['api_key']
            response = requests.post(url, data = json.dumps(args))
            return response.status_code
    elif host == "TMDB":
        if   com == "mov": payload = "movie/", str(args), ""
        elif com == "col": payload = "collection/", str(args), ""
        elif com == "per": payload = "person/", str(args), ""
        elif com == "cred": payload = "person/", str(args), "/movie_credits"
        url = "https://api.themoviedb.org/3/{0}{1}{2}".format(*payload)
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
        elif code in (502,503): fatal("\n" + words.offline.format(host,i)) # FATAL
        else:                                               # UNKNOWN
            if tries < 5 :                                     ## RETRY
                tries += 1
                print(words.api_misc.encode('utf-8', 'replace').format(host,code,tries))
                time.sleep(5) 
            else: fatal("\n" + words.api_retry.format(host,i))           ## LIMITED
                
#%% Item Check Iterator Function

def item_check(part, white_name, json, crew=None):
    global cache, fails
    if part in tmdb_ids:
        skip.append(part) 
        log(words.in_data.format(*mov_info(tmdb_ids.index(part))))
    elif stage == 3 and part in memory:
        pass
    else:
        lookup_json = api("Radarr", com = "lookup", args = part)
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
            if stage == 3: name = json['name'] + " - " + crew
            else: name = json['name']
            payload = words.found.format(name, white_name, post_data['tmdbId'], white_cid, post_data['title'], post_data['year'])
            if stage == 2: found_col.append(payload)
            elif stage == 3: 
                found_per.append(payload)
                memory.append(part)
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
                        print("\n" + words.retry_err.encode('utf-8', 'replace') + "\n") 

#%% Collection Checker Function

def collection_check(col_id):
    col_json = api("TMDB", com = "col", args = col_id)
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
    if stage == 1: payload = two_dex, "> ", col_json['name'], col_id, number
    elif stage == 2: payload = str(i + 1) + ":", white_dex, col_json['name'], col_id, number
    log(words.other.format(*payload) + "\n")
    for part in parts:  item_check(part, white_name, col_json)
    if any([full, all([not full, data[i]["tmdbId"] not in skip])]): log("")
    
#%% Person Monitor Function
    
def person_check(per_id):
    per_gen_json = api("TMDB", com = "per", args = per_id)
    per_cred_json = api("TMDB", com = "cred", args = per_id)
    
    if len(per_gen_json['name']) < 60: top_p = 60
    else: top_p = len(per_gen_json['name']) + 5
    
    payload = str(i+1) + ":", white_dex, per_gen_json['name'], per_id, str([hold.title() for hold in people[per_id]['monitor']]).strip("[]").replace("'","").replace("\"","")
    log(words.person.format(*payload))
    
    if 'cast' in people[per_id]['monitor']:
        log("")
        log(words.cast.format(len(per_cred_json['cast'])))
        log("")
        for k in range(len(per_cred_json['cast'])): 
            white_name = " "*(top_p - len(per_gen_json['name'] + " - Cast"))
            item_check(per_cred_json["cast"][k]['id'], white_name, per_gen_json, "Cast")
    if any(['directing' in people[per_id]['monitor'],
            'production' in people[per_id]['monitor'],
            'writing' in people[per_id]['monitor']]):
        log("")
        log(words.crew.format(len(per_cred_json['crew'])))
        log("")
    for k in range(len(per_cred_json['crew'])):
        if any(['directing' in people[per_id]['monitor'] \
                 and per_cred_json['crew'][k]['department'] == 'Directing',
                 'production' in people[per_id]['monitor'] \
                 and per_cred_json['crew'][k]['department'] == 'Production',
                 'writing' in people[per_id]['monitor'] \
                 and per_cred_json['crew'][k]['department'] == 'Writing']):
            white_name = " "*(top_p - len(per_gen_json['name'] + " - " + per_cred_json['crew'][k]['department']))    
            item_check(per_cred_json['crew'][k]['id'], white_name, per_gen_json, per_cred_json['crew'][k]['department'])
        
#%% Opening
        
if not nolog: f = open(os.path.join('logs',"log_{}.txt".format(start_time)),'w+')

log(words.hello)
data = api("Radarr")

if start > len(data): fatal(words.start_err.format(start, int(len(data))))

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]
title_top = max([len(data[i]["title"]) for i in range(len(data))]) + 2
rad_top = len(str(data[-1]['id'])) + 1

found_col, found_per, col_art, col_ids, memory = [],[],[],[],[]
fails = 0

if cache: log(words.cache)
if art: log(words.art)
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
    numbers = len(data) - start, len(col_ids), len(people)
    log(words.full.format(*numbers))
else:
    skip = s[0].strip('[]\n').split(', ')
    skip = [int(skip[i]) for i in range(len(skip))]
    numbers = len(data) - len(skip), len(col_ids), len(people)
    log(words.update.format(*numbers))

if ignore_wanted: log(words.wanted)

atexit.register(datadump)

two_dex = " "*len(str(len(data)))

#%%  Database Search
stage = 1

if numbers[0] != 0: log(words.run_mov_mon.format(*numbers) + ":" + "\n")
printtime= True
for i in range(start,len(data)):
    white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
    payload = mov_info(i)
    logtext = "{0}:{1}".format(i + 1, white_dex) + words.radarr.format(*payload) + words.mov_info.format(*payload)
    
    if any([not all([ignore_wanted, not data[i]['hasFile']]), not ignore_wanted]) \
    and data[i]["tmdbId"] not in skip:
        mov_json = api("TMDB", com = "mov", args = data[i]["tmdbId"])
        if mov_json == 404: log(logtext + "Error - Not Found")
        elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
            col_id = mov_json['belongs_to_collection']['id']
            if col_id not in col_ids: col_ids.append(col_id)
            log(logtext + "In Collection")
            collection_check(col_id)            
        else: log(logtext + "Not in Collection") # if mov_json == 404
    elif full: log(logtext + "Skipping") # if id in list
log("")

#%% Collection Monitor
stage = 2
if not full:
    printtime = False
    log(words.run_col_mon.format(*numbers) + ":" + "\n")
    printtime= True
    for i, col_id in enumerate(col_ids):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        collection_check(col_id)
        log("")

#%% Person Monitor
stage = 3
if len(people) != 0:
    printtime = False
    log(words.run_per_mon.format(*numbers) + ":" + "\n")
    printtime= True  
    for i, per_id in enumerate(people.keys()):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        person_check(per_id)
        log("")
