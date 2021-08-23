
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
import dnsmasq_parser
import ip2dns
import ipaddress
import config
def onJournalMessage(entry):
	l=entry["MESSAGE"]
	ts=entry['__REALTIME_TIMESTAMP'] #we are parsing real time, no use

	q = dnsmasq_parser.parse_query(l)
	if q:
		source = ipaddress.ip_address(q["source"])
		domain=q["query"]
		if domain in config.ignored_domains:
			return

		sdomain=ip2dns.shorten(domain)
		now=time.time()

		ip2query[source][domain]=now
		ip2queryShort[source][sdomain]=now
		
		resolveTimeList[domain]=now
		resolveShortTimeList[sdomain]=now

		#print(q)
	else:
		ip2dns.onJournalMessage(entry)


import select
from systemd import journal
def monitor():
	reader = journal.Reader()
	reader.log_level(journal.LOG_INFO)

	reader.add_match(_SYSTEMD_UNIT="dnsmasq.service")
	reader.seek_tail()
	reader.get_previous()

	poller = select.poll()
	poller.register(reader, reader.get_events())

	try:
		while poller.poll():
			if reader.process() != journal.APPEND:
				continue

			for entry in reader:
				if entry['MESSAGE']:
					onJournalMessage(entry)
	except KeyboardInterrupt as e:
		return

import threading
def start_monitoring():
	monitor_thread = threading.Thread(name='monitorthread', target=monitor, daemon=True)
	monitor_thread.start()


if __name__ == '__main__':
	monitor()