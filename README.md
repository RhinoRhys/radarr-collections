# Radarr Collection and People Manager

A Python script for checking your [Radarr](https://radarr.video/) database against [TMDB](https://www.themoviedb.org/) Collections and following People's work.<br>

This downloads information directly from the Movie's TMDB page and Collections are strictly limited to sequels. For example, with [Dark Knight (2008)](https://www.themoviedb.org/movie/155-the-dark-knight) in my database, this will look at the attached [collection information](https://www.themoviedb.org/collection/263-the-dark-knight-collection?language=en-US), check the Radarr database for [Batman Begins (2005)](https://www.themoviedb.org/movie/272?language=en-US) and [The Dark Knight Rises (2012)](https://www.themoviedb.org/movie/49026?language=en-US) and can either automatically add any missing into the database or save as a list for manual browsing. If you already have two or more of the movies in a collection, it will only check the collection once and skip the other movies. 

People can also be monitored to automatically find missing Movies from their Acting, Writng, Directing, and / or Production credits as listed on their [TMDB page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US). 

## Optional Features:
- Automatically added into Radarr _or_ save results to text file, <br> 
	- Add Monitored _or_ Unmonitored, <br>
    - Automatic search, <br>
- Follow People and grab everything with / by them, <br>
	- People only mode - disable scanning collections,<br>
- Ignore wanted list - only check movies with files, <br>
- Save list of collection artwork URLs to text file, <br>
- Set blacklist of TMDB IDs to ignore, <br>
- Exclude results by minimum ratings and votes, <br>
- Single TMDB ID scan. <br>
  
## Requirements:
- Radarr, <br>
- Your own TMDB API key, <br>
- Python requests module<br>
	usually `pip install requests` to get
  
**Getting a TMDB API key:** TMDB offers free API keys to anyone with an account. Simply sign up and request a key via your account settings.
  
## Setting up the configuration file

In the config folder, change `rcm.default.conf` to `rcm.conf`

### Radarr settings

- **Host and Port** <br>
If running Radarr in a Docker or on a different machine, the host will need to be set to the IP address of the (virtual) machine running Radarr. Please use the same values as you use for accessing the web interface. Default for running on the same machine is `"localhost"` and `"7878"`.<br>
- **base_url** - Used for reverse proxies. Ignored unless reverse_proxy is set to True, if used needs to have / included eg. `"/radarr"`.<br>
- **api_key** - Can be found under Settings > General.<br>
- **reverse_proxy** [`True`|`False`] - Changes your Radarr URL to `host/base_url` instead of `host:port`.<br>
- **docker** [`True`|`False`] - Forces a unix type filepath for when running from Windows into Docker.<br>
- **ssl** [`True`|`False`] - Changes to `https://` in Radarr URL instead of `http://`.<br>

### TMDB 
- **api_key** - Your TMDB API (v3) key. <br>

### Adding
Settings for automatic adding into Radarr. If using, the first time you run the script it is reccomended to have both set to False. This will find a lot of movies on the first run and having it autosearch all of these is a bad idea, having them unmonitored makes them easier to filter in Radarr.
- **monitored** [`True`|`False`] - Add new movies monitored.<br>
- **autosearch** [`True`|`False`] - Automatically run a historical / backlog search when added.<br>
- **profile** is the TMDB ID of a Movie in your database that will be used to copy the Profile and Root Path from when adding movies via People Monitoring and as a back-up for single scan mode if no movies in the collection are in the database.

### Output
- **column** - Minimum width for first column in output files, I had to give it a number to make everything line up so it might as well be here.

### Blacklist
While checking for movie information, TMDB ratings and the number of votes that contributed were also included so can be used to exclude poorly rated movies.
- **min_rating** - Scale from 0.0 to 10.0
- **min_votes** - Minimum number of votes

There are a lot of bad sequels out there. To block a movie from being imported, simply find it on TMDB and grab the ID number from the web address and add it to the blacklist. Alternatively, the save file option lists the TMDB IDs in in the results file.<br>
- **blacklist** - Comma separated list of TMDB IDs to ignore if missing from the database. For example, to ignore both other Batman movies and only keep the middle one, I would have: `blacklist = 272, 49026`

## Setting up People Monitoring

Do you want everything by a certain Actor, Producer, Director or Writer? Grab their TMDB ID from their profile web address and using the template below, select which credits you would like to monitor. Should work with 'Cast' for acting roles and any of the separating headers on their [TMDB profile page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US) or [this list](https://www.themoviedb.org/talk/598c3a70925141080100e601).<br>

In the config folder, change `people.default.conf` to `people.conf`<br>

Each person needs a header, their name inside [ &nbsp; ]<br>
- **id** - The person's TMDB ID.<br>
- **monitor** - Comma separated list of the roles you wish to follw for that person.<br>

Template:<br>
> [NAME] <br>
> id = TMDB ID <br>
> monitor = Cast, Directing, Production, Writing <br>

Example:<br>
> [Quentin Tarantino] <br>
> id = 138 <br>
> monitor = Directing, Production, Writing <br>

## Running
- Download and extract the zip or clone with git to a location of your choice, <br>
- Rename `rcm.default.conf` to `rcm.conf` in the config folder, edit it for your values and optionally set up `people.conf` as per above, and <br>
- In Command Prompt or Terminal, navigate into the downloaded folder and run `python rcm.py` to initiate a scan. <br>
	Python v2 or v3 compatible (auto add not currently v3 compatible).<br>

After the initial scan, it will save a list of all the TMDB IDs in your Radarr database and all the Collection IDs discovered. Once this is saved, running the script again will run an update scan, only checking movies that have been added to Radarr since and then rechecking the monitored Collections and People for new additions.

Movies added into Radarr automatically from;
- Collection scans will use the same Profile and Root Folder Path for the whole collection. 
- People Monitoring will copy the Profile and Root Folder Path from the declared movie in the config file. 
- Single scan mode will check if any of the collection are already in the database and copy that or copy the declared movie if none are found.

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
> Quentin Tarantino - Directing - Director                            TMDB ID: 187            Sin City (2005)

- When running with the `-a` option, art\_date\_time.txt is a list of every collection that has been checked along with the URL to the default collection artwork from TMDB to be easily pasted into Plex or other media apps.
> The Dark Knight Collection 	 	https://image.tmdb.org/t/p/original/bqS2lMgGkuodIXtDILFWTSWDDpa.jpg 
