"""
Radarr settings
api key can be found under Settings > General
"""
radarr = {"host" : "localhost",
          "port": "7878",
          "base_url": "off",
          "api_key" : "insert api key",
          }

# API key for TMDB
tmdbkey = "insert api key"

# Reccomended defaults below are False, you'll be suprised how many movies will be added on the first run!
# Add new items monitored
monitored = False
# Automatically run a historical / backlog search when new items added
autosearch = False

"""
Blacklist
Comma separated list of TMDB IDs to ignore if missing from database eg [272, 49026]
"""
force_ignore = []

"""
People to follow

NAME for easy identification in file, not actually used.

Template: 
          '<<TMDB ID>>' : { 'name' : '<<NAME>>', 'monitor' : ['cast','directing','production','writing']},

"""
people = {
        }