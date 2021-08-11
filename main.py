#!/usr/bin/env python3

# https://medium.com/@benjaminmbrown/real-time-data-visualization-with-d3-crossfilter-and-websockets-in-python-tutorial-dba5255e7f0e

import utils,geo

import sys,time,datetime

print("seeding domains")
import ip2dns; ip2dns.seedFromDnsmasq()
import ads; ads.init()

print("starting httpd")
import vishttp; vishttp.run_threaded()
time.sleep(1)
print("starting connection monitoring")
import connections; connections.start_tracking()
time.sleep(1)
print("starting domain monitoring")
import monitor_domains; monitor_domains.start_monitoring()
time.sleep(1)

from sanvis import sankey
vishttp.setSankeyProvider(sankey)

time.sleep(1)
print("Dropping to interactive shell")
import code; code.interact(local=locals())
print("quitting")
import sys
sys.exit(0)