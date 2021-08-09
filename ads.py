import ip2dns,re
import ipaddress

ips={}
domains={}

def init():
	with open("ads.txt", "r") as f:
		for l in f.readlines():
			ip,domain = l.split()
			ip2dns.feed(ip,domain)
			ips[ip]="ad"
			domains[domain]="ad"
	
>>> ipaddress.ip_address('192.168.0.1') in ipaddress.ip_network('192.168.0.0/24')
