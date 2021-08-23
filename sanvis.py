#!/usr/bin/env python3

# https://medium.com/@benjaminmbrown/real-time-data-visualization-with-d3-crossfilter-and-websockets-in-python-tutorial-dba5255e7f0e

import utils,geo,ads,config

import sys,time,datetime

from collections import defaultdict

import connections
import ip2dns
import datatoname
import monitor_domains
# Link connections to the sankey visualization
def sankey():
	nodes=[]
	links=[]
	adClassification={}
	nonAdClassification={}
	nameToDomains=defaultdict(lambda: [])
	nameToIPs=defaultdict(lambda: [])
	unaggregated=defaultdict(lambda: defaultdict(lambda: [])) # homeip->name->[]
	homeToNameLastActivity=defaultdict(lambda: {})
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
			extra["title"] = ("%s (%.0f laitetta)") % (extra["title"],extra["hitcount"])

		nodes.append(extra)


	def addLink(s,name,hitcount,actualtargets,v=1,last_act=0):
		s=str(s)
		t=str(name)
		for link in links:
			if link["source"]==s and link["target"]==t:
				return

		addNode(s)
		#print("adClassification.get(t,False)",adClassification.get(t,False),"t=",t)
		addNode(t,{"hitcount": hitcount, "ad": adClassification.get(t,False)})
		links.append({
			"source": s,
			"target": t,
			"value": v,
			"last_act": time.time()-last_act,
			"actualtargets":  actualtargets
		})
	link_count=0
	candidates={}
	name_hits={}

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

		#TODO: packetIn gets swapped also if this istrue
		homeip = connections.getHomeIPFromConnection(conn)
		remoteip = conn.get("dst")
		if homeip==remoteip:
			remoteip = conn.get("src")
			homeip = conn.get("dst")
		else:
			remoteip = conn.get("dst")
			homeip = conn.get("src")
		
		# Skip uninteresting
		if remoteip==config.homenetwork_router or homeip==config.homenetwork_router:
			continue

		# We want to display the short form
		homeip=utils.shortenHomeIPMemorableUniq(homeip,True)
		names=ip2dns.getShortByIp(remoteip)
		remote_resolved=False
		# Shrink resolved name list (if possible) to only actually resolved domains
		if names and names!=[]:
			names_resolved=monitor_domains.filterOnlyResolvedDomains(names,short=True)
			if names_resolved and names_resolved!=[]:
				names=names_resolved
		
				remote_resolved=names_resolved

		# Generate an aggregate name for us
		name=str(remoteip)

		aggregated=False
		if names:
			if len(names)>1:
				monitor_domains.sortDomainsByLastResolved(names)
				aggregated=True
			name=names[0]
		else:
			asname=geo.asn(remoteip)[1]
			if asname:
				name=asname
			
		# Google is always aggregated
		if config.aggregate_google and "google" in name.lower():
			name="Google"
		elif aggregated:
			name="*"+name
		
		l=unaggregated[homeip][name]
		remote=str(remoteip)
		if remote_resolved and len(remote_resolved)>0:
			remote=" ".join(remote_resolved)

		s="%s dport=%s %s"%(str(remote),str(conn["dport"]),str(conn["protoname"]))
		if s not in l:
			l.append(s)

		# Classify IP/domain as advert domain
		isad = ads.classifyIP(remoteip,check_domains=True)
		if isad and not adClassification.get(name):
			#print("setad",name)
			adClassification[name]="ad"
		elif not nonAdClassification.get(name):
			nonAdClassification[name]=True
			#print("SKIP?",name)

		# Store domains for  aggregate 
		details=nameToDomains[name]
		for n in (names or []):
			if n not in details:
				details.append(n)

		# Store IPs for the aggregate name
		details=nameToIPs[name]
		details.append(str(remoteip))


		# Store targets for homeip
		cnames=candidates.get(homeip)
		if not cnames:
			cnames=[]
			candidates[homeip]=cnames
		if name not in cnames:
			cnames.append(name)

			link_count+=1
			name_hits[name]=name_hits.get(name,0)+1

		# store last activity for this name
		homeipNames=homeToNameLastActivity[homeip]
		last_act=max(conn["lastActivity"],conn["gone"])
		homeipNames[name]=min(homeipNames.get(name,time.time()),last_act)
		

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
	
	# OOPS: If we try finding common links and there none then show at least something (TODO: sort by target freshness and only show 25 targets instead of reducing to only common targets)
	if final_count<1:
		ONLY_COMMON_LINKS=False
		final_count=link_count

	# ... and purge if we are
	if final_count>24:
		popular_names=[(k,v) for k,v in name_hits.items()]
		popular_names.sort(key=lambda x: x[1],reverse =True)
		popular_names=popular_names[:24]
#		print("popular_names=",popular_names)
		popular_names=[name for name,hits in popular_names]
#		print("popular_names=",popular_names)
		
		deletable=[]
		for k,names in candidates.items():
			newlist=[n for n in names if n in popular_names]
			if not newlist:
				deletable.append(k)	
			candidates[k]=newlist
		
		for k in deletable:
			print("killing altogether",k)
			del candidates[k]


		PURGED_NAMES=True

	# Finally add the links for real if they match our criteria
	for homeip,names in candidates.items():
		for name in names:
			if ONLY_COMMON_LINKS and namePopularity[name]<=1:
				continue
			last_act=homeToNameLastActivity[homeip][name]
			actualtargets=unaggregated[homeip][name]
			addLink(homeip,name,namePopularity[name],actualtargets,last_act=last_act)

	ret = {
		"nodes": nodes,
		"links": links,
		"namedetails": nameToDomains,
		"nameToIP": nameToIPs,
		"containing": "purged" if PURGED_NAMES else ("common" if ONLY_COMMON_LINKS else "all"),
		"link_count": link_count
	}
	return ret

