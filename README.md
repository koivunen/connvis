# connvis
**WiFi device connections visualizer for those that do not have a networking degree. Where is your data flowing to?**

## Video (outdated)
_connvis_ has two views: (1) sankey diagram of WiFi device connection targets and (2) geographical view and activity of targets.

https://user-images.githubusercontent.com/17916033/129107782-a43c23a0-9e7c-40d7-b7ea-e047d64dde0d.mov


## Usage (for end user)
Connect device(s) to the WiFi network made for connvis and start experimenting.  
 Connvis is even more fun with friends (supports and is actually designed for multiple devices being used in parallel)!

**TLDR**: Basically [conntrack](https://blog.cloudflare.com/conntrack-tales-one-thousand-and-one-flows/), but it tries to not show IP-addresses (_or ports because everything is 443 or proprietary_), but instead it tries to show some other still useful info related to the connections.

## Requirements
 - conntrack kernel module (also `echo 1 > /proc/sys/net/netfilter/nf_conntrack_acct`)
 - dnsmasq
   - systemd (for dnsmasq journal)
 - hostapd
 - python3.9

## Usage
1. Become a WiFi router `apt-get install dnsmasq hostapd`, enable forwarding, etc.
2. Install dependencies 

       apt-get install python3-pip whois python3-gi
       pip3 install -r requirements.txt
       
4. Download required files to data folder
5. Run `python3 main.py` and open the browser.
6. Follow end user usage



```bash

apt-get install python3-pip whois python3-gi
pip3 install -r requirements.txt
```

## TODO
 - [ ] Per device view of activity / bandwidth
 - [ ] New view: Per device domain resolves alone view
 - [ ] Sankey connection freshness coloring
 - [ ] Better purge of expired connections instead of instant disappearing
 - [ ] Priority sorting domains that an IP has based on: dnsmasq latest resolved domains
 - [ ] Display which domains an IP had resolved during the session
 - [ ] Geovisualization show device count without popup on hotspots
 - [ ] Improve hotspot visualization (labels are overlapping easily)
 - [ ] Code cleanup
 - [ ] Extra connection classification: file downloads (long connection and lots of bytes) or something else
 - [ ] TLS SNI sniffing?
 - [ ] Real time audible clicking of packets per second

## Used sources

Blocklists by https://pgl.yoyo.org/adservers/ and https://someonewhocares.org and https://blocklistproject.github.io


Geolocation data provided by https://MaxMind.com and https://lite.ip2location.com ( This site or product includes IP2Location LITE data available from https://lite.ip2location.com ).


## Copyright

MIT

## Acknowledgements

The authors gratefully acknowledge the funding provided by [IDA](https://www.dataintimacy.fi/en/) for the development of the software. The software was developed under the [Software Engineering](https://soft.utu.fi) Laboratory of Department of Computing in University of Turku. 
