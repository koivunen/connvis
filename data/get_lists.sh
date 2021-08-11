curl "https://pgl.yoyo.org/adservers/iplist.php?ipformat=iptables&showintro=0&mimetype=plaintext" | grep OUTPUT | while read a b c d e f ip _ _ _ domain;do echo $ip $domain;done > ads.txt
curl "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext" | grep 127.0. | while read _ domain;do echo $domain;done > ads_domainsonly.txt
curl "https://someonewhocares.org/hosts/zero/hosts" | grep -v '^#' | grep .0.0. | while read ip domain;do echo $domain;done >> ads_domainsonly.txt
whois -h whois.radb.net -- '-i origin AS32934' | grep ^route: | while read a b;do echo $b;done > facebook_cidrs.txt
whois -h whois.radb.net -- '-i origin AS15169' | grep ^route: | while read a b;do echo $b;done > google_cidrs.txt
curl https://blocklistproject.github.io/Lists/tiktok.txt | grep -v '^#' | while read a domain wtf;do echo $domain;done > tiktok_domains.txt
massdns -t A -w tiktok_massdns.txt tiktok_domains.txt  -c 5 -r resolvers.txt
cat tiktok_massdns.txt | grep " IN A " | while read domain _ _ _ ip;do echo $domain $ip;done > tiktok_resolved.txt
wget https://ip-ranges.amazonaws.com/ip-ranges.json -O amazon_ip-ranges.json
