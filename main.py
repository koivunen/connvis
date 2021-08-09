#!/usr/bin/env python3

# https://medium.com/@benjaminmbrown/real-time-data-visualization-with-d3-crossfilter-and-websockets-in-python-tutorial-dba5255e7f0e

import vishttp
vishttp.run_threaded()
import connections
connections.start_tracking()