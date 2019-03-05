# Radarr Collection and People Manager

A Python2 script for checking your [Radarr](https://radarr.video/) database against [TMDB](https://www.themoviedb.org/) Collections and following People's work.<br>

This downloads information directly from the Movie's TMDB page and Collections are strictly limited to sequels. For example, with [Dark Knight (2008)](https://www.themoviedb.org/movie/155-the-dark-knight) in my database, this will look at the attached [collection information](https://www.themoviedb.org/collection/263-the-dark-knight-collection?language=en-US), check the Radarr database for [Batman Begins (2005)](https://www.themoviedb.org/movie/272?language=en-US) and [The Dark Knight Rises (2012)](https://www.themoviedb.org/movie/49026?language=en-US) and can either automatically add any missing into the database or save as a list for manual browsing. If you already have two or more of the movies in a collection, it will only check the collection once and skip the other movies. 

People can also be monitored to automatically find missing Movies from their Acting, Writng, Directing, and / or Production credits as listed on their [TMDB page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US). 

## Optional Features: <br>
- Automatically added into Radarr _or_ save results to text file, <br> 
	- Add Monitored _or_ Unmonitored, <br>
    - Automatic search, <br>
- Follow People and grab everything with / by them, <br>
	- People only mode - disable scanning collections,<br>
- Ignore wanted list - only check movies with files, <br>
- Save list of collection artwork URLs to text file, <br>
- Set blacklist of TMDB IDs to ignore, <br>
- Exclude results by minimum ratings and votes, <br>
- Single movie scan. <br>
  
## Requirements:
- Radarr, <br>
- Your own TMDB API key, <br>
- Python requests module<br>
	`pip install requests`
  
**Getting a TMDB API key:** TMDB offers free API keys to anyone with an account. Simply sign up and request a key via your account settings.
  
## Setting up config.py
### Radarr settings

All values need to be in ""<br>

- **Host and Port** <br>
If running Radarr in a Docker or on a different machine, the host will need to be set to the IP address of the (virtual) machine running Radarr. Please use the same values as you use for accessing the web interface. Default for running on the same machine is `"localhost"` and `"7878"` <br>

- **base_url** - used for reverse proxies. Should be set as `"off"` unless needed, if used needs to have / included eg. `"/radarr"`. <br>

- **api_key** - can be found under Settings > General <br>

### Other Variables 
**tmdbkey** is where to paste your TMDB API key, also needs "".

**monitored** and **autosearch** can be set to `True` or `False`, need the capital first letter but do not need the "" <br>
If using automatic adding, the first time you run the script it is reccomended to have both set to False. From a database of 1200 movies, this added 180 more on my first run and having it autosearch all of these is a bad idea, having them unmonitored makes them easy to filter in Radarr.

### Blacklist
Is there a sequel that you just don't want? Simply find it on TMDB and grab the ID from the web address and add it to the blacklist. For example the web address for The Dark Knight Rises has the ID 49026 in it.

**force_ignore** should be a comma separated list of TMDB IDs in [ &nbsp; ] to ignore if missing from the database. For example, to ignore both other Batman movies and only keep the middle one, I would have: `force_ignore = [272, 49026]`

### People Monitoring

Do you want everything by a certain Actor, Producer, Director or Writer? Grab their TMDB ID from their profile web address and using the template below, select which credits you would like to monitor. 

**profile** is the TMDB ID of a Movie in your database that will be used to copy the Profile and Root Path from when adding movies via People Monitoring.

**people** needs to have { &nbsp; } around the whole thing and each entry needs to be comma separated. The Name varaible is only for easy file management and not used by the script.
Filter out certain roles by removing them from the monitor list. 

Template: `          "<<TMDB ID>>" : { "name" : "<<NAME>>", "monitor" : ['Cast','Directing','Production','Writing']},`
<br>
Example:

```python
profile = 49026
people = {'15277' : { 'name' : 'Jon Favreau', 'monitor' : ['Cast','Production']}, 
          '138' : { 'name' : 'Quentin Tarantino', 'monitor' : ['Directing','Production']},
        }
```

## Running
Download and extract the zip or clone with git to a location of your choice. Edit config.py with your values then, in Command Prompt or Terminal, navigate into the downloaded folder and run `python rcm.py` to initiate a scan. <br>

After the initial scan, it will save a list of all the TMDB IDs in your Radarr database and all the Collection IDs discovered. Once this is saved, running the script again will run an update scan, only checking movies that have been added to Radarr since and then rechecking the monitored Collections and People for new additions.

Movies added into Radarr from Collection scans will use the same Profile and Root Folder Path for the whole collection. Movies added from People Monitoring will copy the settings from the declared movie.

#### Options

You are able to change the function and output by running as `python rcm.py [options]`

|	Short	|	Long	|	Use	|
|	---		|	---		|	---	|
| `-h` | `--help`		|	Displays this help.	|
| `-f` | `--full`		|	Repeat initial scan, recheck all movies.	|
| `-s <num>` | `--start <num>`	|	Specify start point, useful for big libraries if errors occur. (forces `-f`)	|
| `-t <num>` | `--tmdbid <num>` |	Check single TMDB ID for Collections.	|
| `-d` | `--down`		|	Only search movies with files. Ignore Wanted list.	|
| `-p` | `--people`		| 	Disable all Collection scanning, only scan People.	|
| `-q` | `--quiet`		|	Disables verbose logging in command line. Log file still created.	|
| `-n` | `--nolog` 		|	Disables log file creation. Verbose logging still visible.	|
| `-c` | `--cache`		|	Disables automatic adding to Radarr, instead saves list of missing movies to text file.	|
| `-a` | `--art`		|	Saves list of Collection artwork URLs to text file.	|

Multiple options can be passed in, in any order. `python rcm.py -d -q -f` would work for example.

## Additional Output Files

- When running with the `-c` option, found\_date\_time.txt is the scan results file that lists the movies that have been found on that run. It is not created if 0 movies are found.  <br>
> Total Movies Found: 2
> 
> From Collections: 1
> 
> The Dark Knight Collection    TMDB ID: 272    Batman Begins (2005)
> 
> From People: 1
> 
> Quentin Tarantino - Directing                                TMDB ID: 187            Sin City (2005)

- When running with the `-a` option, art\_date\_time.txt is a list of every collection that has been checked along with the URL to the default collection artwork from TMDB to be easily pasted into Plex or other media apps.
> The Dark Knight Collection 	 	https://image.tmdb.org/t/p/original/bqS2lMgGkuodIXtDILFWTSWDDpa.jpg 
