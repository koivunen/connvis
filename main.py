#!/usr/bin/env python3

# https://medium.com/@benjaminmbrown/real-time-data-visualization-with-d3-crossfilter-and-websockets-in-python-tutorial-dba5255e7f0e


import config


import utils,geo

import sys,time,datetime

import ip2dns
if config.args.nodnsseed==False:
	print("seeding domains from dnsmasq journal")
	ip2dns.seedFromDnsmasq()
import ads; ads.init()

print("starting connection monitoring")
import connections; connections.start_tracking()
time.sleep(0.1)
print("starting domain monitoring")
import monitor_domains; monitor_domains.start_monitoring()
time.sleep(0.1)

# piping (WIP)
from sanvis import sankey
from dnsvis import provider as dnsbar
from geovis import provider as geoprov

print("starting httpd")
import vishttp; vishttp.run_threaded()

vishttp.setSankeyProvider(sankey)
vishttp.setGeoProvider(geoprov)
vishttp.setDnsBarProvider(dnsbar)
inspect_enabled=config.args.shell

import threading
def monitor():
	try:
		while True:
			time.sleep(1)
			connections.receiver_thread.join(timeout=0.0)
			if not connections.receiver_thread.is_alive():
				print("connections.receiver_thread.is_alive()")
				break
			connections.connection_thread.join(timeout=0.0)
			if not connections.connection_thread.is_alive():
				print("connections.connection_thread.is_alive()")
				break
	except KeyboardInterrupt as e:
		return

	print("monitor dying...")
	import os 
	os._exit(1)
	
monitor_thread = threading.Thread(name='monitoring', target=monitor,daemon=inspect_enabled)
monitor_thread.start()

if inspect_enabled:
	print("\n")
	time.sleep(1)
	print("\n")
	print("============ Inspection shell enabled ============")

	import traceback, sys, code
	def debug_provider(provider):
		try:
			provider()
		except:
			type, value, tb = sys.exc_info()
			traceback.print_exc()
			last_frame = lambda tb=tb: last_frame(tb.tb_next) if tb.tb_next else tb
			frame = last_frame().tb_frame
			ns = dict(frame.f_globals)
			ns.update(frame.f_locals)
			print("============ Exception! You can now debug inline it ============")
			code.interact(local=ns)


	import code; code.interact(local=locals())
	print("\n")
	print("CONNVIS Quit")
else:
	time.sleep(1)
	print("CONNVIS Ready!")