#!/usr/bin/env python3

import ipaddress
import utils, geo, ads, config

import sys, time, datetime

from collections import defaultdict

import connections
import ip2dns
import datatoname
import monitor_domains

def provider(short=True,DOMAIN_LIMIT=32):

	bars = []
	total_domains = 0

	domain_to_age = defaultdict(lambda: 0)
	domain_to_homeips = defaultdict(lambda: set())
	domain_to_domains = defaultdict(lambda: set())

	def getImportanceSortedDomains():
		
		domain_displaylist = [(domain, len(ips))
							  for domain, ips in domain_to_homeips.items()]

		domain_last_resolve_order = list(domain_to_homeips.keys())
		monitor_domains.sortDomainsByLastResolved(domain_last_resolve_order)

		domain_displaylist.sort(key=lambda x:
								(x[1], domain_last_resolve_order.index(x[0])),
								reverse=True)
		domain_displaylist=[domain for domain,_ in domain_displaylist]
		return (domain_displaylist,domain_last_resolve_order)

	# Gather all domains
	for homeip, domains in monitor_domains.getIPQueryMapping().items():
		for domain, last_resolved in domains.items():
			if short:
				shortdomain=ip2dns.shorten(domain)
				shortdomain=utils.aggregateBigCompanies(shortdomain)
				domain_to_domains[shortdomain].add(domain)
				domain=shortdomain

			domain_to_homeips[domain].add(int(homeip))
			domain_to_age[domain] = max(domain_to_age[domain], last_resolved)

	domain_importance_sorted,domain_last_resolve_order = getImportanceSortedDomains()

	total_domains = len(domain_importance_sorted)

	# Are we hitting the limit?
	if total_domains > DOMAIN_LIMIT:
		# cull excess, if we are over the limit
		# based on query count and last query time (if only one phone, for example)

		domain_importance_sorted=domain_importance_sorted[:DOMAIN_LIMIT]
		
		domain_last_resolve_order=[a for a in domain_last_resolve_order if a in domain_importance_sorted]

		domain_to_age={domain:age for domain,age in domain_to_age.items() if domain in domain_importance_sorted}
		domain_to_homeips={domain:ips for domain,ips in domain_to_homeips.items() if domain in domain_importance_sorted}
		domain_to_domains={a:b for a,b in domain_to_domains.items() if a in domain_importance_sorted}

	# Generate homeip names
	domain_to_homeip_names = {}
	for domain, homeips in domain_to_homeips.items():
		ips_dest = []
		for ip in homeips:
			ip = ipaddress.ip_address(ip)
			ips_dest.append(utils.shortenHomeIPMemorableUniq(ip, True))
		domain_to_homeip_names[domain] = ips_dest

	bars=[]
	now=time.time()
	for domain in domain_importance_sorted:
		ips=domain_to_homeips[domain]
		
		domains=list(domain_to_domains[domain])
		monitor_domains.sortDomainsByLastResolved(domains)
		
		isad=ads.classifyDomain(domain)
		if not isad:
			for isad_domain in domains:
				isad = ads.classifyDomain(isad_domain)
				if isad:
					break

		bars.append({
			"name": domain,
			"value": len(ips),
			"homeips": domain_to_homeip_names[domain],
			"domains": domains,
			"isad": isad if isad else False,
			"last_query": domain_to_age[domain],
			"age": now-domain_to_age[domain],
		})

	ret = {
		"bars": bars,
		"total_domains": total_domains
	}
	return ret
