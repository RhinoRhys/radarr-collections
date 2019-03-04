helptext = ["rcm.py <option>",
            "",
            "Options:",
            "| Short    | Long          | Use",
            "|----------|---------------|---------",
            "| -h       | --help        | Displays this help.",
            "| -f       | --full        | Repeat initial scan, recheck all movies.	",
            "| -s <num> | --start <num> | Specify start point, useful for big libraries if errors occur. (forces -f)",
            "| -d       | --down        | Only search movies with files. Ignore Wanted list.",
            "| -p       | --people      | Disable all Collection scanning, only scan People."
            "| -q       | --quiet       | Disables verbose logging in command line. Log file still created.",
            "| -n       | --nolog       | Disables log file creation. Verbose logging still visible.",
            "| -c       | --cache       | Disables automatic adding to Radarr, instead saves list of missing movies to text file.",
            "| -a       | --art         | Saves list of Collection artwork URLs to text file."
            ]
            
hello = "Welcome to Radarr Collection and People Manager by RhinoRhys" + "\n"

start_err = "Error - Start point {0} greater that data length {1} - Exiting"

peeps = "People only mode: Ignoring Collections" + "\n"

run_mov_mon = "Checking {0} Movies"
run_col_mon = "Checking {1} existing Collections"
run_per_mon = "Checking {2} monitored People"

full = "Running full scan:" + "\n" \
     + " ->\t" + run_mov_mon + " \n" \
     + " ->\t" + run_per_mon
     
update = "Running update scan:" + "\n" \
        + " ->\t" + run_mov_mon + "\n" \
        + " ->\t" + run_col_mon + "\n" \
        + " ->\t" + run_per_mon 

wanted = "Ignore wanted list active: only checking Movies with files" + "\n"
art = "Collection Artwork URLs file will be created" + "\n"
cache = "Auto adding disabled: saving results to file" + "\n"
start = "Start point specified: skipping {0} items" + "\n"

api_auth = "Unauthorized - Please check your {0} API key" + "\n"
api_wait = "\n" + "Too many requests - waiting {0} seconds"
api_misc = "\n" + "Unplanned error from {0} API, return code: {1} - Retrying, attempt {2}"

radarr = "Radarr ID: {0}"
mov_info = u"{1} TMDB ID: {2}{3}{4} ({5}){6}"

other = u"{0}{1}{2} (ID: {3}): {4} Movies in collection:"
person = u"{0}{1}{2} (ID: {3}): Monitoring: {4}"

two =  " "*3 + ">> "
in_data  = two + radarr + mov_info + "In Library"
not_data = two + " "*11 + mov_info + "Missing"
ignore = two + " "*11 + mov_info + "Blacklisted"
found = u"{0}{1} TMDB ID: {2}{3}{4} ({5})"
col_art = u'{0}{1} https://image.tmdb.org/t/p/original{2}'

cast = two + "Appeared in {0} Movies:"
crew = two + "Credited on {0} Movies:"

three = " "*3 + ">>>" + " "*21 + "{0}"
add_true = three + "Added sucessfully"
add_fail = three + "Failed to add [Response Code: {0}]"

exiting = " - Exiting at item {1}"
api_retry = "{0} API Error - Retry limit reached" + exiting
offline = "Error {0} offline" + exiting
retry_err = "Too many errors adding to Radarr - Switching to caching mode"

found_open = "Total Movies Found: {0}" + "\n"
found_start = "From Collections: {1}" + "\n" 
found_middle = "From People: {2}" + "\n"

auto_cache = "Too many errors adding to Radarr, found_{0}.txt has been saved in the output folder instead"
bye = "Found {0} Movies" + "\n\n" + "Thank You for using Radarr Collection and People Manager by RhinoRhys"


