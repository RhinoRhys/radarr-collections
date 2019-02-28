# Radarr Collection Manager

A Python script for checking your [Radarr](https://radarr.video/) database against [TMDB](https://www.themoviedb.org/) Collections. <br>
This is my first experience writing code not to do with scientific data analysis so it may not be amazingly written.

This will check every movie in your Radarr database, it does not matter if the movie is downloaded or wanted, my thought process was if you want one of them, you'll want the whole set but this could be filtered if requested. This downloads information directly from the movie's TMDB page and TMDB Collections are strictly limited to sequels. For example, with [Dark Knight (2008)](https://www.themoviedb.org/movie/155-the-dark-knight) in my database, this will look at the attached [collection information](https://www.themoviedb.org/collection/263-the-dark-knight-collection?language=en-US), check the Radarr database for [Batman Begins (2005)](https://www.themoviedb.org/movie/272?language=en-US) and [The Dark Knight Rises (2012)](https://www.themoviedb.org/movie/49026?language=en-US) and then will automatically add any that are not in the database. If you already have two or more of the movies in a collection, it will only check the collection once. 

**Update**
Multiple root folder support - New items added will use the same root folder as the movie currently being checked.

## Features: <br>
- Automatically Added into Radarr using API, <br>
- Option to add Monitored or Unmonitored, <br>
- Automatic Search (optional), <br>
- Outputs list of collection artwork URLs to text file. 
  
## Requirements:
- Radarr, <br>
- Your own TMDB API key. <br>
  
## Getting a TMDB API key:<br>
TMDB offers free API keys to anyone with an account. Simply sign up for an account and request a key via your account settings. I did intend to embed a key into the code but couldn't work out how to hide it from public view so I'm afraid you'll need to get your own.
  
## config.py <br>
### Radarr settings <br>

All values need to be in "" except Profile <br>
- host is default "localhost"
- port is default "7878"
- base url should be set as "off" unless needed, if used needs / <br>
- api key can be found under Settings > General <br>
- profile is the numerical ID assigned by Radarr and does not need the "" <br>
    
#### Profile ID
To find your profile ID you will need to view the API raw data. Assuming a default install, with your Radarr API key go to `http://localhost:7878/api/movie?apikey=XXX` and search for "qualityProfileId". If you use more than one Profile in Radarr you will need to manually match the ID to the correct Profile by checking the movie titles (for example my films use a 1080p cut off profile and the ID was 1 and my documentaries use the Any profile and the ID was 7).

### Other Variables 
tmdbkey is where to paste your TMDB API key and needs the ""

Monitored and Autosearch are boolean (True/False) switches, do not need the "" but do need the capital first letter. <br>
The first time you run the script, it is reccomended to have both set to False. From a database of 1200 movies, this added 180 more on my first run and having it autosearch all of these is a bad idea.

## Running
- Once the config file is set up, simply run `python rcm.py` to initiate the sync. Once the script has run, it will save a list of all the TMDB IDs in your Radarr database at that moment. 
- Running `python rcm.py` again will initiate an update scan, import the list and only check items added to Radarr since to save on unnecessary API calls to TMDB. 
- Running `python rcm.py -f` or `--full` will not import this list and will run a full scan and recheck every item.

### Command line options
- `-h` or `--help`	displays this help
- `-f` or `--full`	run full scan 
- `-q` or `--quiet`	disable verbose logging in command line. log file still created. 

## Output
As well as as the complete log file there is an output folder with additional files. <br>
- added [date].txt is a secondary log file that lists the movies that have been added on that run. It is not created if 0 movies are added. <br>
- art.txt is a list of every collection that has been checked along with the URL to the default collection artwork from TMDB to be easily pasted into Plex or other media apps.
