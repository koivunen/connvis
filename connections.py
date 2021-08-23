#!/usr/bin/env python3


from xml.etree.ElementTree import XML
import xml.dom.minidom
import queue
from queue import Full
import ipaddress
from multiprocessing import Process, Queue, process
from Conntrack import ConnectionManager
import time
cm = ConnectionManager()
from config import homenetwork,homenetwork_router
homenetwork_broadcast = homenetwork.broadcast_address
import threading,pprint

#TODO: Thread safety for other than conns in a saner way

conns={}
conns_mainthread = {}
conns_lock = threading.Lock()
conns_dirty = True
activeIPs={}
ipByteTable={}
ipPacketTable={}
queue=Queue(2)
def getHomeIPFromConnection(conn):
	"""
	Return source or destination if either one is in home network
	"""
	src = conn.get("src")
	if src and src in homenetwork and src!=homenetwork_broadcast:
		return src
	dst = conn.get("dst")
	if dst and dst in homenetwork and dst!=homenetwork_broadcast:
		return dst


def getConnections():
	"""
	Returns connections list:
	Dict of 'conntrackid': {'bytes': '2519',
               'bytesIn': '8445',
               'dport': '443',
               'dst': IPv4Address('1.2.3.4'),
               'gone': False,							# Timestamp when the connection was purged from conntrack
               'id': '623806457',						# conntrackid
               'lastActivity': 1628534811.1428092,		# last packet received/sent
               'packets': '12',
               'packetsIn': '7',
               'protoname': 'tcp',
               'sport': '45012',
               'src': IPv4Address('192.168.0.142'),
               'state': 'ESTABLISHED'}					# if tcp connection, shows conntrack state
	"""
	
	global conns_dirty,conns_mainthread
	
	# TODO: cleanup!!!
	#assert threading.current_thread() is threading.main_thread()
	
	if conns_dirty:
		conns_dirty=False
		with conns_lock:
			conns_mainthread=dict(conns) # GIL cannot yield in a dict copy
			
	return conns_mainthread


def getIPActivity():
	return activeIPs

def getIPByteTable():
	#TODO
	return ipByteTable
def getIPPacketTable():
	return ipPacketTable


def getIPConnections():
	res={}
	for con in conns:
		if con["gone"]:
			continue
		res[con["src"]]

def doDiff(conn,vals):
	if conn["packets"]!=vals["packets"] or conn["packetsIn"]!=vals["packetsIn"]:
		now=time.time()
		vals["lastActivity"]=now
		src=conn["src"]
		activeIPs[src]=now
		activeIPs[conn["dst"]]=now
		added=vals["packets"]-conn["packets"]
		if added<0:
			print("negative packet count (",added,") on",src,conn["dst"])
			pprint.pprint(vals)
			pprint.pprint(conn)
			added=0

		ipPacketTable[src]=ipPacketTable.get(src,0)+added

def isHomeDNSConnection(conn):
	if conn.get("dport")!=53 and conn.get("sport")!=53:
		return False

	src = conn.get("src")
	dst = conn.get("dst")

	if not src or src not in homenetwork or not dst or dst not in homenetwork:
		return False
	
	return True

def processEntryTable(t):
	updateConns=[]
	for vals in t:
		src = vals.get("src")
		dst = vals.get("dst")
		homeip = getHomeIPFromConnection(vals)
		if homeip and not isHomeDNSConnection(vals):
			id = vals["id"]
			updateConns.append(id)

			# Existing, update
			if id in conns:
				conn=conns[id]
				doDiff(conn,vals)
				for k,v in vals.items():
					conn[k]=v
				vals=conn
				vals["gone"]=False					
			else: # New, initialie
				now = time.time()
				vals["gone"]=False
				vals["lastActivity"]=now
				with conns_lock:
					conns[id]=vals
					activeIPs[src]=now
					activeIPs[dst]=now

	for id,conn in conns.items():
		if id not in updateConns and not conn["gone"]:
			conn["gone"]=time.time()
	global conns_dirty
	conns_dirty=True

def receiver():
	try:
		while True:
			t=queue.get()
			processEntryTable(t)
	except KeyboardInterrupt as e:
		return
def processCMList():
	"processes the connection manager list and puts it up to queue further processing"
	try:
		ret=[]
		for msg in cm.list():
			#dom = xml.dom.minidom.parseString(msg)
			#pretty_xml_as_string = dom.toprettyxml()

			#print(pretty_xml_as_string)
			msg=XML(msg)
			#import code; code.interact(local=locals())
			vals=parse(msg)
			ret.append(vals)
		try:
			queue.put(ret,True,1)
		except Full as e:
			print("processCMList being consumed too slow")
			return # We will try soon again
	except:
		raise #TODO: ??? what does ConnectionManager raise and when
	


def _find(msg,path,toint=False):
	ret = msg.find(path)
	#import code; code.interact(local=locals())
	if ret is not None:
		if toint:
			return int(ret.text)
		return ret.text

# example xml from conntrack
"""<?xml version="1.0" ?>
<flow type="update">
		<meta direction="original">
				<layer3 protonum="2" protoname="ipv4">
						<src>192.168.0.142</src>
						<dst>123.58.123.123</dst>
				</layer3>
				<layer4 protonum="6" protoname="tcp">
						<sport>33245</sport>
						<dport>443</dport>
				</layer4>
				<counters>
						<packets>16</packets>
						<bytes>10075</bytes>
				</counters>
		</meta>
		<meta direction="reply">
				<layer3 protonum="2" protoname="ipv4">
						<src>123.58.123.123</src>
						<dst>10.0.7.71</dst>
				</layer3>
				<layer4 protonum="6" protoname="tcp">
						<sport>443</sport>
						<dport>33245</dport>
				</layer4>
				<counters>
						<packets>13</packets>
						<bytes>6516</bytes>
				</counters>
		</meta>
		<meta direction="independent">
				<state>ESTABLISHED</state>
				<timeout>431952</timeout>
				<mark>0</mark>
				<use>1</use>
				<id>2759672141</id>
				<assured/>
		</meta>
		<when>
				<hour>16</hour>
				<min>01</min>
				<sec>46</sec>
				<wday>2</wday>
				<day>9</day>
				<month>8</month>
				<year>2021</year>
		</when>
</flow>"""

def parse(msg):

	ret = {
		"src": 			_find(msg,'./meta[@direction="original"]/layer3/src'),
		"dst": 			_find(msg,'./meta[@direction="original"]/layer3/dst'),
		"sport": 		_find(msg,'./meta[@direction="original"]/layer4/sport',True),
		"dport": 		_find(msg,'./meta[@direction="original"]/layer4/dport',True),
		"protoname": 	msg.find('./meta[@direction="original"]/layer4').get('protoname'),
		"packets": 		_find(msg,'./meta[@direction="original"]/counters/packets',True),
		"bytes": 		_find(msg,'./meta[@direction="original"]/counters/bytes',True),
		"packetsIn": 	_find(msg,'./meta[@direction="reply"]/counters/packets',True),
		"bytesIn": 		_find(msg,'./meta[@direction="reply"]/counters/bytes',True),
		"id": 			_find(msg,'./meta[@direction="independent"]/id',True),
		"state":		_find(msg,'./meta[@direction="independent"]/state'),
	}
	src = ret.get("src")
	if src:
		ret["src"]=ipaddress.ip_address(src) 
	dst = ret.get("dst")
	if dst:
		ret["dst"]=ipaddress.ip_address(dst)


	return ret


def reader():
	try:
		while True:
			processCMList()
			time.sleep(0.9)
	except KeyboardInterrupt as e:
		return


from multiprocessing import Process
def start_tracking():
	global receiver_thread,connection_thread
	connection_thread = Process(name="connectionthread",target=reader, daemon=True)
	connection_thread.start()

	receiver_thread = threading.Thread(name='connectionrecvthread', target=receiver, daemon=True)
	receiver_thread.start()

	

if __name__ == "__main__":
	from tabulate import tabulate
	start_tracking()
	while True:
		import pprint
		time.sleep(3.9)
		print("\n\n")
		pprint.pprint(getConnections())
		break
		hdrs=next(iter( getConnections().items() ))[1].keys()
		rows=[r.values() for id,r in getConnections().items()]
		print(tabulate(rows,headers=hdrs,floatfmt=".0f"))
		
		print("\n")
		rows=[]
		hdrs=["ip","seconds"]
		for ip,last in getIPActivity().items():
			if ip in homenetwork:
				rows.append([ip,int(time.time()-last)])
		print(tabulate(rows,headers=hdrs,floatfmt=".0f"))