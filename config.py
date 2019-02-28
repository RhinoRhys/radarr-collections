"""
Radarr settings
api key can be found under Settings > General
path is to your root movie folder where the new items will be added
profile is the numerical ID assigned by Radarr - see Readme for more info
"""
radarr = {"host" : "mediaserver",
          "port": "7878",
          "base_url": "/film",
          "api_key" : "8192a439d494498cb31a93808e0d5980",         
          }

# API key for TMDB
tmdbkey = "05905018ab36263a8506b6e8caeb28fd"

# Reccomended defaults below are False, you'll be suprised how many movies will be added on the first run!

# Add new items monitored
monitored = True

# Automatically run a historical / backlog search when new items added
autosearch = False
