# Radarr Collection and People Manager

A Python script for checking your [Radarr](https://radarr.video/) database against Collections and People's careers on [TMDB](https://www.themoviedb.org/).

This downloads information directly from the Movie's TMDB page and Collections are strictly limited to sequels. For example, with [Dark Knight (2008)](https://www.themoviedb.org/movie/155-the-dark-knight) in my database, this will look at the attached [collection information](https://www.themoviedb.org/collection/263-the-dark-knight-collection?language=en-US), check the Radarr database for [Batman Begins (2005)](https://www.themoviedb.org/movie/272?language=en-US) and [The Dark Knight Rises (2012)](https://www.themoviedb.org/movie/49026?language=en-US) and can either automatically add any missing into the database or save as a list for manual browsing.

People can also be monitored to automatically find missing Movies from their Acting, Writng, Directing, and / or Production credits as listed on their [TMDB page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US). 

## Optional Features:
- Automatically added into Radarr _or_ save results to text file, 
	- Add Monitored _or_ Unmonitored, 
	- Automatic search, 
- Follow People and grab everything with / by them, 
	- People only mode - disable scanning collections,
- Ignore wanted list - only check movies with files, 
- Save list of collection artwork URLs to text file, 
- Set blacklist of TMDB IDs to ignore, 
- Exclude results by minimum ratings and votes, 
- Single TMDB ID scan.
  
## Requirements:
- Radarr, 
- Your own TMDB API key.
  
**Getting a TMDB API key:** TMDB offers free API keys to anyone with an account. Simply sign up and request a key via your account settings.
  
## Setting up the configuration file

The config folder can be named and placed anywhere on your computer and the directory path must be specified when running the command.

In the config folder, rename `rcm.default.conf` to `rcm.conf`.

#### Radarr settings

- **server** - Please use the same address as you use for accessing the web interface in your browser. Default for running on the same machine is `localhost:7878`.
- **api_key** - Can be found under Settings > General.
- **ssl** [`True`|`False`] - Changes to `https://` in Radarr URL instead of `http://`.
- **docker** [`True`|`False`] - Forces a linux style directory path for when running from Windows with Radarr in a Docker or on a remote linux machine.


### TMDB 
- **api_key** - Your TMDB API (v3) key. 

#### Adding
Settings for automatic adding into Radarr. If using, the first time you run the script it is reccomended to have both set to False. This will find a lot of movies on the first run and having it autosearch all of these is a bad idea, having them unmonitored makes them easier to filter in Radarr.
- **monitored** [`True`|`False`] - Add new movies monitored.
- **autosearch** [`True`|`False`] - Automatically run a historical / backlog search when added.
- **profile** is the TMDB ID of a Movie in your database that will be used to copy the Profile and Root Path from when adding movies via People Monitoring and as a back-up for single scan mode if no movies in the collection are in the database.

#### Output
- **column** - Minimum width for first column in output files, I had to give it a number to make everything line up so it might as well be here.
- **path** - Set folder where the two `output` and `logs` folders will be created. Default is to use the current working directory.

#### Blacklist
While checking for movie information, TMDB ratings and the number of votes that contributed were also included so can be used to exclude poorly rated movies.
- **min_rating** - Scale from 0.0 to 10.0
- **min_votes** - Minimum number of votes

There are a lot of bad sequels out there. To block a movie from being imported, simply find it on TMDB and grab the ID number from the web address and add it to the blacklist. Alternatively, the save file option lists the TMDB IDs in in the results file.
- **blacklist** - Comma separated list of TMDB IDs to ignore if missing from the database. For example, to ignore both other Batman movies and only keep the middle one, I would have: `blacklist = 272, 49026`

## Setting up People Monitoring

Do you want everything by a certain Actor, Producer, Director or Writer? Grab their TMDB ID from their profile web address and using the template below, select which credits you would like to monitor. Should work with 'Cast' for acting roles and any of the separating headers on their [TMDB profile page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US) or [this list](https://www.themoviedb.org/talk/598c3a70925141080100e601).

In the config folder, change `people.default.conf` to `people.conf`.

For each person you wish to follow you need to make a new entry into `people.conf`
- **header** The section header needs to be their name inside [ &nbsp; ]
- **id** - The person's TMDB ID.
- **monitor** - Comma separated list of the roles you wish to follw for that person.

Template:
> [NAME] <br>
> id = TMDB ID <br>
> monitor = Cast, Directing, Production, Writing <br>

Example:
> [Quentin Tarantino] <br>
> id = 138 <br>
> monitor = Directing, Production, Writing <br>

## Running
**Local**
- Download and extract the zip or clone with git to a location of your choice,
- You may name and place the config folder anywhere on the computer, the given command assumes it has been left as `config` in the same folder as `rcm.py`.
- In the config folder, rename `rcm.default.conf` to `rcm.conf`, edit it for your values and optionally set up `people.conf`, and
- In Command Prompt or Terminal, navigate into the downloaded folder and run `python rcm.py ./config` to initiate a scan. Python v2 and v3 compatible.

**Docker Container** 
- Container written and maintained by **Roxedus** is available [here](https://github.com/si0972/docker-containers/tree/master/alpine/radarr-collections).

If you already have two or more of the movies in a collection, it will only check the collection once and skip the other movies. <br>
After the initial scan, it will save a list of all the TMDB IDs in your Radarr database and all the Collection IDs discovered. Once this is saved, running the script again will run an update scan, only checking movies that have been added to Radarr since and then rechecking the monitored Collections and People for new additions.

Movies added into Radarr automatically from;
- Collection scans will use the same Profile and Root Folder Path for the whole collection. 
- People Monitoring will copy the Profile and Root Folder Path from the declared movie in the config file. 
- Single scan mode will check if any of the collection are already in the database and copy that or copy the declared movie if none are found.

#### Options

You are able to change the function and output by running as `python rcm.py ./config [options]`

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

Multiple options can be passed in, in any order. `python rcm.py ./config -d -q -f` would work for example.

#### Common Problems

> Traceback (most recent call last): File "rcm.py", line 4, in <module> import requests, json, datetime, os, sys, getopt, time, atexit, configparser ImportError: No module named XXXX
- You do not have the 'requests' or 'configparser' Python module(s) installed.
- `pip install requests configparser`

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

## Support

- [Discord](https://discord.gg/nXcFvWX)
- [Reddit](https://www.reddit.com/user/RhinoRhys)
