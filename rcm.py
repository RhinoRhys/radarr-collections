#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, datetime, sys, getopt, time, atexit, configparser
from pathlib import Path, PurePosixPath 

for var in ['quiet', 'full', 'peeps', 'nolog', 'cache', 'single', 'quick', 'printtime', 'first']:
    exec("{} = False".format(var))

check_num = 0 # 0

def get_dir(input_path):
    if not Path(input_path).is_absolute(): return Path.cwd() / input_path
    else: return Path(input_path)

def fatal(error):
    global printtime
    printtime = False
    if quiet: print(error)
    log(error + u"\n")
    sys.exit(2)

def nologfatal(error):
    global nolog, quiet
    quiet = False
    nolog = True
    fatal(error)

# Output files

def log(text):
    if printtime and text != "": pay = datetime.datetime.now().strftime("[%y-%m-%d %H:%M:%S] ") + text
    else: pay = text
    if not quiet: 
        try: print(pay)
        except: print(pay.encode("utf-8", errors = 'replace'))
    if not nolog: 
        f = open(Path.joinpath(output_path,'logs',"log_{}.txt".format(start_time)),'a+')
        try: f.write(pay + u"\n")
        except: pass
        f.close()

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
    global printtime, added
    if len(found_col)+len(found_per) != 0 and cache:
        if fails == 10: 
            printtime = False
            log(words[u'text'][u'auto_cache'].format(start_time) + u"\n")
        found_col.sort()
        found_per.sort()
        g = open(Path.joinpath(output_path,'output','found_{0}.txt'.format(start_time)),'w+')
        g.write(words[u'text'][u'name'] + u"\n\n")
        g.write(words[u'text'][u'found_total'].format(len(found_col) + len(found_per)) + u"\n\n")
        if len(found_col) != 0: 
            g.write(words[u'text'][u'found_cols'].format(len(found_col)) + u"\n\n")
            for item in found_col: g.write(str(item.encode('utf-8')) + u'\n')
            g.write(u"\n")
        if len(found_per) != 0: 
            g.write(words[u'text'][u'found_peep'].format(len(found_per)) +  u"\n\n")
            for item in found_per: g.write(str(item.encode('utf-8')) +  "\n")
            g.write(u"\n")
        g.write(words[u'text'][u'found_black'] + u"\n\n")
        g.write(u"blacklist = {}".format(str(found_black).strip("[]")))
        g.close()
               
    if check_num != 0:    
        col_ids.sort()
        [tmdb_ids.remove(mov_id) for mov_id in wanted]
        [tmdb_ids.remove(mov_id) for mov_id in list(set(unmon)-set(wanted))]
        g = open(Path.joinpath(config_path,u'memory.dat'),'w+')
        for text in (str(tmdb_ids),str(col_ids),str(wanted),str(unmon)): g.write(text +  u"\n")
        g.close()
    
    printtime = False
    log(words[u'text'][u'found_total'].format(len(found_col) + len(found_per)) + u"\n")
    if added > 0: log(words[u'text'][u'added_total'].format(added) + u"\n")
    log(u"\n" + words[u'text'][u'bye']) 
 
#  API Function

def api(host, com = "get", args = None ):
    global printtime
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
            response = requests.post(url, json = args, headers={'Content-Type': 'application/json; charset=utf-8','x-api-key' : config[u'radarr'][u'api_key']})
            return response.status_code
    elif host == "TMDB":
        key = {"api_key": config[u'tmdb'][u'api_key']}
        if   com == "mov": endpoint = "movie"
        elif com == "col": endpoint = "collection"
        elif com == "per": 
            endpoint = "person"
            key.update({"append_to_response" : "movie_credits"})
        url = "https://api.themoviedb.org/3/{0}/{1}".format(endpoint, str(args))
    
    good = False
    tries = 1
    while not good:    
        response = requests.get(url, params = key )
        response.content.decode("utf-8")
        code = response.status_code 
        
        if code == 200: # GOOD
            good = True
            return response.json()  ## EXIT
        elif code == 404: # MINOR
            good = True
            return code ## EXIT
        elif code == 429: # TOO FAST
            wait = int(response.headers["Retry-After"]) + 1 
            if not quiet: print(words[u'text'][u'api_wait'].format(wait))
            time.sleep(wait) ## LOOP
        elif code == 401: fatal(words[u'text'][u'api_auth'].format(host))
        elif code in (502,503): fatal(u"\n" + words[u'text'][u'offline'].format(host, check_num))
        else: # UNKNOWN
            if tries < 6: ## RETRY
                print(words[u'text'][u'api_misc'].format(host, code, tries))
                time.sleep(5 + tries)
                tries += 1 ### LOOP
            else: 
                printtime = False
                fatal(u"\n" + words[u'text'][u'api_retry'].format(host, check_num)) ## FATAL
    
# Movie in Database Check & POST Function

def database_check(id_check, white_name, json_in, input_data):
    global cache, fails, printtime, added
    if id_check in tmdb_ids:
        skip.append(id_check) 
        log(words[u'text'][u'in_data'].format(*mov_info(tmdb_ids.index(id_check))))
    else:
        lookup_json = api("Radarr", com = "lookup", args = id_check)
        w_rad, w_id, w_title = whitespace(id_check, lookup_json['title'], lookup_json['year'], "")
        payload = " "*11, w_rad, id_check, w_id, lookup_json['title'], lookup_json['year'], w_title
    # check for rejections
        if id_check in blacklist: log(words[u'text'][u'ignore'].format(*payload))
        elif lookup_json[u'ratings'][u'tmdb'][u'value'] < float(config[u'blacklist'][u'min_rating']) or lookup_json['ratings'][u'tmdb'][u'votes'] < int(config[u'blacklist'][u'min_votes']): log(words[u'text'][u'rated'].format(*payload))
        elif stage != 3 and lookup_json[u'year'] < int(config[u'blacklist'][u'min_year']): log(words[u'text'][u'early'].format(*payload + (config[u'blacklist'][u'min_year'],)))
        elif stage == 3 and lookup_json[u'year'] < int(people[person][u'min_year']): log(words[u'text'][u'early'].format(*payload + (people[person][u'min_year'],)))
        elif lookup_json[u'year'] == 0 and 'true' in config[u'blacklist'][u'ignore_zero'].lower(): log(words[u'text'][u'ignore_zero'].format(*payload))
        else: # add movie
            log(words[u'text'][u'not_data'].format(*payload))
            if stage == 0: 
                try: index = tmdb_ids.index(input_data)
                except: index = tmdb_ids.index(int(config[u"adding"][u"profile"]))
            elif stage == 1: index = input_data
            elif stage == 2: index = tmdb_ids.index(input_data) 
            elif stage == 3: index = tmdb_ids.index(int(config[u'adding'][u'profile']))
            folder = str(lookup_json[u"title"]).replace(":","") + " (" + str(lookup_json[u"year"]) + ")"
            if u'true' in config[u'radarr'][u'docker']: rootpath = str(PurePosixPath(data[index]['path']).parent)
            else: rootpath = str(Path(data[index]['path']).parent)
            post_data = lookup_json       
            post_data.update({
                u"id": 0,
                u"monitored" : "true" in config[u'adding'][u'monitored'].lower(),
                u"rootFolderPath" : rootpath, 
                u"folder": folder,
                u"qualityProfileId": int(data[index][u'qualityProfileId']), 
                u"minimumAvailability" : "released",
                u"tags": [], 
                u"addOptions" : {u"searchForMovie" : "true" in config[u'adding'][u'autosearch'].lower()}
                            })

            white_cid = " "*(15 - len(str(post_data["tmdbId"])))
            if stage == 3: name = json_in['name'] + input_data
            else: name = json_in['name']
            payload = words[u'text'][u'found'].format(name.encode('utf-8'), white_name, post_data[u'tmdbId'], white_cid, post_data['title'], post_data['year'])
            if stage in [0, 1, 2]: found_col.append(payload)
            elif stage == 3: found_per.append(payload)
            found_black.append(post_data[u'tmdbId'])
            if not cache:
                post = api("Radarr", com = "post", args = post_data)
                white_yn = " "*(rad_top + 10)
                if post == 201: 
                    log(words[u'text'][u'add_true'].format(white_yn))
                    tmdb_ids.append(post_data['tmdbId'])
                    added += 1
                else:
                    log(words[u'text'][u'add_fail'].format(white_yn, post))
                    fails += 1
                    if fails == 10:
                        cache = True
                        printtime = False
                        log(u"\n" + words[u'text'][u'retry_err'] +  u"\n")
                        printtime = True

# Collection Parts Check Function

def collection_check(col_id, tmdbId = None):
    if single: log("")
    col_json = api("TMDB", com = "col", args = col_id)
    if len(col_json['name']) < int(config[u'results'][u'column']): top_c = int(config[u'results'][u'column'])
    else: top_c = len(col_json['name']) + 5
    white_name = " "*(top_c - len(col_json['name'])) 
    parts = [col['id'] for col in col_json['parts']]
    number = len(parts)
    if stage == 1:
        try: parts.remove(int(tmdbId))
        except: pass
        log("")
    if stage in [0, 1]: payload = ">", " "*(1 + len(str(len(data)))), col_json['name'], col_id, number
    elif stage == 2: payload = str(check_num + 1) + ":", white_dex, col_json['name'], col_id, number
    if stage == 1: input_id = check_num
    elif stage in [0, 2]:
        source = list(set(parts).intersection(tmdb_ids))
        if len(source) > 0: input_id = source[0]
        elif not cache: input_id = int(config[u'adding'][u'profile'])
        else: input_id = None
    log(words[u'text'][u'other'].format(*payload) +  u"\n")
    for id_check in parts:  database_check(id_check, white_name, col_json, input_id)
    if any([full, all([not full, tmdbId not in skip])]): log("")
                
# Movie in Collection Check Function

def tmdb_check(tmdbId):
    mov_json = api("TMDB", com = "mov", args = tmdbId)
    if mov_json == 404: log(words[u'text'][u'col_err'].format(logtext))
    elif type(mov_json['belongs_to_collection']) != type(None): # Collection Found
        col_id = mov_json['belongs_to_collection'][u'id']
        if col_id not in col_ids: col_ids.append(col_id)
        log(words[u'text'][u'in_col'].format(logtext))
        collection_check(col_id, tmdbId)
    else: log(words[u'text'][u'no_col'].format(logtext))          

# Person Credits Check Function

def person_check(person):
    per_id = int(people[person][u'id'])
    per_json = api("TMDB", com = "per", args = per_id)
    
    if len(per_json[u'name']) + 20 < int(config[u'results'][u'column']): top_p = int(config[u'results'][u'column'])
    else: top_p = len(per_json[u'name']) + 25
    search = [role.strip().title() for role in people[person][u'monitor'].split(",")]
    reject = [role.strip().lower() for role in people[person][u'reject'].split(",")]
    if u'&name' in reject: reject.append(per_json[u'name'].lower())
    payload = str(per_num + 1) + ":", white_dex, per_json['name'], per_id, ", ".join(search)
    log(words[u'text'][u'person'].format(*payload))
    scan_hold = []
    if len(list(set(search).intersection(['Cast','Acting']))) != 0:
        cast = []
        for movie in per_json[u'movie_credits']['cast']:
            try: role = movie[u'character'].lower()
            except: 
                movie[u'character'] = u'No Data'
                role = movie[u'character'].lower()
            for string in ["/","(",")"]: role = role.replace(string,",")
            role = role.split(",")
            role = [string.strip() for string in role]
            if not any([len(list(set(role).intersection(reject))) != 0,
                         all(['&blank' in reject,
                              movie[u'character'] == ""])]):
                cast.append(movie)
        log("")
        log(words[u'text'][u'cast'].format(len(cast)))
        log("")
        for movie in cast:
            scan_hold.append(movie['id'])
            white_name = " "*(top_p - len(per_json['name'] + " - Cast - " + movie[u'character']))
            database_check(movie['id'], white_name, per_json, " - Cast - " + movie[u'character'].title())
    roles = {}
    for movie in per_json[u'movie_credits']['crew']:
        if all([movie['department'].title() in search, \
                movie['id'] not in scan_hold]):
            if movie['department'] not in roles.keys():
                roles.update({movie['department'] : []})
            roles[movie['department']].append([movie['id'],movie['job'].title()])
            scan_hold.append(movie['id'])
    for role in roles.keys(): 
        log("")
        log(words[u'text'][u'crew'].format(role, len(roles[role])))
        log("")        
        for tmdb_Id, job in roles[role]:
            white_name = " "*(top_p - len(per_json['name'] + " - " + role + " - " + job))    
            database_check(tmdb_Id, white_name, per_json, " - " + role + " - " + job)

#%% Config Check

if len(sys.argv) != 1 and sys.argv[1][0] != "-": config_path = get_dir(sys.argv[1])
else: nologfatal(u"\n" + u"Error - path to config folder must be given in command. eg: python rcm.py ./config")
if not Path.exists(Path.joinpath(config_path, "rcm.conf")): nologfatal(u"\n" + "Error - {}/rcm.conf does not exist.".format(config_path))

#%% Configuration

start_time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")    
    
words = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(),allow_no_value=True)
words.read(Path.joinpath(config_path,u'words.conf'))
config = configparser.ConfigParser(allow_no_value=True)
config.read(Path.joinpath(config_path,u'rcm.conf'))
people = configparser.ConfigParser(allow_no_value=True)
people.read(Path.joinpath(config_path,u'people.conf'))

if config[u'results'][u'path'] == "": config[u'results'][u'path'] = u"./"
output_path = get_dir(config[u'results'][u'path'])

for folder in ["logs","output"]: 
    with Path.joinpath(output_path, folder) as fold: 
        if not Path.exists(fold): Path.mkdir(fold)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[2:],"hqdfas:ncpt:u",["help","quiet","down","full","start=","nolog","cache","people","tmdbid=","up"])
    except getopt.GetoptError:
        print(u"\n" + u'Error in options\n')
        print(words[u'help'][u'text'])
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(words[u'help'][u'text'])
            sys.exit()
        elif opt in ("-q", "--quiet"): quiet = True
        elif opt in ("-f", "--full"): full = True
        elif opt in ("-p", "--people"): peeps = True
        elif opt in ("-s", "--start"): check_num = int(arg)
        elif opt in ("-n", "--nolog"): nolog = True
        elif opt in ("-c", "--cache"): cache = True
        elif opt in ("-u", "--up"): quick = True
        elif opt in ("-t", "--tmdbid"):
            single = True
            single_id = int(arg)

if check_num != 0: full = True

skip, old_want, old_unmon, col_ids = [],[], [],[]

with Path.joinpath(config_path, u'memory.dat') as file:
    if Path.exists(file):
        memory = open(Path.joinpath(config_path, u'memory.dat'), "r")
        memory = memory.readlines()
        
        if not full: 
            skip = memory[0].strip('[]\n').split(',')
            skip = [int(mov_id) for mov_id in skip]
            try:
                old_want = memory[2].strip('[]\n').split(',')
                if old_want[0] != "": old_want = [int(mov_id) for mov_id in old_want]
                else: old_want = []
            except: pass
            try:
                old_unmon = memory[3].strip('[]\n').split(',')
                if old_unmon[0] != "": old_unmon = [int(mov_id) for mov_id in old_unmon]
                else: old_unmon = []
            except: pass
        
        if full and check_num == 0: col_ids = []
        else:
            col_ids = memory[1].strip('[]\n').split(',')
            if col_ids[0] != "": col_ids = [int(col_id) for col_id in col_ids]
            else: col_ids = []
    else:
        check_num = 0
        first = True
        full = True


#%% Data grab

if u'true' in config[u'radarr'][u'ssl'].lower(): radarr_url = u"https://"
else: radarr_url = u"http://"
radarr_url += u"{0}/api/v3/movie".format(config[u'radarr'][u'server'])

data = api("Radarr")
tmdb_ids, wanted, unmon = [],[],[]
for movie in data:
    tmdb_ids.append(movie["tmdbId"])
    if u'true' in config[u'results'][u'ignore_wanted'].lower() and not movie['hasFile']: 
        wanted.append(movie["tmdbId"])
    if u'true' in config[u'results'][u'ignore_unmonitored'].lower() and not movie['monitored']:
        unmon.append(movie["tmdbId"])

if full: numbers = [len(data) - check_num]
else: 
    numbers = [max(0, len(data) - len(skip + old_want) - len(set(old_unmon) - set(old_want).intersection(old_unmon)) \
                   + len(set(old_unmon) - set(unmon) - set(wanted)) \
                   + len(set(old_want) - set(wanted) - set(unmon)))]
numbers += [len(col_ids), len(people.sections())]

blacklist = config[u'blacklist'][u'blacklist'].split(",")
if blacklist[0] != "": blacklist = [int(mov_id) for mov_id in blacklist]

title_top = max([len(movie["title"]) for movie in data]) + 2
rad_top = len(str(data[-1]['id'])) + 1

found_col, found_per, found_black, = [],[],[]
fails = 0
added = 0
  
#%% Fatal Input Errors

if full and quick: nologfatal(u"\n" + words[u'text'][u'uf_err'])
if check_num > len(data): nologfatal(u"\n" + words[u'text'][u'start_err'].format(check_num, len(data)))
if len(people.sections()) != 0:
    if not cache:
        try: int(config[u'adding'][u'profile'])
        except: nologfatal("{0} {1}".format(u"\n" + words[u'text'][u'template_err'], words[u'text'][u'int_err'])) 
        if int(config[u'adding'][u'profile']) not in tmdb_ids: nologfatal(u"\n" + "{0} {1}".format(words[u'text'][u'template_err'], words[u'text'][u'prof_err']))

if u'added_total' not in words[u'text']: nologfatal(u"\n Error - Please download latest words.conf file")

#%% Begin
        
log(words[u'text'][u'hello'] +  u"\n")
if first: log(words[u'text'][u'first'])
if cache: log(words[u'text'][u'cache'])
if single:
    if peeps: 
        log(words[u'text'][u'tp_err'])
        peeps = False
    if quick: 
        log(words[u'text'][u'tu_err'])
        quick = False
else: # Not single
    if peeps:
        if quick: 
            log(words[u'text'][u'up_err'])
            peeps = False
        else: log(words[u'text'][u'peeps'])
    else: # not single not peeps
        if check_num != 0: log(words[u'text'][u'start'].format(check_num))

if any([single, peeps, quick, cache, first]): log("")

if not peeps and not single: 
    if full: log(words[u'text'][u'full_scan'].format(*numbers) +  u"\n")
    elif quick: log(words[u'text'][u'quick_scan'].format(*numbers) +  u"\n")
    else: log(words[u'text'][u'update_scan'].format(*numbers) +  u"\n")

atexit.register(datadump)

#%% Single Scan Mode
stage = 0
if single:
    printtime = True
    check_num = 1
    lookup_json = api("Radarr", com = "lookup", args = single_id)
    w_rad, w_id, w_title = whitespace(single_id, lookup_json['title'], lookup_json['year'], "")
    payload = "", " "*(len(str(len(data))) + 13 + len(w_rad) - len(words[u'text'][u'single'])), single_id, w_id, lookup_json['title'], lookup_json['year'], w_title
    logtext = words[u'text'][u'single'] + words[u'text'][u'mov_info'].format(*payload)
    tmdb_check(single_id)
    log(u"")
    sys.exit()

#%% Database Search Loop
stage = 1
if not peeps:    
    if numbers[0] > 0: 
        log(words[u'text'][u'run_mov_mon'].format(*numbers) + u":\n")
        printtime= True
        for movie in data[check_num:]:
            white_dex = " "*(len(str(len(data))) + 1 - len(str(check_num + 1)))
            payload = mov_info(check_num)
            logtext = "{0}:{1}".format(check_num + 1, white_dex) + words[u'text'][u'radarr'].format(*payload) + words[u'text'][u'mov_info'].format(*payload)
            
            if movie["tmdbId"] in unmon: 
                if movie["tmdbId"] not in old_unmon + old_want: log(words[u'text'][u'unmonitored'].format(logtext))
            elif movie["tmdbId"] in wanted: 
                if movie["tmdbId"] not in old_unmon + old_want: log(words[u'text'][u'file'].format(logtext))
            elif movie["tmdbId"] in skip:
                if full or movie["tmdbId"] in old_unmon + old_want: log(words[u'text'][u'checked'].format(logtext)) # if id in list
            else: tmdb_check(movie["tmdbId"]) 
            check_num += 1
        log("")
if quick: sys.exit()

#%% Collection Monitor Loop
stage = 2
if not peeps and not full:
    data = api("Radarr")
    printtime = False
    log(words[u'text'][u'run_col_mon'].format(*numbers) + u":\n")
    printtime= True
    for check_num, col_id in enumerate(col_ids):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(check_num + 1)))
        collection_check(col_id)

#%% Person Monitor Loop
stage = 3
if len(people.sections()) != 0:
    printtime = False
    log(words[u'text'][u'run_per_mon'].format(*numbers) + u":\n")
    printtime= True  
    for per_num, person in enumerate(people.sections()):
        white_dex = " "*(len(str(len(data))) + 1 - len(str(per_num + 1)))
        person_check(person)
        log("")
