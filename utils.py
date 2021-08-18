import config
import ipaddress
def shortenIP(ip,net=config.homenetwork):
	if ip not in net:
		return False
		
	mask=net.hostmask

	masked=int(ip) & int(mask)
	ip=str(ipaddress.ip_address(masked))
	ipn=ip.removeprefix("0.").removeprefix("0.").removeprefix("0.")
	if ipn!=ip:
		ipn="."+ipn
	return ipn
import datatoname

shorten_memory_homeip=datatoname.TonameMemory()
def shortenHomeIPMemorableUniq(homeip,original_important=True,net=config.homenetwork):
	homeipname=datatoname.toname_mem(int(homeip),shorten_memory_homeip)
	if original_important:
		homeip=shortenIP(homeip,net)
		homeipname=f"{homeip}\n({homeipname})"
	return homeipname

def aggregateBigCompanies(identifier,where=False):
	if config.aggregate_google and "google" in identifier.lower(): # gvt2.com gstatic.om doubleclick
			return "google.com" 
	return identifier

if __name__ == "__main__":
	import random
	net=ipaddress.ip_network("10.0.0.0/16")
	h=[h for h in net.hosts()]
	ip = random.choice(h)
	print("shortenIP",shortenIP(ip,net))
	ip=h[0]
	print("shortenIP",shortenIP(ip,net))
	ip=h[len(h)-1]
	print("shortenIP",shortenIP(ip,net))

