#!/usr/bin/env python3

# https://medium.com/@benjaminmbrown/real-time-data-visualization-with-d3-crossfilter-and-websockets-in-python-tutorial-dba5255e7f0e

import utils,geo

import sys,time,datetime


import connections
import ip2dns

# Link connections to the sankey visualization
def sankey():
	nodes=[]
	links=[]

	def addNode(id,extra=False):
		if extra is False:
			extra={}

		id=str(id)
		for node in nodes:
			if node["id"]==id:
				return node
		extra["id"]=id
		extra["title"]=id

		hitcount = extra.get("hitcount")
		if hitcount and hitcount>1:
			extra["title"] = ("%s (%.0f laitetta)").format(extra["title"],extra["hitcount"])

		nodes.append(extra)


	def addLink(s,t,hitcount,v=1):
		s=str(s)
		t=str(t)
		for link in links:
			if link["source"]==s and link["target"]==t:
				return

		addNode(s)
		addNode(t,{"hitcount": hitcount})
		links.append({
			"source": s,
			"target": t,
			"value": v
		})
	link_count=0
	candidates={}
	name_hits={}
	for id,conn in connections.getConnections().items():
		if conn["gone"]:
			continue
		if conn["state"] and conn["state"]!="ESTABLISHED":
			continue


		homeip = connections.getHomeIPFromConnection(conn)
		remoteip = conn.get("dst")
		if homeip==remoteip:
			remoteip = conn.get("src")
			homeip = conn.get("dst")
		else:
			remoteip = conn.get("dst")
			homeip = conn.get("src")

		homeip=utils.shortenIP(homeip)
		names=ip2dns.getShortByIp(remoteip)
		name="?"
		if not names:
			name=geo.asn(remoteip)[1]
			if not name:
				name=str(remoteip)
		elif len(names)>1:
			name="*"+names[0]
		else:
			name=names[0]
		if "google" in name:
			name="GOOGLE"

		cnames=candidates.get(homeip)
		if not cnames:
			cnames=[]
			candidates[homeip]=cnames
		if name not in cnames:
			cnames.append(name)
			link_count+=1
			name_hits[name]=name_hits.get(name,0)+1
	
	# If we have over 32 links then we can only show common links
	ONLY_COMMON_LINKS=link_count>32

	namePopularity={}
	for homeip,names in candidates.items():
		for cname in names:
			namePopularity[cname]=namePopularity.get(cname,0)+1

	PURGED_NAMES=False
	
	# Check if we are still over the limit...
	final_count=0
	if ONLY_COMMON_LINKS:
		for homeip,names in candidates.items():
			for name in names:
				if namePopularity[name]>1:
					final_count+=1

	# If we try finding common links there are none so show at least something (TODO: sort by target freshness)
	if final_count<1:
		ONLY_COMMON_LINKS=False
		final_count=link_count

	# ... and purge if we are
	if final_count>24:
		popular_names=[(k,v) for k,v in name_hits.items()]
		popular_names.sort(key=lambda x: x[1])[:24]
		for k,names in candidates.items():
			candidates[k]=[n for n in names if n in popular_names]

		PURGED_NAMES=True

			
	for homeip,names in candidates.items():
		for name in names:
			if ONLY_COMMON_LINKS and namePopularity[name]<=1:
				continue
			addLink(homeip,name,namePopularity[name])

	ret = {
		"nodes": nodes,
		"links": links,
		"containing": "purged" if PURGED_NAMES else ("common" if ONLY_COMMON_LINKS else "all"),
		"link_count": link_count
	}
	return ret

