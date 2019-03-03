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

start_err = "Fatal Error - Start point too high - Exiting"

partial = "Running partial scan: checking %i movies added since last run" + "\n"
full = "Running full scan: checking all items" + " \n"
wanted = "Ignore wanted list active: only checking movies with files" + "\n"
art = "Collection Artwork URLs file will be created" + "\n"
start = "Start point specified: skipping %i items" + "\n"
scan = "Checking %i movies" + "\n"

api_auth = "Unauthorized - Please check your %s API key" + "\n"
api_wait = "\n" + "Too many requests - waiting %i seconds"
api_misc = "\n" + "Unplanned error from %s API, return code: %i - Retrying, attempt %i"

radarr = "Radarr ID: %i"
mov_info = "%s TMDB ID: %i%s%s (%i)%s"
other = " "*8 + ">" + " "*5 + "%s: %i other movies:"
two =  " "*23 + ">> "
in_data  = two + radarr + mov_info + "In Library"
not_data = two + " "*11 + mov_info + "Missing"
three = " "*23 + ">>>" + " "*21 + "%s"
add_true = three + "Added sucessfully"
add_fail = three + "Failed to add [Response Code: %i]"

api_retry = "\n" + "%s API Error - Retry limit reached - Exiting at item %i"
retry_err = "\n" + "Too many errors adding to Radarr - Switching to caching mode" + "\n"

cache = "\n" + "Too many errors adding to Radarr, found_%s.txt has been saved in the output folder instead"
bye = "\n" + "Found %i movies" + "\n\n" + "Thank You for using Radarr Collection Manager by RhinoRhys"
