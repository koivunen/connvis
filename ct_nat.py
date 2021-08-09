#!/usr/bin/env python3
from Conntrack import ConnectionManager, NFCT_O_XML
from lxml.etree import fromstring


def filter_nat(xml):
    d = fromstring(xml)
    orig_src = d.xpath("..//meta[@direction='original']/layer3/src/text()")[0]
    repl_dst = d.xpath("..//meta[@direction='reply']/layer3/dst/text()")[0]
    return orig_src != repl_dst


for i in ConnectionManager(NFCT_O_XML).list():
    if filter_nat(i):
        print(i)
