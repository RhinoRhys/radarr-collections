"""
Library of written output

To customise your logging and results files, feel free to change any of the words in " "
Changing any of the {#} variables WILL cause errors.

"""
helptext = [u"rcm.py <option>",
            u"",
            u"Options:",
            u"| Short    | Long           | Use",
            u"|----------|----------------|---------",
            u"| -h       | --help         |  Displays this help.",
            u"| -f       | --full         |  Repeat initial scan, recheck all movies.",
            u"| -s <num> | --start <num>  |  Specify start point, useful for big libraries if errors occur. (forces -f)",
            u"| -t <num> | --tmdbid <num> |  Check single TMDB ID for Collections.",
            u"| -d       | --down         |  Only search movies with files. Ignore Wanted list.",
            u"| -p       | --people       |  Disable all Collection scanning, only scan People.",
            u"| -q       | --quiet        |  Disables verbose logging in command line. Log file still created.",
            u"| -n       | --nolog        |  Disables log file creation. Verbose logging still visible.",
            u"| -c       | --cache        |  Disables automatic adding to Radarr, instead saves list of missing movies to text file.",
            u"| -a       | --art          |  Saves list of Collection artwork URLs to text file."
            ]

name = u"Radarr Collection and People Manager by u/RhinoRhys"            
hello = u"Welcome to " + name

start_err = u"Error - Start point {0} greater that data length {1} - Exiting"
template_err = u"Error - Profile template TMDB ID for People Monitoring not in database - Exiting"
tp_err = u"Error - t and p options not compatible"

peeps = u"People only mode: Ignoring Collections"

run_mov_mon = u"Checking {0} Movies"
run_col_mon = u"Checking {1} existing Collections"
run_per_mon = u"Checking {2} monitored People"

single = u"Scanning:"

dent = u" -> "
full = u"Running full scan:" + u"\n" \
     + dent + run_mov_mon + u"\n" \
     + dent + run_per_mon
     
update = u"Running update scan:" + u"\n" \
        + dent + run_mov_mon + u"\n" \
        + dent + run_col_mon + u"\n" \
        + dent + run_per_mon 

wanted = u"Ignore wanted list active: only checking Movies with files"
art = u"Collection Artwork URLs file will be created"
cache = u"Auto adding disabled: saving results to file"
start = u"Start point specified: skipping {0} items"

api_auth = u"Unauthorized - Please check your {0} API key" 
api_wait = u">>> Too many requests - waiting {0} seconds <<<"
api_misc = u">>> Unplanned error from {0} API, return code: {1} - Retrying, attempt {2} <<<"

radarr = u"Radarr ID: {0}"
mov_info = u"{1} TMDB ID: {2}{3}{4} ({5}){6}"

stage_info = u"{0}{1}{2} (ID: {3})"
other = stage_info + u": {4} Movies in collection:"
person = stage_info + u": Monitoring: {4}"

no_col = u"None"
in_col = u"In Collection"
col_err = u"Error - Not Found"
skip = u"Skipping"

two =  u" "*3 + u">> "
in_data  = two + radarr + mov_info + u"In Library"
not_data = two + u" "*11 + mov_info + u"Missing"
ignore = two + u" "*11 + mov_info + u"Blacklisted"
rated = two + u" "*11 + mov_info + u"Rating Too Low"
found = u"{0}{1} TMDB ID: {2}{3}{4} ({5})"
col_art = u'{0}{1} https://image.tmdb.org/t/p/original{2}'

cast = two + u"Appeared in {0} Movies:"
crew = two + u"Credited for {0} on {1} Movies:"

three = u" "*3 + u">>>" + u" "*21 + u"{0}"
add_true = three + dent + u"Added sucessfully"
add_fail = three + dent + u"Failed to add [Response Code: {1}]"

exiting = u" - Exiting at item {1}"
api_retry = u"{0} API Error - Retry limit reached" + exiting
offline = u"Error {0} offline" + exiting
retry_err = u"Too many errors adding to Radarr - Switching to caching mode"

found_open = u"Total Movies Found: {0}"
found_start = u"From Collections: {1}"
found_middle = u"From People: {2}"

auto_cache = u"Too many errors adding to Radarr, found_{0}.txt has been saved in the output folder instead"
bye = u"Found {0} Movies" + u"\n\n" + u"Thank You for using " + name


