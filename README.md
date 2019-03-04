# Radarr Collection Manager

A Python script for checking your [Radarr](https://radarr.video/) database against [TMDB](https://www.themoviedb.org/) Collections. <br>

This downloads information directly from the movie's TMDB page and TMDB Collections are strictly limited to sequels. For example, with [Dark Knight (2008)](https://www.themoviedb.org/movie/155-the-dark-knight) in my database, this will look at the attached [collection information](https://www.themoviedb.org/collection/263-the-dark-knight-collection?language=en-US), check the Radarr database for [Batman Begins (2005)](https://www.themoviedb.org/movie/272?language=en-US) and [The Dark Knight Rises (2012)](https://www.themoviedb.org/movie/49026?language=en-US) and can either automatically add any missing into the database or save as a list for manual browsing. If you already have two or more of the movies in a collection, it will only check the collection once. 

## Optional Features: <br>
- Automatically added into Radarr (default) _or_ save results to text file, <br> 
	- Add Monitored _or_ Unmonitored, <br>
    - Automatic search, <br>
- Ignore wanted list - only check movies with files, <br>
- Save list of collection artwork URLs to text file, <br>
- Set blacklist of TMDB IDs to ignore. <br>
  
## Requirements:
- Radarr, <br>
- Your own TMDB API key, <br>
- Python requests module<br>
	`pip install requests`
  
## Getting a TMDB API key:
TMDB offers free API keys to anyone with an account. Simply sign up for an account and request a key via your account settings. I did intend to embed a key into the code but couldn't work out how to hide it from public view so I'm afraid you'll need to get your own.
  
## config.py
### Radarr settings

All values need to be in ""<br>

- **Host and Port** <br>
If running Radarr in a Docker or on a different machine, the host will need to be set to the IP address of the (virtual) machine running Radarr. Please use the same values as you use for accessing the web interface. Default for running on the same machine is `"localhost"` and `"7878"` <br>

- **base url** <br>
Used for reverse proxies. Should be set as `"off"` unless needed, if used needs to have / included eg. `"/radarr"`. <br>

- **api key** <br>
Can be found under Settings > General <br>

### Other Variables 
**tmdbkey** is where to paste your TMDB API key, also needs "".

**Monitored** and **Autosearch** are boolean (`True`/`False`) switches, need the capital first letter but do not need the "" <br>
The first time you run the script, it is reccomended to have both set to False. From a database of 1200 movies, this added 180 more on my first run and having it autosearch all of these is a bad idea. Having them unmonitored makes them easy to filter in Radarr movie editor for bulk editing.

### Blacklist
Is there a sequel that you just don't want? Simply search for it on TMDB and grab the ID from the web address and add it to the blacklist. For example the web address for The Dark Knight Rises has the ID 49026 in it.

**force_ignore** should be a comma separated list of TMDB IDs in [ &nbsp; ] to ignore if missing from the database. For example, to ignore both other Batman movies and only keep the middle one, I would have: `force_ignore = [272, 49026]`

## Running
Download and extract the zip or clone with git to a location of your choice. Edit config.py with your values then, in Command Prompt or Terminal, navigate into the downloaded folder and run `python rcm.py` to initiate a scan.<br>

After the initial scan, it will save a list of all the TMDB IDs in your Radarr database and all the Collection IDs discovered. Once this is saved, running the script again in the default mode will run an update scan, only checking movies that have been added to Radarr since and then rechecking the collections for new additions. 

#### Options

You are able to change the function and output by running as `python rcm.py [options]`

|	Short	|	Long	|	Use	|
|	---		|	---		|	---	|
| `-h` | `--help`		|	Displays this help.	|
| `-f` | `--full`		|	Run full scan, recheck all movies.	|
| `-d` | `--down`		|	Only search movies with files. Ignore Wanted list.	|
| `-q` | `--quiet`		|	Disables verbose logging in command line. Log file still created.	|
| `-n` | `--nolog` 	|	Disables text file log output.	|
| `-c` | `--cache`		|	Disables automatic adding to Radarr, instead saves list of missing movies to text file.	|
| `-s <num>` | `--start <num>`	|	Specify start point, useful for big libraries if errors occur. (forces `-f`)	|
| `-a` | `--art`		|	Saves list of Collection artwork URLs to text file.	|

Multiple options can be passed in, in any order. `python rcm.py -d -q -f` would work for example.

## Additional Output Files

- When running with the `-c` option, found\_date\_time.txt is the scan results file that lists the movies that have been found on that run. It is not created if 0 movies are found.  <br>
> Movies Found: 1
> 
> The Dark Knight Collection    TMDB ID: 272    Batman Begins (2005)

- When running with the `-a` option, art\_date\_time.txt is a list of every collection that has been checked along with the URL to the default collection artwork from TMDB to be easily pasted into Plex or other media apps.
> The Dark Knight Collection 	 	https://image.tmdb.org/t/p/original/bqS2lMgGkuodIXtDILFWTSWDDpa.jpg 
