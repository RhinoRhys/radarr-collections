helptext = ["rcm.py <option>",
            "",
            "Options:",
            "-h \t help",
            "-q \t disable verbose logging",
            "-f \t run full scan, recheck all movies",
            "-d \t only check downloaded movies, ignore wanted list",
            "-a \t output artwork URL file",
            "-s <num> \t specify start point",
            "-n \t disable text logging - ignores unresolved logging issue",
            "-c \t disable automatic adding to radarr"]

hello = "Welcome to Radarr Collection Manager by RhinoRhys" + "\n"

start_err = "Error - Start point {0} greater that data length {1} - Exiting"

partial = "Running partial scan: checking {0} movies added since last run and rechecking {1} existing collections" + "\n"
full = "Running full scan: checking {0} items" + " \n"
wanted = "Ignore wanted list active: only checking movies with files" + "\n"
art = "Collection Artwork URLs file will be created" + "\n"
cache = "Auto adding disabled: saving results to file" + "\n"
start = "Start point specified: skipping {0} items" + "\n"

api_auth = "Unauthorized - Please check your {0} API key" + "\n"
api_wait = "\n" + "Too many requests - waiting {0} seconds"
api_misc = "\n" + "Unplanned error from {0} API, return code: {1} - Retrying, attempt {2}"

radarr = "Radarr ID: {0}"
mov_info = u"{1} TMDB ID: {2}{3}{4} ({5}){6}"

other = u"{0}{1}{2} (ID: {3}): {4} movies in collection:"
two =  " "*3 + ">> "
in_data  = two + radarr + mov_info + "In Library"
not_data = two + " "*11 + mov_info + "Missing"
ignore = two + " "*11 + mov_info + "Blacklisted"
found = u"{0}{1} TMDB ID: {2}{3}{4} ({5})"
col_art = u'{0}{1} https://image.tmdb.org/t/p/original{2}'
three = " "*3 + ">>>" + " "*21 + "{0}"
add_true = three + "Added sucessfully"
add_fail = three + "Failed to add [Response Code: {0}]"

exiting = " - Exiting at item {1}"
api_retry = "\n" + "{0} API Error - Retry limit reached" + exiting
offline = "\n" + "Error {0} offline" + exiting
retry_err = "\n" + "Too many errors adding to Radarr - Switching to caching mode" + "\n"

run_col_mon = "Rechecking {0} previosuly found collections:" + "\n"

found_open = "Total Movies Found: {0}" + "\n\n" \
           + "From Collections: {1}" + "\n\n" 

auto_cache = "\n" + "Too many errors adding to Radarr, found_{0}.txt has been saved in the output folder instead"
bye = "Found {0} movies" + "\n\n" + "Thank You for using Radarr Collection Manager by RhinoRhys"


