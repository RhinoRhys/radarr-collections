"""
Radarr settings
api key can be found under Settings > General
path is to your root movie folder where the new items will be added
profile is the numerical ID assigned by Radarr - see Readme for more info
"""
radarr = {"host" : "localhost",
          "port": "7878",
          "base_url": "",
          "api_key" : "",
          "path" : ""
          "profile" : <INT>
          }

# Add new items monitored
# Reccomended default is False, you'll be suprised how many movies will be added!
monitored = False

# Automatically run a historical / backlog search when new items added
# Reccomended default is False, you'll be suprised how many movies will be added!
autosearch = False

# Full library scan (True) or only search added since last run (False)
full = True

# API key for TMDB
tmdbkey = ""
