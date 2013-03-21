Simple installation:
1) Run ./phenny - this creates a default config file
2) Edit ~/.phenny/default.py
3) Run ./phenny - this now runs phenny with your settings

-- 
Sean B. Palmer, http://inamidst.com/sbp/
Kyle Fitzsimmons, http://kylefitz.com/

Updates:
 * added rottentomatoes module
 * previous weather script relied on now defunct google secret weather api, rewrote this to query google for place name & lat,lng from input search and fetch data from wunderground api.
* added simple open "telnet" (insecure generic socket) for announcing torrents from shell scripts

Additional dependencies (folders can be unzipped and placed in root phenny file):
* simplejson
* geopy - wunderground.py
* twisted - telnet.py
* python-twitter - url.py