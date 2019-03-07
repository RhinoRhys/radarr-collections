#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests, json, datetime, os, sys, getopt, time, atexit, configparser

start_time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")

def get_dir(input_path):
    path = list(os.path.split(input_path))
    if path[0] in ["~","."]: path[0] = os.getcwd()
    return os.path.join(*path)

for var in ['quiet', 'ignore_wanted', 'full', 'peeps', 'art', 'nolog', 'cache', 'single']:
    exec("{} = False".format(var))
start = 0 # 0

config_path = get_dir(sys.argv[1])

if not os.path.isfile(os.path.join(config_path, "rcm.conf")):
    print(u'Error - No configuration file found - Exiting')
    sys.exit(2)
    
words = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(), allow_no_value=True)
words.read(os.path.join(config_path,u'words.conf'))
config = configparser.ConfigParser(allow_no_value=True)
config.read(os.path.join(config_path,u'rcm.conf'))
people = configparser.ConfigParser(allow_no_value=True)
people.read(os.path.join(config_path,u'people.conf'))
 
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[2:],"hqdfas:ncpt:",["help","quiet","down","full","art","start=","nolog","cache","people","tmdbid="])
    except getopt.GetoptError:
        print(u'Error in options\n')
        print(words[u'help'][u'text'])
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(words[u'help'][u'text'])
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

if config[u'results'][u'path'] in ["","0"]: config[u'results'][u'path'] = u"./"
output_path = get_dir(config[u'results'][u'path'])

blacklist = config[u'blacklist'][u'blacklist'].split(",")
if blacklist[0] != "": blacklist = [int(item) for item in blacklist]

if u'true' in config[u'radarr'][u'ssl'].lower(): http = u"https://"
else: http = u"http://"
if all([u'true' in config[u'radarr'][u'reverse_proxy'].lower(), u'true' in config[u'radarr'][u'docker'].lower()]): http + u"{0}:{1}{2}/api/movie".format(config[u'radarr'][u'host'].strip(), config[u'radarr'][u'port'].strip(), config[u'radarr'][u'base_url'].strip())
elif 'true' in config[u'radarr'][u'reverse_proxy'].lower(): radarr_url = http + u"{0}{1}/api/movie".format(config[u'radarr'][u'host'].strip(), config[u'radarr'][u'base_url'].strip())
else: radarr_url = http + u"{0}:{1}/api/movie".format(config[u'radarr'][u'host'].strip(), config[u'radarr'][u'port'].strip())

if start != 0: full = True
printtime = False

def fatal(error):
    if quiet: print(error)
    log(error)
    sys.exit(2)
    
#%% Output files

if not os.path.exists(os.path.join(output_path,"logs")): os.mkdir(os.path.join(output_path,"logs"))
if not os.path.exists(os.path.join(output_path,"output")): os.mkdir(os.path.join(output_path,"output"))

def log(text):
    if printtime and text not in ("", "\n"): pay = datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S] ") + text
    else: pay = text
    if not quiet: print(pay)
    if sys.version_info[0] == 2 and not nolog: f.write(pay.encode("utf-8", "replace") + "\n")
    elif sys.version_info[0] == 3 and not nolog: f.write(pay + u"\n")

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
            log(words[u'text'][u'auto_cache'].format(start_time) + u"\n")
        found_col.sort()
        found_per.sort()
        g = open(os.path.join(output_path,'output','found_{0}.txt'.format(start_time)),'w+')
        payload = len(found_col) + len(found_per), len(found_col), len(found_per)
        if sys.version_info[0] == 2:    
            g.write(words[u'text'][u'found_open'].format(*payload) + "\n\n")
            if len(found_col) != 0: 
                g.write(words[u'text'][u'found_start'].format(*payload) + "\n\n")
                for item in found_col: g.write(item.encode("utf-8", "replace") + "\n")
                g.write("\n")
            if len(found_per) != 0: g.write(words[u'text'][u'found_middle'].format(*payload) + "\n\n")
            for item in found_per: g.write(item.encode("utf-8", "replace") + "\n")
        elif sys.version_info[0] == 3:
            g.write(words[u'text'][u'found_open'].format(*payload) + u"\n\n")
            if len(found_col) != 0: 
                g.write(words[u'text'][u'found_start'].format(*payload) + u"\n\n")
                for item in found_col: g.write(item + u"\n")
                g.write(u"\n")
            if len(found_per) != 0: g.write(words[u'text'][u'found_middle'].format(*payload) +  u"\n\n")
            for item in found_per: g.write(item +  u"\n")
        g.close()
        
    if art and not peeps:
        col_art.sort()
        g = open(os.path.join(output_path,'output','art_{0}.txt'.format(start_time)), 'w+')
        if sys.version_info[0] == 2: 
            for line in col_art: g.write(line.encode("utf-8", "replace") +  "\n")
        elif sys.version_info[0] == 3:
            for line in col_art: g.write(line +  u"\n")
        g.close()
    
    col_ids.sort()
    g = open(os.path.join(config_path,u'memory.dat'),'w+')
    if sys.version_info[0] == 2: g.write(str(tmdb_ids) + "\n")
    elif sys.version_info[0] == 3: g.write(str(tmdb_ids) +  u"\n")
    g.write(str(col_ids))
    g.close()
    
    printtime = False
    log(words[u'text'][u'bye'].format(len(found_col) + len(found_per)))
    if not nolog: f.close() 
 
#%%  API Function

def api(host, com = "get", args = None ):
    """
    radarr: get & {} | lookup & {id:} | post & {**data}
    tmdb: get & com & {id}
    """
    if host == "Radarr":
        url = radarr_url
        key = {"apikey": config[u'radarr'][u'api_key']}
        if com == "lookup":
            url += "/lookup/tmdb"
            key.update({"tmdbid" : int(args)})
        elif com == "post":
            url += u"?apikey=" + config[u'radarr'][u'api_key']
            response = requests.post(url, data = args)
            return response.status_code
    elif host == "TMDB":
        if   com == "mov": payload = "movie/", str(args), ""
        elif com == "col": payload = "collection/", str(args), ""
        elif com == "per": payload = "person/", str(args), ""
        elif com == "cred": payload = "person/", str(args), "/movie_credits"
        url = "https://api.themoviedb.org/3/{0}{1}{2}".format(*payload)
        key = {"api_key": config[u'tmdb'][u'api_key'].strip(" ") }
    
    good = False
    tries = 0
    while not good:    
        response = requests.get(url, params = key )
        response.content.decode("utf-8")
        code = response.status_code 
        
        if code == 200:                                     # GOOD
            good = True
            return response.json()
        elif code == 401: fatal(words[u'text'][u'api_auth'].format(host) +  u"\n")       # FATAL
        elif code == 404:                                   # MINOR
            good = True
            return code
        elif code == 429:                                   # RETRY
            wait = int(response.headers["Retry-After"]) + 1
            if not quiet: print(words[u'text'][u'api_wait'].format(wait))
            time.sleep(wait)
        elif code in (502,503): fatal( u"\n" + words[u'text'][u'offline'].format(host,i)) # FATAL
        else:                                               # UNKNOWN
            if tries < 5 :                                     ## RETRY
                tries += 1
                print(words[u'text'][u'api_misc'].format(host, code, tries))
                time.sleep(5 + tries) 
            else: fatal( u"\n" + words[u'text'][u'api_retry'].format(host,i))           ## LIMITED
                
#%% Movie in Collection Check Function

def tmdb_check(tmdbId):
    mov_json = api("TMDB", com = "mov", args = tmdbId)
    if mov_json == 404: log(logtext + words[u'text'][u'col_err'])
    elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
        col_id = mov_json['belongs_to_collection'][u'id']
        if col_id not in col_ids: col_ids.append(col_id)
        log(logtext + words[u'text'][u'in_col'])
        collection_check(col_id, tmdbId)
    else: log(logtext + words[u'text'][u'no_col'])          

#%% Collection Parts Check Function

def collection_check(col_id, tmdbId = None):
    if single: log("")
    col_json = api("TMDB", com = "col", args = col_id)
    if len(col_json['name']) < int(config[u'results'][u'column']): top_c = int(config[u'results'][u'column'])
    else: top_c = len(col_json['name']) + 5
    white_name = " "*(top_c - len(col_json['name'])) 
    if art: col_art.append(words[u'text'][u'col_art'].format(col_json['name'], white_name, col_json['poster_path']))
    parts = [col_json['parts'][j]['id'] for j in range(len(col_json['parts']))]
    number = len(parts)
    if stage == 1:
        try: parts.remove(int(tmdbId))
        except: pass
        log("")
    if stage in [0, 1]: payload = ">", " "*(1 + len(str(len(data)))), col_json['name'], col_id, number
    elif stage == 2: payload = str(i + 1) + ":", white_dex, col_json['name'], col_id, number
    if stage == 1: input_id = i
    elif stage in [0, 2]:
        source = []
        for id_check in parts:
            if id_check in tmdb_ids: source.append(id_check)
        if len(source) > 0: input_id = source[0]
        else: input_id = int(config[u'adding'][u'profile'])
    log(words[u'text'][u'other'].format(*payload) +  u"\n")
    for id_check in parts:  database_check(id_check, white_name, col_json, input_id)
    if any([full, all([not full, tmdbId not in skip])]): log("")
    
#%% Movie in Database Check Function

def database_check(id_check, white_name, json_in, input_data):
    global cache, fails
    if id_check in tmdb_ids:
        skip.append(id_check) 
        log(words[u'text'][u'in_data'].format(*mov_info(tmdb_ids.index(id_check))))
    else:
        lookup_json = api("Radarr", com = "lookup", args = id_check)
        w_rad, w_id, w_title = whitespace(id_check, lookup_json['title'], lookup_json['year'], "")
        payload = " "*11, w_rad, id_check, w_id, lookup_json['title'], lookup_json['year'], w_title
        if id_check in blacklist: log(words[u'text'][u'ignore'].format(*payload))
        elif lookup_json['ratings'][u'value'] < float(config[u'blacklist'][u'min_rating']) \
        or lookup_json['ratings'][u'votes'] < int(config[u'blacklist'][u'min_votes']): log(words[u'text'][u'rated'].format(*payload))
        else:
            log(words[u'text'][u'not_data'].format(*payload))
            if stage == 1: index = input_data
            elif stage in [0, 2]: index = tmdb_ids.index(input_data) 
            elif stage == 3: index = tmdb_ids.index(int(config[u'adding'][u'profile']))
            if 'true' in config[u'radarr'][u'docker'].lower(): path = "/".join(data[index]['path'].split("/")[:-1])
            else: path = os.path.split(data[index]['path'])[0]
            post_data = {u"qualityProfileId" : int(data[index][u'qualityProfileId']),
                         u"rootFolderPath": path,
                         u"monitored" : config[u'adding'][u'monitored'],
                         u"addOptions" : {u"searchForMovie" : config[u'adding'][u'autosearch']}}
            for dictkey in [u"tmdbId",u"title",u"titleSlug",u"images",u"year"]: post_data.update({dictkey : lookup_json[dictkey]})
            white_cid = " "*(15 - len(str(post_data["tmdbId"])))
            if stage == 3: name = json_in['name'] + " - " + input_data
            else: name = json_in['name']
            payload = words[u'text'][u'found'].format(name, white_name, post_data[u'tmdbId'], white_cid, post_data['title'], post_data['year'])
            if stage in [0, 1, 2]: found_col.append(payload)
            elif stage == 3: found_per.append(payload)
            if not cache:
                if sys.version_info[0] == 2: post_datar = json.dumps(post_data)
                elif sys.version_info[0] == 3: post_datar = str(post_data).replace("'","\"")
                post = api("Radarr", com = "post", args = post_datar)
                white_yn = " "*(rad_top + 10)
                if post == 201: 
                    log(words[u'text'][u'add_true'].format(white_yn))
                    tmdb_ids.append(post_data['tmdbId'])
                else:
                    log(words[u'text'][u'add_fail'].format(white_yn, post))
                    fails += 1
                    if fails == 10:
                        cache = True
                        print( u"\n" + words[u'text'][u'retry_err'] +  u"\n") 

#%% Person Credits Check Function

def person_check(person):
    per_id = int(people[person]['id'])
    per_gen_json = api("TMDB", com = "per", args = per_id)
    per_cred_json = api("TMDB", com = "cred", args = per_id)
    
    if len(per_gen_json['name']) < int(config[u'results'][u'column']): top_p = int(config[u'results'][u'column'])
    else: top_p = len(per_gen_json['name']) + 5
    search = [x.strip(' ').title() for x in people[person]['monitor'].split(",")]
    payload = str(i+1) + ":", white_dex, per_gen_json['name'], per_id, ", ".join(search)
    log(words[u'text'][u'person'].format(*payload))
    
    if 'cast' in people[person]['monitor'].lower():
        log("")
        log(words[u'text'][u'cast'].format(len(per_cred_json['cast'])))
        log("")
        for k in range(len(per_cred_json['cast'])): 
            white_name = " "*(top_p - len(per_gen_json['name'] + " - Cast"))
            database_check(per_cred_json["cast"][k]['id'], white_name, per_gen_json, "Cast")
    roles = {}
    scan_hold = []
    for k in range(len(per_cred_json['crew'])):
        if per_cred_json['crew'][k]['department'].title() in search \
        and per_cred_json['crew'][k]['id'] not in scan_hold:
            if per_cred_json['crew'][k]['department'] not in roles.keys():
                roles.update({per_cred_json['crew'][k]['department'] : []})
            roles[per_cred_json['crew'][k]['department']].append([per_cred_json['crew'][k]['id'],per_cred_json['crew'][k]['job']])
            scan_hold.append(per_cred_json['crew'][k]['id'])
    for role in roles.keys(): 
        log("")
        log(words[u'text'][u'crew'].format(role, len(roles[role])))
        log("")        
        for tmdb_Id, job in roles[role]:
            white_name = " "*(top_p - len(per_gen_json['name'] + " - " + role + " - " + job))    
            database_check(tmdb_Id, white_name, per_gen_json, role + " - " + job)
    
#%% Opening
        
if not nolog: f = open(os.path.join(output_path,'logs',"log_{}.txt".format(start_time)),'w+')

log(words[u'text'][u'hello'] +  u"\n")
data = api("Radarr")

if start > len(data): fatal(words[u'text'][u'start_err'].format(start, int(len(data))))

tmdb_ids = [data[i]["tmdbId"] for i in range(len(data))]

if len(people.sections()) != 0 and int(config[u'adding'][u'profile']) not in tmdb_ids: fatal(words[u'text'][u'template_err'])

title_top = max([len(data[i]["title"]) for i in range(len(data))]) + 2
rad_top = len(str(data[-1]['id'])) + 1

found_col, found_per, col_art, col_ids = [],[],[],[]
fails = 0

if cache: log(words[u'text'][u'cache'] +  u"\n")
if art and not peeps: log(words[u'text'][u'art'] +  u"\n")
if start != 0 and not peeps and not single: log(words[u'text'][u'start'].format(start) +  u"\n")
if single and peeps: log(words[u'text'][u'tp_err'] +  u"\n")

try: 
    s = open(os.path.join(config_path,u'memory.dat'), "r+")
    s = s.readlines()
    col_ids = s[1].strip('[]\n').split(', ')
    col_ids = [int(col_ids[i]) for i in range(len(col_ids))]
except: 
    full = True

if full:
    skip = []
    numbers = len(data) - start, len(col_ids), len(people.sections())
    if not peeps and not single: log(words[u'text'][u'full'].format(*numbers) +  u"\n")
else:
    skip = s[0].strip('[]\n').split(', ')
    skip = [int(skip[i]) for i in range(len(skip))]
    numbers = max(0, len(data) - len(skip)), len(col_ids), len(people.sections())
    if not peeps and not single: log(words[u'text'][u'update'].format(*numbers))

if peeps and not single: log(words[u'text'][u'peeps'] +  u"\n")
if ignore_wanted and not peeps and not single: log(words[u'text'][u'wanted'] +  u"\n")

atexit.register(datadump)

#%% Single Scan Mode
stage = 0
if not peeps and single:
    printtime = True
    lookup_json = api("Radarr", com = "lookup", args = single_id)
    
    w_rad, w_id, w_title = whitespace(single_id, lookup_json['title'], lookup_json['year'], "")
    payload = "", " "*(len(str(len(data))) + 13 + len(w_rad) - len(words[u'text'][u'single'])), single_id, w_id, lookup_json['title'], lookup_json['year'], w_title
    logtext = words[u'text'][u'single'] + words[u'text'][u'mov_info'].format(*payload)
    tmdb_check(single_id)
    log(u"")
    sys.exit()

#%%  Database Search Loop
stage = 1
if not peeps and not single:    
    if numbers[0] != 0: log(words[u'text'][u'run_mov_mon'].format(*numbers) + u":" + u"\n")
    printtime= True
    for i in range(start,len(data)):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        payload = mov_info(i)
        logtext = "{0}:{1}".format(i + 1, white_dex) + words[u'text'][u'radarr'].format(*payload) + words[u'text'][u'mov_info'].format(*payload)
        
        if any([not all([ignore_wanted, not data[i]['hasFile']]), not ignore_wanted]) \
        and data[i]["tmdbId"] not in skip:
            tmdb_check(data[i]["tmdbId"])
        elif full: log(logtext + words[u'text'][u'skip']) # if id in list
    log("")

#%% Collection Monitor Loop
stage = 2
if not full and not peeps and not single:
    printtime = False
    log(words[u'text'][u'run_col_mon'].format(*numbers) + u":" +  u"\n")
    printtime= True
    for i, col_id in enumerate(col_ids):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        collection_check(col_id)

#%% Person Monitor Loop
stage = 3
if len(people.sections()) != 0 and not single:
    printtime = False
    log(words[u'text'][u'run_per_mon'].format(*numbers) + u":" +  u"\n")
    printtime= True  
    for i, person in enumerate(people.sections()):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(i + 1)))
        person_check(person)
        log("")
