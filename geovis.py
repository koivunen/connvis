
import ipaddress
import utils,geo,ads,config


import connections
import ip2dns
import pycountry

def alpha2ToName(a2):
	if not a2:
		return
	try:
		c= pycountry.countries.get(alpha_2=a2)
	except LookupError as e:
		return a2

	if c:
		return c.name
	if a2=="ZZ":
		a2="Unknown"
	return a2

import geojson
from geojson import Feature, Point, FeatureCollection
import sys,time,datetime

def populateNames(remoteip,res):
	"populates known domains and alike for this IP"

	names=ip2dns.getShortByIp(remoteip)
	if names:
		for n in names:
			if n not in res:
				if config.aggregate_google and "google" in n:
					n="Google"
				res.append(n)
	return res

def iterateViableConnections():
	now=time.time()
	for id,conn in connections.getConnections().items():
		
		#TODO: keep gone for a while (if space)
		if conn.get("gone"):
			continue
		if conn.get("state") and conn["state"]!="ESTABLISHED":
			continue

		lastEventTime = conn.get("gone") or conn.get("lastActivity")
		if now-lastEventTime>60*5:
			continue

		homeip = connections.getHomeIPFromConnection(conn)
		remoteip = conn.get("dst")
		if homeip==remoteip:
			remoteip = conn.get("src")
			homeip = conn.get("dst")
		else:
			remoteip = conn.get("dst")
			homeip = conn.get("src")
		
		# Uninteresting
		if remoteip==config.homenetwork_router or homeip==config.homenetwork_router:
			continue
		yield (homeip,remoteip,lastEventTime,conn)


def processIPPair(homeip,remoteip,lastEventTime,conn,dest):
	"Add a new ip pair for mapMarkerData"

	countrycode,coord_lat,coord_lon = geo.country(remoteip)
	if not coord_lat:
		return # Cannot do anything with this
		
	lat=dest.get(coord_lat)
	if not lat:
		lat={}
		dest[coord_lat]=lat

	lon=lat.get(coord_lon)
	if not lon:
		lon={}
		lat[coord_lon]=lon
	
	ipdata=lon.get(int(remoteip))
	if not ipdata:
		ipdata={
			"count": 0,
			"countrycode": countrycode,
			"lastEventTime": lastEventTime,
			"devices": [],
			"names": []
		}
		lon[int(remoteip)]=ipdata
	
	ipdata["count"]+=1
	ipdata["lastEventTime"]=max(ipdata["lastEventTime"],lastEventTime)
	
	names=ipdata["names"]
	populateNames(remoteip,names)
	
	# Gather originating IPs
	if homeip not in ipdata["devices"]:
		ipdata["devices"].append(homeip)


def GenerateASNListFromIPS(iplist):
	asns=[]
	asnames=[]

	for ip in iplist:
		asn,asname=geo.asn(ip)
		if asn and asn not in asns:
			asns.append(asn)
			asnames.append(asname)
	return asnames

def provider():
	"provide a geojson object from tracked connections"	

	mapMarkerData={} # latlist={lonlist={ipaddresslist={devices={},names={}}}}

	for homeip,remoteip,lastEventTime,conn in iterateViableConnections():
		processIPPair(homeip,remoteip,lastEventTime,conn,mapMarkerData)

	features = []

	id=0
	for lat,lons in mapMarkerData.items():
		for lon,coordIPs in lons.items():
			iplist=[]
			names=[]
			last_activity=0
			originators=[]
			countrycode=False # country for lat lon
			# Collect coordinate's IP addresses
			for ipdec,ipdata in coordIPs.items():
				if ipdata.get("countrycode"):
					if not countrycode:
						countrycode=ipdata["countrycode"]
					elif countrycode!=ipdata["countrycode"]:
						print("COUNTRY MISMATCH TODO?",lat,lon,countrycode,ipdata["countrycode"])
				last_activity = max(last_activity,ipdata["lastEventTime"])
				ip = ipaddress.ip_address(ipdec)
				iplist.append(ip)
				for n in ipdata["names"]:
					if n not in names:
						names.append(n)

				# Collect originators
				for homeip in ipdata["devices"]:
					if homeip not in originators:
						originators.append(homeip)

			id=id+1

			targets_ads=[str(ip) for ip in iplist if ads.classifyIP(ip,check_domains=True)]
			targets=[str(ip) for ip in iplist if str(ip) not in targets_ads]

			targetnames_ads=[name for name in names if ads.classifyDomain(name)]

			features.append(Feature(properties={
				"id": str((lon,lat)),
				"targets": targets,
				"country_code": ipdata["countrycode"],
				"country_name": alpha2ToName(ipdata["countrycode"]),
				"targets_ads": 	targets_ads,
				"targetnames": [n for n in names if n not in targetnames_ads],
				"targetnames_ads": targetnames_ads,
				"countrycode": countrycode or "ZZ",
				"last_activity": last_activity,
				"last_activity_msec": int(1000*(time.time()-last_activity)),
				"asns": GenerateASNListFromIPS(iplist),
				"originators": [utils.shortenHomeIPMemorableUniq(homeip,True) for homeip in originators]
			},geometry=Point((lon,lat))))

	data = FeatureCollection(features)
	return data
