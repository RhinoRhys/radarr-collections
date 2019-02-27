# Radarr Collection Manager

A Python script for checking your [Radarr](https://radarr.video/) database against [TMDB](https://www.themoviedb.org/) Collections. <br>
This is my first experience writing code not to do with scientific data analysis so it may not be amazingly written.

## Features: <br>
Automatic Add using API, <br>
Add Monitored (optional), <br>
Automatic Search (optional) <br>
  
## Requirements:
Radarr, <br>
Your own TMDB API key <br>
  
## Getting a TMDB API key:<br>
TMDB offers free API keys to anyone with an account. Simply sign up for an account and request a key via your account settings. I did intend to embed a key into the code but couldn't work out how to hide it from public view so I'm afraid you'll need to get your own.
  
## config.py <br>
### Radarr settings <br>

**All values need to be in "" except Profile** <br>
base url should be set as "" unless needed. <br>
api key can be found under Settings > General <br>
path is to your root movie folder where the new items will be added <br>
profile is the numerical ID assigned by Radarr and does not need the "" <br>
    
#### Profile ID
To find your profile ID you will need to view the API raw data. Assuming a default install, with your Radarr API key go to http://localhost:7878/api/movies?apikey=XXX and search for "qualityProfileId". If you use more than one Profile in Radarr you will need to manually match the ID to the correct Profile by checking the movie titles (for example my films use a 1080p cut off profile and the ID was 1 and my documentaries use the Any profile and the ID was 7).

### Other Variables 
Monitored, Autosearch are boolean (True/False), do not need the "" but do need the capital first letter. <br>
The first time you run this script, it is reccomended to have both set to False. From a database of 1200 movies, this found 180 new movies on my first run and having it autosearch all of these is a bad idea.

tmdbkey is where to paste your TMDB API key and needs the ""

## Running
Once the config file is set up, simply run `python rcm.py` to initiate the sync. <br>
Once the script has run, it will save a list of TMDB IDs in the Radarr database at that moment. Running `python rcm.py` again will initiate an update scan and import the list and only check items added to Radarr since to save on unnecessary API calls to TMDB. Running `python rcm.py full` will not import this list and will run a full scan and recheck every item.

## Output
As well as as the complete log file there is an output folder with additional files. <br>
added [date].txt is a secondary log file that lists the movies that have been added on that run. It is not created if 0 movies are added. <br>
art.txt is a list of every collection that has been checked along with the URL to the default collection artwork from TMDB to be easily pasted into Plex or other media apps.
