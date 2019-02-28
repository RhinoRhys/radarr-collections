"""
Radarr settings
api key can be found under Settings > General
path is to your root movie folder where the new items will be added
profile is the numerical ID assigned by Radarr - see Readme for more info
"""
radarr = {"host" : "localhost",
          "port": "7878",
          "base_url": "",
          "api_key" : "insert api key",
          }

# API key for TMDB
tmdbkey = "insert api key"

# Reccomended defaults below are False, you'll be suprised how many movies will be added on the first run!

# Add new items monitored
monitored = False

# Automatically run a historical / backlog search when new items added
autosearch = False
