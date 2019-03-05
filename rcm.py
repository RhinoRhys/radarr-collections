#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time, atexit
from config import radarr, force_ignore, people
import config
import words

for var in ['quiet', 'ignore_wanted', 'full', 'peeps', 'art', 'nolog', 'cache', 'single']:
    exec("{} = False".format(var))
start = 0 # 0

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hqdfas:ncpt:",["help","quiet","down","full","art","start=","nolog","cache","people","tmdbid="])
    except getopt.GetoptError:
        print('Error in options\n\n')
        for line in words.helptext: print(line)
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            for line in words.helptext: print(line)
            sys.exit()
        elif opt in ("-q", "--quiet"): quiet = True
        elif opt in ("-d", "--down"): ignore_wanted = True
        elif opt in ("-f", "--full"): full = True
        elif opt in ("-p", "--people"): peeps = True
        elif opt in ("-a", "--art"): art = True
        elif opt in ("-s", "--start"): start = int(arg)
        elif opt in ("-n", "--nolog"): nolog = True
        elif opt in ("-c", "--cache"): cache = True
        elif opt in ("-t", "--tmdbid"):
            single = True
            single_id = int(arg)

start_time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S") 

if radarr['base_url'] == "off": radarr['url'] = "http://{0}:{1}/api/movie".format(radarr['host'].strip(), radarr['port'].strip())
else: radarr['url'] = "http://{0}{1}/api/movie".format(radarr['host'].strip(), radarr['base_url'].strip())

if start != 0: full = True
printtime = False

def fatal(error):
    if quiet: print(error.encode('utf-8', 'replace'))
    log(error)
    sys.exit(2)
    
#%% Output files

if not os.path.exists("logs"): os.mkdir("logs")
if not os.path.exists("output"): os.mkdir("output")
    
def log(text):
    if printtime and text not in ("", "\n"): pay = datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S] ") + text.encode('utf-8', 'replace')
    else: pay = text.encode('utf-8', 'replace')
    if not quiet: print(pay)
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
        g.write(words.found_open.format(*payload) + "\n\n")
        if len(found_col) != 0: 
            g.write(words.found_start.format(*payload) + "\n\n")
            for item in found_col: g.write(item.encode("utf-8", "replace") + '\n')
            g.write("\n")
        if len(found_per) != 0: g.write(words.found_middle.format(*payload) + "\n\n")
        for item in found_per: g.write(item.encode("utf-8", "replace") + '\n')
        g.close()
        
    if art and not peeps:
        col_art.sort()
        g = open(os.path.join('output','art_{0}.txt'.format(start_time)), 'w+')
        for line in col_art: g.write(line.encode("utf-8", "replace") + '\n')
        g.close()
    
    col_ids.sort()
    g = open('memory.dat','w+')
    g.write(str(tmdb_ids) + "\n")
    g.write(str(col_ids))
    g.close()
    
    printtime = False
    log(words.bye.format(len(found_col) + len(found_per)))
    if not nolog: f.close() 
 
#%%  API Function

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
        key = {"api_key": config.tmdbkey }
    
    good = False
    tries = 0
    while not good:    
        response = requests.get(url, params = key )
        response.content.decode("utf-8")
        code = response.status_code 
        
        if code == 200:                                     # GOOD
            good = True
            return response.json()
        elif code == 401: fatal(words.api_auth.format(host) + "\n")       # FATAL
        elif code == 404:                                   # MINOR
            good = True
            return code
        elif code == 429:                                   # RETRY
            wait = int(response.headers["Retry-After"]) + 1
            if not quiet: print(words.api_wait.encode('utf-8', 'replace').format(wait))
            time.sleep(wait)
        elif code in (502,503): fatal("\n" + words.offline.format(host,i)) # FATAL
        else:                                               # UNKNOWN
            if tries < 5 :                                     ## RETRY
                tries += 1
                print(words.api_misc.encode('utf-8', 'replace').format(host,code,tries))
                time.sleep(5 + tries) 
            else: fatal("\n" + words.api_retry.format(host,i))           ## LIMITED
                
#%% Movie in Collection Check Function

def tmdb_check(tmdbId):
    mov_json = api("TMDB", com = "mov", args = tmdbId)
    if mov_json == 404: log(logtext + words.col_err)
    elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
        col_id = mov_json['belongs_to_collection']['id']
        if col_id not in col_ids: col_ids.append(col_id)
        log(logtext + words.in_col)
        collection_check(col_id, tmdbId)
    else: log(logtext + words.no_col)          

#%% Collection Parts Check Function

def collection_check(col_id, tmdbId = None):
    if single: log("")
    col_json = api("TMDB", com = "col", args = col_id)
    if len(col_json['name']) < white_top: top_c = white_top
    else: top_c = len(col_json['name']) + 5
    white_name = " "*(top_c - len(col_json['name'])) 
    if art: col_art.append(words.col_art.format(col_json['name'], white_name, col_json['poster_path']))
    parts = [col_json['parts'][j]['id'] for j in range(len(col_json['parts']))]
    number = len(parts)
    if tmdbId != None and any([full, all([not full, tmdbId not in skip])]):
        try: parts.remove(int(tmdbId))
        except: pass
        log("")
    if stage == 1: payload = " "*(len(str(len(data)))), "> ", col_json['name'], col_id, number
    elif stage == 2: payload = str(i + 1) + ":", white_dex, col_json['name'], col_id, number
    log(words.other.format(*payload) + "\n")
    for part in parts:  database_check(part, white_name, col_json)
    if any([full, all([not full, tmdbId not in skip])]): log("")
    
#%% Movie in Database Check Function

def database_check(part, white_name, json, crew=None):
    global cache, fails
    if part in tmdb_ids:
        skip.append(part) 
        log(words.in_data.format(*mov_info(tmdb_ids.index(part))))
    else:
        lookup_json = api("Radarr", com = "lookup", args = part)
        w_rad, w_id, w_title = whitespace(part, lookup_json['title'], lookup_json['year'], "")
        payload = "", w_rad, part, w_id, lookup_json['title'], lookup_json['year'], w_title
        if part in force_ignore: log(words.ignore.format(*payload))
        elif lookup_json['ratings']['value'] < config.min_rating \
        or lookup_json['ratings']['votes'] < config.min_votes: log(words.rated.format(*payload))
        else:
            log(words.not_data.format(*payload))
            if stage == 3: index = tmdb_ids.index(config.profile)
            else: index = i
            post_data = {"qualityProfileId" : int(data[index]['qualityProfileId']),
                         "rootFolderPath": os.path.split(data[index]['path'])[0].encode(sys.getfilesystemencoding()),
                         "monitored" : config.monitored,
                         "addOptions" : {"searchForMovie" : config.autosearch}}
            for dictkey in ["tmdbId","title","titleSlug","images","year"]: post_data.update({dictkey : lookup_json[dictkey]})
            white_cid = " "*(15 - len(str(post_data["tmdbId"])))
            if stage == 3: name = json['name'] + " - " + crew
            else: name = json['name']
            payload = words.found.format(name, white_name, post_data['tmdbId'], white_cid, post_data['title'], post_data['year'])
            if stage == 2: found_col.append(payload)
            elif stage == 3: found_per.append(payload)
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

#%% Person Credits Check Function

def person_check(per_id):
    per_gen_json = api("TMDB", com = "per", args = per_id)
    per_cred_json = api("TMDB", com = "cred", args = per_id)
    
    if len(per_gen_json['name']) < white_top: top_p = white_top
    else: top_p = len(per_gen_json['name']) + 5
    
    payload = str(i+1) + ":", white_dex, per_gen_json['name'], per_id, str([hold.title() for hold in people[per_id]['monitor']]).strip("[]").replace("'","").replace("\"","")
    log(words.person.format(*payload))
    
    if 'cast' in people[per_id]['monitor'] or 'Cast' in people[per_id]['monitor']:
        log("")
        log(words.cast.format(len(per_cred_json['cast'])))
        log("")
        for k in range(len(per_cred_json['cast'])): 
            white_name = " "*(top_p - len(per_gen_json['name'] + " - Cast"))
            database_check(per_cred_json["cast"][k]['id'], white_name, per_gen_json, "Cast")
    roles = {}
    scan_hold = []
    for k in range(len(per_cred_json['crew'])):
        if per_cred_json['crew'][k]['department'] in people[per_id]['monitor'] \
        and per_cred_json['crew'][k]['id'] not in scan_hold:
            if per_cred_json['crew'][k]['department'] not in roles.keys():
                roles.update({per_cred_json['crew'][k]['department'] : []})
            roles[per_cred_json['crew'][k]['department']].append([per_cred_json['crew'][k]['id'],per_cred_json['crew'][k]['job']])
            scan_hold.append(per_cred_json['crew'][k]['id'])
    for role in roles.keys(): 
        log("")
        log(words.crew.format(role, len(roles[role])))
        log("")        
        for tmdb_Id, job in roles[role]:
            white_name = " "*(top_p - len(per_gen_json['name'] + " - " + role + " - " + job))    
            database_check(tmdb_Id, white_name, per_gen_json, role + " - " + job)
    
#%% Opening
        
if not nolog: f = open(os.path.join('logs',"log_{}.txt".format(start_time)),'w+')

log(words.hello + "\n")
data = api("Radarr")

if start > len(data): fatal(words.start_err.format(start, int(len(data))))

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]

if len(people) != 0 and config.profile not in tmdb_ids: fatal(words.template_err)

title_top = max([len(data[i]["title"]) for i in range(len(data))]) + 2
rad_top = len(str(data[-1]['id'])) + 1
white_top = 60 # Whitespace Maximum for output

found_col, found_per, col_art, col_ids = [],[],[],[]
fails = 0

if cache: log(words.cache + "\n")
if art and not peeps: log(words.art + "\n")
if start != 0 and not peeps and not single: log(words.start.format(start) + "\n")
if single and peeps: log(words.tp_err + "\n")

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
    if not peeps and not single: log(words.full.format(*numbers) + "\n")
else:
    skip = s[0].strip('[]\n').split(', ')
    skip = [int(skip[i]) for i in range(len(skip))]
    numbers = max(0, len(data) - len(skip)), len(col_ids), len(people)
    if not peeps and not single: log(words.update.format(*numbers))

if peeps and not single: log(words.peeps + "\n")
if ignore_wanted and not peeps and not single: log(words.wanted + "\n")

atexit.register(datadump)

#%% Single Scan Mode

stage = 1
if not peeps and single:
    printtime = True
    lookup_json = api("Radarr", com = "lookup", args = single_id)
    
    w_rad, w_id, w_title = whitespace(single_id, lookup_json['title'], lookup_json['year'], "")
    payload = "", " "*(len(str(len(data))) + 13 + len(w_rad) - len(words.single)), single_id, w_id, lookup_json['title'], lookup_json['year'], w_title
    logtext = words.single + words.mov_info.format(*payload)
    tmdb_check(single_id)
    log("")
    sys.exit()

#%%  Database Search Loop

if not peeps and not single:    
    if numbers[0] != 0: log(words.run_mov_mon.format(*numbers) + ":" + "\n")
    printtime= True
    for i in range(start,len(data)):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        payload = mov_info(i)
        logtext = "{0}:{1}".format(i + 1, white_dex) + words.radarr.format(*payload) + words.mov_info.format(*payload)
        
        if any([not all([ignore_wanted, not data[i]['hasFile']]), not ignore_wanted]) \
        and data[i]["tmdbId"] not in skip:
            tmdb_check(data[i]["tmdbId"])
        elif full: log(logtext + words.skip) # if id in list
    log("")

#%% Collection Monitor Loop
stage = 2
if not full and not peeps and not single:
    printtime = False
    log(words.run_col_mon.format(*numbers) + ":" + "\n")
    printtime= True
    for i, col_id in enumerate(col_ids):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        collection_check(col_id)

#%% Person Monitor Loop
stage = 3
if len(people) != 0 and not single:
    printtime = False
    log(words.run_per_mon.format(*numbers) + ":" + "\n")
    printtime= True  
    for i, per_id in enumerate(people.keys()):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        person_check(per_id)
        log("")
