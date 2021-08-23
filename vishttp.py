from flask import Flask, request, send_from_directory, jsonify, render_template, Response
import folium
import threading
import random
import sys
import config
import math
import geojson
from geojson import Feature, Point, FeatureCollection

app = Flask(__name__,
			static_url_path='',
			static_folder='static',
			template_folder='templates')


@app.route('/folium')
def index():
	start_coords = (46.9540700, 142.7360300)
	folium_map = folium.Map(location=start_coords, zoom_start=14)
	return folium_map._repr_html_()


import config
import connections
@app.route('/deviceactivity.json')
def ipinfo():
	acts = {}
	activity_local = {}
	for ip,last_activity in connections.getIPActivity().items():
		if ip in config.homenetwork:
			activity_local[str(ip)]=last_activity
		else:
			acts[str(ip)]=last_activity

	return jsonify({        
		"activity": acts,   
		"activity_local": activity_local,
	})

@app.route('/config.json')
def configjson():
	return jsonify({  "homenetwork": str(config.homenetwork) })

import monitor_domains
@app.route('/ipdomainquerymappingshort.json')
def ipdomainquerymappingshort():
	return jsonify({        "mapping": monitor_domains.getIPQueryMappingShort()    })

# Geo visualization

def GeoProvider():
	"Example geoprovider"
	
	features = []
	features.append(Feature(properties={
		"id": "1",
		"ip": "10.0.0.0",
		"asnname": "localhost",
	},geometry=Point((random.random() * 360 - 180, random.random() * 360 - 180))))
	features.append(Feature(properties={    
		"id": "2",
		"ip": "10.0.0.1",
		"asnname": "localhost2",
	},geometry=Point((random.random() * 360 - 180, random.random() * 360 - 180))))

	data = FeatureCollection(features)
	return data


#TODO less ugly
def setGeoProvider(p):
	global GeoProvider
	GeoProvider=p

@app.route('/geo.json')
def geodata():
	return Response(
		response=geojson.dumps(GeoProvider(), sort_keys=False),
		mimetype='application/json',
		status=200)


def dnsBarProvider():
	return {}

def setDnsBarProvider(p):
	global dnsBarProvider
	dnsBarProvider=p

@app.route('/dnsbar.json')
def dnsbar():
	return jsonify(dnsBarProvider())

@app.route('/dnsbar_unshort.json')
def dnsbar_unshort():
	return jsonify(dnsBarProvider(short=False))





 #  Sankey visualization

def SankeyProvider():
	return jsonify({})

def setSankeyProvider(p):
	global SankeyProvider
	SankeyProvider=p

@app.route('/sankey.json')
def sankeyjson():
	return jsonify(SankeyProvider())

import ipaddress,utils
@app.route("/")
def main():
	yourip=ipaddress.ip_address(request.remote_addr)
	yourname=request.remote_addr
	if yourip in config.homenetwork:
		yourname=utils.shortenHomeIPMemorableUniq(yourip,True)
		
	return render_template("hello.html",yourip=yourip,yourname=yourname)


def run(use_reloader=False):
	app.run(debug=True, host='0.0.0.0', use_reloader=use_reloader)



def run_threaded():
	threading.Thread(target=run).start()

if __name__ == "__main__":
	run(use_reloader=True)
