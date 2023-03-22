from multiprocessing import Value
import ip2dns,re
import ipaddress

ips={}
domains={}

def init():
	with open("data/ads.txt", "r") as f:
		for l in f.readlines():
			try:
				ip,domain = l.split()
			except:
				print("Failed parsing from data/ads.txt: ",l)
				continue
			ip=ipaddress.ip_address(ip)
			ips[int(ip)]="ad" # todo: ad/tracking/malware/???
			domains[domain]="ad" # todo: ad/tracking/malware/???
			
			# TODO: move
			ip2dns.feed(ip,domain) 
	with open("data/ads_domainsonly.txt", "r") as f:
		for domain in f.readlines():
			domain=domain.strip()
			if domain and " " not in domain:
				domains[domain]="ad" # todo: ad/tracking/malware/???

def classifyIP(ip,check_domains=False):
	isad = ips.get(int(ip))
	if isad:
		return isad
	if check_domains:
		domains = ip2dns.getByIp(ip)
		if domains:
			for domain in domains:
				isad = classifyDomain(domain)
				if isad:
					return isad
				
		names=ip2dns.getShortByIp(ip)
		if names:
			for domain in names:
				isad = classifyDomain(domain)
				if isad:
					return isad
	return False

def classifyDomain(domain):
	assert not isinstance(domain, list),"supply a domain"

	return domains.get(domain)

if __name__ == '__main__':
	init()
	for k,v in domains.items():
		print("domains",k,v)
		break
	for k,v in ips.items():
		print("ips",k,v)
		break
	print("get chartbeat",classifyDomain(ip2dns.getByIp(ipaddress.ip_address("174.129.218.62"))))
