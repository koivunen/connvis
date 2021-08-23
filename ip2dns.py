domain2ip={}
ip2domain={}
ip2short={}
import ipaddress
def feed(ip,domain):
	#print(ip,domain)
	ipnum=int(ipaddress.ip_address(ip))

	l=ip2domain.get(ipnum)
	checkForShort=False
	if not l:
		l=[]
		ip2domain[ipnum]=l
		checkForMore=True
	if domain not in l:
		l.append(domain)
		checkForShort=True
	
	if checkForShort:
		sdomain=shorten(domain)
		l=ip2short.get(ipnum)
		if not l:
			l=[]
			ip2short[ipnum]=l
		if sdomain not in l:
			l.append(sdomain)

	l=domain2ip.get(domain)
	if not l:
		l=[]
		domain2ip[domain]=l
	if ip not in l:
		l.append(ip)

def getByIp(ip):
	return ip2domain.get(int(ip))
def getShortByIp(ip):
	return ip2short.get(int(ip))
def getByDomain(domain):
	return domain2ip.get(domain)
	
def dump():
	return (domain2ip,ip2domain,ip2short,)

def load(*args):
	domain2ip,ip2domain,ip2short=args

from publicsuffixlist import PublicSuffixList

psl = PublicSuffixList()

def shorten(domain):
	if not domain:
		return domain

	ret = psl.privatesuffix(domain)
	if ret:
		return ret
	if not psl.is_public(domain):
		print("FIXME: PSL could not digest:",domain)
	return domain # it IS a private suffix or not a domain

import dnsmasq_parser,config
def onJournalMessage(entry):
	l=entry["MESSAGE"]

	r=dnsmasq_parser.parse_reply(l)
	if r:
		ip=r["ip"]
		domain=r["domain"]
		if domain in config.ignored_domains:
			return
		if not "NODATA" in ip and not "NXDOMAIN" in ip:
			feed(ip,domain)
		return r
	
def seedFromDnsmasq():

	import select
	from systemd import journal

	j = journal.Reader()
	j.log_level(journal.LOG_INFO)

	j.add_match(_SYSTEMD_UNIT="dnsmasq.service")
	for entry in j:
		onJournalMessage(entry)

if __name__ == '__main__':
	seedFromDnsmasq()
	import pprint
	domains={}
	for domain,ips in domain2ip.items():
		domain = shorten(domain)
		if not domains.get(domain):

			domains[domain]=ips

	for k,v in domains.items():
		print(k,"\t","\t".join(v))
		continue
	#import code; code.interact(local=locals())