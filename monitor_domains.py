

ip2queryShort={}
def getIPQueryMappingShort():
	return ip2queryShort
def getLatestQueriedDomains():
	raise AssertionError("TODO: useful?")

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
		db[domain]=time.time()
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

	while poller.poll():
		if reader.process() != journal.APPEND:
			continue

		for entry in reader:
			if entry['MESSAGE']:
				onJournalMessage(entry)

import threading
def start_monitoring():
	monitor_thread = threading.Thread(name='monitorthread', target=monitor)
	monitor_thread.start()


if __name__ == '__main__':
	monitor()