
from collections import defaultdict

ip2queryShort=defaultdict(lambda: {})
ip2query=defaultdict(lambda: {})
def getIPQueryMappingShort():
	return ip2queryShort
def getIPQueryMapping():
	return ip2query

def sortDomainsByLastResolved(domains,reverse=False):
	now=time.time()
	domains.sort(reverse=reverse, key=lambda d: (lastDomainResolveTime(d) or now+2,lastDomainResolveTime(d,True) or now+1,d))


resolveShortTimeList={}
resolveTimeList={}
def wasResolved(domain,short=False):
	"was domain or its short form resolved this session"
	l = resolveTimeList
	if short:
		domain=ip2dns.shorten(domain)
		l = resolveShortTimeList
	resolved = l.get(domain,False)
	return True if resolved else False

def wasResolvedBy(domain,ip=False,short=False):
	raise NotImplementedError("todo")

def filterOnlyResolvedDomains(domains,short=False):
	"return the domains that were actually resolved during this session (short=compare using short form)"
	ret=[]
	for d in domains:
		if wasResolved(d,short):
			ret.append(d)
	if ret!=[]:
		return ret
	return False

# For prioritizing shown domains
def lastDomainResolveTime(domain,short=False):
	l = resolveTimeList
	if short:
		domain=ip2dns.shorten(domain)
		l=resolveShortTimeList
	return l.get(domain)

import time

import ip2dns
import ipaddress
import config
def onData(entry):
	pass	


import select

import subprocess
import sys

process = subprocess.Popen(["sni-sniffer","--sniff",config.internal_interface], stdout=subprocess.PIPE)
for c in iter(lambda: process.stdout.read(1), b""):
	sys.stdout.buffer.write(c)

def monitor():

	reader = ndjson.reader(f)
	try:
		for post in reader:
			print(post)
	except KeyboardInterrupt as e:
		return

import threading
def start_monitoring():
	monitor_thread = threading.Thread(name='monitorthread', target=monitor, daemon=True)
	monitor_thread.start()


if __name__ == '__main__':
	monitor()