import sqlite3
import sys
import re
from dateutil.parser import parser

def parse_query(l):	
	if 'query[' in l:
		m = re.search('^query\[(.*)\] (.*) from (.*)', l)
		#print(l,m)
		r = {'query_type':m.group(1), 'query':m.group(2), 'source':m.group(3)}
		return r


origin_domain = False
newdomain=False
do_clear=False
def reset():
	global origin_domain
	global newdomain
	global do_clear
	origin_domain=False
	newdomain=False


def parse_reply(l):
	global newdomain
	global origin_domain
	global do_clear
	if 'reply ' not in l:
		return

	m = re.search('reply (.*) is (.*)$', l)
	dns=m.group(1)

	# Track if we are replying to same domain
	if newdomain == False:
		newdomain = dns

	same_domain = newdomain == dns
	if not same_domain:
		newdomain = dns

	if do_clear and not same_domain:
		do_clear = False
		origin_domain = False

	result=m.group(2)

	# Set origin domain (first reply api.facebook.com is <CNAME>)
	if not origin_domain and ("CNAME" in result):
		origin_domain = dns

	# Use the original domain
	if origin_domain and ("CNAME" not in result):
		#print("dns swap",dns,"->",origin_domain)
		dns=origin_domain

	ip = m.group(2)
		
	r = {'domain':dns, 'ip':ip}
		# Clear if we have a result IP (reply star.c10r.facebook.com is 31.13.72.8)

	if origin_domain and "CNAME" not in result:
		do_clear = True
	if "CNAME" not in result:
		return r


if __name__ == '__main__':
		
	import select
	from systemd import journal

	j = journal.Reader()
	j.log_level(journal.LOG_INFO)

	j.add_match(_SYSTEMD_UNIT="dnsmasq.service")
	for entry in j:
		print(entry['__REALTIME_TIMESTAMP'] )
		import code; code.interact(local=locals())
		l=entry['MESSAGE']
		print("\n","TEST:",l)
		r=parse_reply(l)
		if r:
			print("\n\t\t PARSE REPLY ANSWER",r)
		q = parse_query(l)
		if q:
			print("\n\t\t PARSE QUERY ANSWER",q)
