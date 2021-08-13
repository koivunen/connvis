

ip2queryShort={}
def getIPQueryMappingShort():
	return ip2queryShort

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
def onJournalMessage(entry):
	l=entry["MESSAGE"]
	ts=entry['__REALTIME_TIMESTAMP'] #we are parsing real time, no use

	q = dnsmasq_parser.parse_query(l)
	if q:
		source = q["source"]
		db=ip2queryShort.get(source)
		if not db:
			db={}
			ip2queryShort[source]=db
		domain=ip2dns.shorten(q["query"])
		now=time.time()
		db[domain]=now
		sdomain=ip2dns.shorten(domain)
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