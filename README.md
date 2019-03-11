# Radarr Collection and People Manager

A Python script for checking your [Radarr](https://radarr.video/) database against Collections and People's careers on [TMDB](https://www.themoviedb.org/).

This downloads information directly from the Movie's TMDB page and Collections are strictly limited to sequels. For example, with [Dark Knight (2008)](https://www.themoviedb.org/movie/155-the-dark-knight) in my database, this will look at the attached [collection information](https://www.themoviedb.org/collection/263-the-dark-knight-collection?language=en-US), check the Radarr database for [Batman Begins (2005)](https://www.themoviedb.org/movie/272?language=en-US) and [The Dark Knight Rises (2012)](https://www.themoviedb.org/movie/49026?language=en-US) and can either automatically add any missing into the database or save as a list for manual browsing.

People can also be monitored to automatically find missing Movies from their Acting, Writng, Directing, and / or Production credits as listed on their [TMDB page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US).

**Jump to:**
- [Setting up config files](https://github.com/RhinoRhys/radarr-collections#setting-up-the-configuration-files)
- [Setting up People monitoring](https://github.com/RhinoRhys/radarr-collections#people-monitoring)
- [Install and Run](https://github.com/RhinoRhys/radarr-collections#installation-and-running)
- [Get in touch](https://github.com/RhinoRhys/radarr-collections#get-in-touch)

## Optional Features:
- Automatically added into Radarr _or_ save results to text file. 
	- Add Monitored _or_ Unmonitored.
	- Automatic search.
- Follow People and grab everything with / by them.
	- People only mode - disable scanning collections.
- Ignore wanted list - only check movies with files.
- Save list of collection artwork URLs to text file.
- Set blacklist of movies to ignore.
- Exclude results by minimum ratings and votes.
- Single movie scan mode.
  
## Requirements:
- Radarr
- Your own TMDB API key.
  
**Getting a TMDB API key:** TMDB offers free API keys to anyone with an account. Simply sign up and request a key via your account settings.
  
## Setting up the configuration files

The config folder can be named and placed anywhere on your computer and the directory path must be specified when running the command.

In the config folder, make a copy of `rcm.default.conf`, rename it `rcm.conf` and open it with any text editor.

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
- **profile** is the TMDB ID number of a Movie in your database that will be used to copy the Profile and Root Path from when adding movies via People Monitoring and as a back-up for single scan mode if no movies in the collection are in the database. You need to find a movie in Radarr that has the root folder and profile that you want to copy and take the number from the end of the web address, `localhost:7878/movies/name-of-movie-#####`. The profile variable has to be a movie TMDB ID number, it cannot be the name of a movie.

#### Output
- **column** - Minimum width for first column in output files, I had to give it a number to make everything line up so it might as well be here.
- **path** - Set folder where the two `output` and `logs` folders will be created. Default is to use the current working directory.

#### Blacklist
While checking for movie information, TMDB ratings and the number of votes that contributed were also included so can be used to exclude poorly rated movies.
- **min_rating** - Scale from 0.0 to 10.0
- **min_votes** - Minimum number of votes

There are a lot of bad sequels out there. To block a movie from being imported, simply find it on TMDB and grab the ID number from the web address `themoviebd.org/movie/#####-name-of-movie` and add it to the blacklist.  Alternatively, running the script with automatic adding disabled will list the movie TMDB ID numbers in the results file.
- **blacklist** - Comma separated list of movie TMDB ID numbers to ignore if missing from the database. For example, to ignore both other Batman movies and only keep the middle one, I would have: `blacklist = 272, 49026`

## People Monitoring

Do you want everything by a certain Actor, Producer, Director or Writer? Grab their TMDB ID number from their [TMDB profile page](https://www.themoviedb.org/person/138-quentin-tarantino?language=en-US) web address `themoviebd.org/person/####-name-of-person` and using the template below, select which credits you would like to monitor. Should work with 'Cast' and any of the separating headers on their profile page or [this list](https://www.themoviedb.org/talk/598c3a70925141080100e601).

In the config folder, make a copy of `people.default.conf` and rename it `people.conf`.

#### Setting up an individual to follow
 
For each person you wish to follow you need to make a new entry into `people.conf`.
- **header** The section header should be their name inside [ &nbsp; ].
- **id** - The person's TMDB ID number.
- **monitor** - Comma separated list of the roles you wish to follow for that person.

Template:
> [NAME] <br>
> id = TMDB ID <br>
> monitor = Cast, Directing, Production, Writing <br>

Example:
> [Quentin Tarantino] <br>
> id = 138 <br>
> monitor = Directing, Production, Writing <br>

## Installation and Running
**Local**
- Download and extract the zip or clone with git to a location of your choice.
- You may name and place the config folder anywhere on the computer, the given command assumes the folder is still named `config` in the same folder as `rcm.py`.
- In the config folder, make a copy of `rcm.default.conf` and rename it `rcm.conf`, edit `rcm.conf` for your values and optionally set up `people.conf`.
- In Command Prompt or Terminal, navigate into the downloaded folder and run `python rcm.py ./config` to begin a scan with the default running options. Python v2 and v3 compatible.

**Docker Container** 
- Container written and maintained by **Roxedus**, and is available [here](https://github.com/si0972/docker-containers/tree/master/alpine/radarr-collections).
```
docker create \
  --name=radarr-collections \
  -v <path to data>:/config \
  -e PGID=<gid> -e PUID=<uid>  \
  -e args=CHANGE_ME \ 
  si0972/radarr-collections
```
The `args` enviroment variable refers to the [running options](https://github.com/RhinoRhys/radarr-collections#running-options).

I know nothing about Docker myself so cannot assist with any related issues, please open issues about the container [here](https://github.com/si0972/docker-containers/issues/new).

**Running Process** <br>
Running without any mode options will default to a **full update scan** after one **full initial scan** has completed.

If you already have two or more of the movies in a collection, it will only check the collection once and skip the other movies so you may see large chunks of skipped movies towards the end.

Movies added into Radarr automatically from;
- Collection scans will use the same Profile and Root Folder Path for the whole collection. 
- People Monitoring will copy the Profile and Root Folder Path from the movie set in the varibale below. 
- Single scan mode will check if any of the collection are already in the database and copy that or copy the people monitoring default if none are found.

### Running options

You are able to change the mode and output by running as `python rcm.py ./config [options]`. <br>

| Short | Long 			| Use |
|---|---|---|
| `-h` | `--help`		| Displays this help.	|
| | **Conflicting** | **Mode options** |
| `-f` | `--full`		| Repeat full initial scan - recheck all movies.	|
| `-u` | `--up`			| Reduced update scan - only check recently added items.	|
| `-p` | `--people`		| People only mode - disable all collection scanning	|
| `-t <num>` | `--tmdbid <num>` | Single scan mode - check single TMDB ID for Collections.	|
| `-s <num>` | `--start <num>`	| Specify start point - useful for big libraries if errors occur. (forces `-f`)	|
| | **Independant** | **Output options** |
| `-d` | `--down`		| Only search movies with files. Ignore Wanted list.	|
| `-q` | `--quiet`		| Disables verbose logging in command line. Log file still created.	|
| `-n` | `--nolog` 		| Disables log file creation. Verbose logging still visible.	|
| `-c` | `--cache`		| Disables automatic adding to Radarr, instead saves list of missing movies to text file.	|
| `-a` | `--art`		| Saves list of Collection artwork URLs to text file.	|

Multiple options can be passed in, in any order. `python rcm.py ./config -d -q -f` would work for example.

### Scan Modes
#### Full initial Scan

The first time the script is run, or when running with the `-f` option, every movie in your Radarr database will be checked for collections, then your monitored people if set up. After this complete scan, it will save a list of all the movie TMDB ID numbers in your Radarr database and all the Collection ID numbers discovered. 

#### Full update Scan

Running the script after this data is saved will perform an update scan, only checking movies that have been added to the Radarr database since and then rechecking the previously found collections and your monitored people for any new additions. If you delete any or all of the movies in a collection from Radarr without adding them to the blacklist, the update scan will still remember the collection and try to re-add the movies. The only way to remove an entire collection from memory is to re-run the initial scan.

#### Reduced update scan

As new movies don't come out very often, running with the `-u` options allows you to check collections for newly added movies in Radarr without rechecking the saved collections or your monitored people. This is an ideal scan mode to schedule at short intervals to keep all movies added into Radarr checked.

#### Single scan

When running with the `-t <num>` option, this will only run a collection check for that movie then stop. If you have limited your full scans to only movies with files, using the `-d` option, single scan mode can be set up as a post processing script in Radarr to automatically check collections as files are downloaded.

#### People only scan

If you do not wish to check your Radarr database against collection information and are only interested in searching people's careers, collection scanning can be skipped by running with the `-p` option.

### Common Problems

> Traceback ..... ImportError: No module named XXXX
- You do not have the 'requests' or 'configparser' Python module(s) installed.
- `pip install requests configparser`

### Scheduling

To automate running a scan at set intervals, please use your inbuilt OS scheduling tool to run the command. Please be aware that once the **full initial scan** has run, the **full update scan** is unlikely to find new movies very often. This script makes one API call to TMDB per movie, collection and person that it checks, and while their network can probably handle it, it just seems like a waste to be running repeated scans when new sequels are only announced every few years and it takes months of people's time to make or be in one. A suggested set up would be to have two scheduled tasks, one running the **Reduced update scan** at regular hourly intervals to keep the database checks up to date and the other running a **full update scan** once per week, or even less, to sync your monitored items.

### Additional output files
#### Caching mode

When running with the `-c` option, no movies will be automatically added into Radarr. Instead, found\_date\_time.txt is the scan results file that lists the movies that have been found. It is not created if 0 movies are found.  <br>
> Total Movies Found: 2
> 
> From Collections: 1
> 
> The Dark Knight Collection    TMDB ID: 272    Batman Begins (2005)
> 
> From People: 1
> 
> Quentin Tarantino - Directing - Director                            TMDB ID: 187            Sin City (2005)

#### Artwork mode

When running with the `-a` option, art\_date\_time.txt is a list of every collection that has been checked along with the URL to the default collection artwork from TMDB to be easily pasted into Plex or other media apps.
> The Dark Knight Collection 	 	https://image.tmdb.org/t/p/original/bqS2lMgGkuodIXtDILFWTSWDDpa.jpg

## Get in touch

- [Discord](https://discord.gg/nXcFvWX)
- [Reddit](https://www.reddit.com/user/RhinoRhys)
