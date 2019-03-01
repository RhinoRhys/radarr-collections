#!/usr/bin/env python2
# -*- coding: utf-8 -*-

helptext = ["rcm.py <option>",
            "",
            "Options:",
            "-h \t help",
            "-q \t disable verbose logging",
            "-f \t run full scan, recheck all movies",
            "-d \t only check downloaded movies, ignore wanted list",
            "-a \t output artwork URL file",
            "-s <num> \t specify start point",
            "-n \t disable text logging - ignores unresolved logging issue",
            "-c \t disable automatic adding to radarr"]

hello = "Welcome to Radarr Collection Manager by RhinoRhys \n"

start_err = "Fatal Error - Start point too high - Exiting \n"
opts_err = "Options Error - All functions disabled, not adding or writing output - Exiting\n"
api_auth = "Error Unauthorized - Please check your %s API key"
api_retry = "Fatal Error - Retry limit reached - Exiting at item %i \n"
api_misc = "Unplanned error from %s API, return code: %i - Retrying, attempt %i \n"
api_wait = "Too many requests - waiting %i seconds \n"

partial = "Running partial scan: only checking movies added since last run\n"
full = "Running full scan: checking all items\n"
wanted = "Ignore wanted list active: only checking movies with files\n"
art = "Collection Artwork URLs file will be created\n"
start = "Start point specified: skipping %i items\n"

bye = "Found %i movies \n\n" + "Thank You for using Radarr Collection Manager by RhinoRhys"

