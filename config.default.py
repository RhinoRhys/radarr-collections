"""
Radarr settings
api key can be found under Settings > General
"""
# Force unix style file path
docker = False
# Use host/base_url instead of host:port
reverse_proxy = False
# Use https:// instead of http://
ssl = False

radarr = {"host" : "localhost",
          "port": "7878",
          "base_url": "",
          "api_key" : "insert api key",
          }

# API key (v3) for TMDB
tmdbkey = "insert api key"

# Reccomended defaults below are False, you'll be suprised how many movies will be added on the first run!
# Add new items monitored
monitored = False
# Automatically run a historical / backlog search when new items added
autosearch = False

# Minimum column width for output files
column = 60

"""
Blacklist
Comma separated list of TMDB IDs to ignore if missing from database eg [272, 49026]
"""
min_rating = 0
min_votes = 0

force_ignore = []

"""
People to follow

profile is the TMDB ID of a Movie in your database that will be used to copy the Profile and Root Path from when adding movies from People Monitoring

NAME for easy identification in file, not actually used.

Template: 
          '<<TMDB ID>>' : { 'name' : '<<NAME>>', 'monitor' : ['Cast','Directing','Production','Writing']},

"""
profile = 0
people = {
          }
