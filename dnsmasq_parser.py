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

	r = {'domain':dns, 'ip':m.group(2)}
		# Clear if we have a result IP (reply star.c10r.facebook.com is 31.13.72.8)

	if origin_domain and "CNAME" not in result:
		do_clear = True
	if "CNAME" not in result:
		return r

import select
from systemd import journal

j = journal.Reader()
j.log_level(journal.LOG_INFO)

# j.add_match(_SYSTEMD_UNIT="systemd-udevd.service")
j.seek_tail()
j.get_previous()
# j.get_next() # it seems this is not necessary.

p = select.poll()
p.register(j, j.get_events())

while p.poll():
    if j.process() != journal.APPEND:
        continue

    # Your example code has too many get_next() (i.e, "while j.get_next()" and "for event in j") which cause skipping entry.
    # Since each iteration of a journal.Reader() object is equal to "get_next()", just do simple iteration.
    for entry in j:
        if entry['MESSAGE'] != "":
            print(str(entry['__REALTIME_TIMESTAMP'] )+ ' ' + entry['MESSAGE'])