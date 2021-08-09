dns2ip={}
ip2dns={}

def feed(ip,dns):
	l=ip2dns.get(ip)
	if not l:
		l=[]
		ip2dns[ip]=l
	if dns not in l:
		l.append(dns)

	l=dns2ip.get(dns)
	if not l:
		l=[]
		dns2ip[ip]=l
	if ip not in l:
		l.append(ip)

def getip(ip):
	return ip2dns.get(ip)
def getdomain(dns):
	return dns2ip.get(dns)
def dump():
	return (dns2ip,ip2dns,)

import select
from systemd import journal

j = journal.Reader()
j.log_level(journal.LOG_INFO)

j.add_match(_SYSTEMD_UNIT="dnsmasq.service")
for entry in j:
	print(entry['MESSAGE'])
