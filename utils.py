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