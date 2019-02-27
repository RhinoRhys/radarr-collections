# radarr-collections

A Python script for checking your Radarr database against TMDB Collections. <br>
This is my first experience writing code not to do with scientific data analysis so it may not be amazingly written.

## Features: <br>
Automatic Add using API, <br>
Add Monitored (optional), <br>
Automatic Historical Search (optional) <br>
  
## Requirements:
Radarr, <br>
Your own TMDB API key <br>
  
## Getting a TMDB API key:<br>
TMDB offers free API keys to anyone with an account. Simply sign up for an account and request a key via your account settings. I did intend to use a single key for the entire app but could not work out how to hide it from public view so you'll need to get your own.
  
## config.py <br>
### Radarr settings <br>

**All values need "" except Profile** <br>
base url should be set as "" unless needed. <br>
api key can be found under Settings > General <br>
path is to your root movie folder where the new items will be added <br>
profile is the numerical ID assigned by Radarr and does not need the "" <br>
    
To find your quality profile ID you will need to view the API raw data. <br>
After finding your Radarr API key (and assuming a default install), go to http://localhost:7878/api/movies?apikey=### and search for "qualityProfileId". If you use more than one Profile in Radarr you will need to manually match the ID to the correct Profile by checking the movie title. <br>
For example my films use a 1080p cutoff profile with ID of 1 and my documentaries use the Any profile with ID of 7.

### Other Variables 
Monitored, Autosearch and Full are boolean (True/False), do not need the "" but do need the capital first letter. <br>
The first time you run this script, it is reccomended to have all three set to False. From a library of 1200 movies, this script found 180 new movies on my first run, having it autosearch all of these is a bad idea.

tmdbkey is where to paste your TMDB API key and needs the ""

## Output

## Running
Once the config file is written, simply run rcm.py to initiate the search. There is currently no function for automation or monitoring but movies are released so infrequently that once you've done the initial 
