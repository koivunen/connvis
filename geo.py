import geoip2.database

citydb=geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')
asndb=geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-ASN.mmdb')

def country(ip):
	response = citydb.city(ip)
	return (response.country.iso_code,response.location.latitude,response.location.longitude)
def asn(ip):
	response = asndb.asn(ip)
	return (response.autonomous_system_number,response.autonomous_system_organization,)

if __name__ == "__main__":
	c=country("130.232.246.90")
	a=asn("130.232.246.90")
	import code; code.interact(local=locals())