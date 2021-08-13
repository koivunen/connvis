import ipaddress
import geoip2.database

citydb=geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')
asndb=geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-ASN.mmdb')

customNetworkData={}
import json
import IP2Location, os, IP2Proxy

try:
	ip2p = IP2Proxy.IP2Proxy(os.path.join("data", "IP2PROXY-LITE-PX9.BIN"))
except FileNotFoundError as exc:
	raise FileNotFoundError("Missing data/IP2PROXY-LITE-PX9.BIN. See: https://www.ip2location.com/development-libraries/ip2location/python")

try:
	ip2l = IP2Location.IP2Location(os.path.join("data", "ip2location.bin"))
except FileNotFoundError as exc:
	raise FileNotFoundError("Missing data/ip2location.bin. See: https://www.ip2location.com/development-libraries/ip2location/python")
		


from data.amz import regionInfo as amzRegionInfo

with open('data/amazon_ip-ranges.json') as f:
	data = json.load(f)
	for prefix in data["prefixes"]:
		region=prefix["region"]
		rinfo=amzRegionInfo[region]
		customNetworkData[ipaddress.ip_network(prefix["ip_prefix"])]=tuple([region]+list(rinfo))

def country(ip):
	ip=ipaddress.ip_address(ip)
	
	for r,data in customNetworkData.items():
		if ip in r:
			return (data[1],data[2],data[3])
	try:
		response = citydb.city(ip)
	except: # Invalid IP verification?
		return (False,False,False,)
	return (response.country.iso_code,response.location.latitude,response.location.longitude)

import config
CGN=ipaddress.ip_network("100.64.0.0/10")
p1=ipaddress.ip_network("10.0.0.0/8")
def asn(ip):
	
	ip=ipaddress.ip_address(ip)
	
	if ip in config.homenetwork:
		return (-1,"HOME")
	if ip in p1:
		return (-2,"Private 10.x.x.x")
	if ip.is_private:
		return (-2,"Local Network")
	if ip in CGN:
		return (-3,"Carrier Grade NAT")

	try:
		response = asndb.asn(ip)

		for r,data in customNetworkData.items():
			if ip in r:
				return (response.autonomous_system_number,"Amazon "+data[0],)

	except:
		return (0,"ASN-UNKNOWN",)
	return (response.autonomous_system_number,response.autonomous_system_organization,)

if __name__ == "__main__":
	c=country("130.232.246.90")
	a=asn("130.232.246.90")
	amaze=country("35.180.0.0")
	ip2 = ip2p.get_all("35.180.0.0")
	ip3 = ip2l.get_all("35.180.0.0")
	import code; code.interact(local=locals())