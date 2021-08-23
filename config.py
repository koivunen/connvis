import argparse
parser = argparse.ArgumentParser(prog="connvis",description='Web-based conntrack that tries to simplify the data for privacy research')
parser.add_argument('--nodnsseed', help='do not seed domains from dnsmasq history',action='store_true')
parser.add_argument('--shell', help='Enable interactive shell',action='store_true')
args = parser.parse_args()


import ipaddress

homenetwork = ipaddress.ip_network('192.168.0.0/24')
homenetwork_router = ipaddress.ip_address('192.168.0.1')
aggregate_google=True # That is a lot of domains
ignored_domains=["osoite.local"]