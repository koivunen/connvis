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

#TODO
"""  File "/home/display/connvis/utils.py", line 26, in aggregateBigCompanies
    if config.aggregate_google and "google" in identifier.lower(): # gvt2.com gstatic.om doubleclick
AttributeError: 'NoneType' object has no attribute 'lower'
130.232.129.162 - - [20/Aug/2021 13:49:50] "GET /dnsbar.json HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 2088, in __call__
    return self.wsgi_app(environ, start_response)
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 2073, in wsgi_app
    response = self.handle_exception(e)
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 2070, in wsgi_app
    response = self.full_dispatch_request()
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 1515, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 1513, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 1499, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
  File "/home/display/connvis/vishttp.py", line 93, in dnsbar
    return jsonify(dnsBarProvider())
  File "/home/display/connvis/dnsvis.py", line 43, in provider
    shortdomain=utils.aggregateBigCompanies(shortdomain)
  File "/home/display/connvis/utils.py", line 26, in aggregateBigCompanies
    if config.aggregate_google and "google" in identifier.lower(): # gvt2.com gstatic.om doubleclick
AttributeError: 'NoneType' object has no attribute 'lower'
130.232.129.162 - - [20/Aug/2021 13:49:53] "GET /dnsbar.json HTTP/1.1" 500 -
Traceback (most recent call last):
  File "/usr/local/lib/python3.9/dist-packages/flask/app.py", line 2088, in __call__
  """
  
def aggregateBigCompanies(identifier,where=False):
	if not identifier: #TODO: ???
		return identifier

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

