#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# CuteSpider
#               -- Keep it cute, stupid
#
# Test domain parsers in `extract_templates` dir.
#
#--------------------------------------------------------------
#
# Date:     2013-01-14
#
# Author:   gewu@baidu.com
#
#

import os
import re
import sys
import imp
import urllib2
import zlib
import random
import urlparse
import urllib 
import chardet
from simhash import Simhash

from web_discovery_tools import Web_Discovery_Tools 
from ChinaCities import ChinaCities
#--------------------------------------------------------------
# Global Constants & Vars
#--------------------------------------------------------------
USER_AGENTS = {
        # Chrome, Firefox, Opera etc.
        "modern": [
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8) AppleWebKit/536.25 (KHTML, like Gecko) Version/6.0 Safari/536.25",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.60 Safari/537.1",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.109 Safari/535.1"
                ],
        # IE agents
        "ie": [
                "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727) IE 7.0 WinXP 32-bit",
                "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; FunWebProducts; .NET CLR 1.1.4322; PeoplePal 6.2)",
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
                ]
}

d_map = {
         " ":"",
         "\t":"",
         "\n":"",
         "\r":"",
         "　":""
}
#--------------------------------------------------------------
# Funcs
#--------------------------------------------------------------

def fetchContent(url, method="GET"):
    headers = makePseudoHeaders(url)
    if method.upper() == 'POST': # POST request
        real_request_url = url
        post_params = {}
        if '?' in url: # Hack! Parse GET params, use them as form data
            # If you've got a easier & faster way to do this! You must be a genius!
            o = urlparse.urlparse(url)
            post_params = urlparse.parse_qsl(o.query)
            if ('c_s_kp', '1') not in post_params:# c_s_kp(KEEP_PARAMS) not in url, don't keep params in GET url
                real_request_url = url.split('?', 1)[0] # strip query & fragment
        else:
            post_params['c_s'] = 1 # fake post data
        post_data = urllib.urlencode(post_params)
        req = urllib2.Request(real_request_url, post_data, headers)
    else: # GET request
        req = urllib2.Request(url, None, headers)
    try:
        '''
        proxy = urllib2.ProxyHandler({"http": "59.78.160.244:8080"})
        opener = urllib2.build_opener(proxy)
        res = opener.open(req, timeout=30)
        '''
        res = urllib2.urlopen(req)
        content = res.read()
        code = res.getcode()

    # decode gzipped content if needed
        content_encoding = res.info().getheader('Content-Encoding')
        if content_encoding == 'gzip':
            content = zlib.decompress(content, 16+zlib.MAX_WBITS)
    except:
        print "download fail '%s'" % url
        return None, -1 # fail
    return content, code # success

def makePseudoHeaders(url):
    headers = {
            "User-Agent": makePseudoUserAgent(),
            #"User-Agent":"",
            "Referer": makePseudoReferer(url),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "utf-8,gb2312,GBK;q=0.7,*;q=0.3",
            # I don't need gzip
            #"Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Language":"zh-CN,en-US;q=0.8,en;q=0.6",
            "Cookie": "SUB=_2AkMjqKkfdcNhrAJYnPEXzGjhbIpVn1m3_dTxNU6sQH5SdXVRj1EKqCRotBN-XN2j2jPesFF0PBB-Q4FLNIx_5De4OR-DVtVLjg..; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WWc7FAVWyvVazrpDWxQLN._5JpV2JHyMNBEeh-7BsU_qgLjTJSadBtt;",
            #"Cookie": "TurnAD23=visit:1; TurnAD475=visit:2; TurnAD476=visit:2; TurnAD477=visit:1; TurnAD20=visit:1; TurnAD472=visit:1; TurnAD473=visit:1; TurnAD474=visit:1; TurnAD143=visit:2; TurnAD478=visit:2; TurnAD479=visit:2; TurnAD480=visit:2; vjuids=-d802f8508.149a1abfbbb.0.8dfb5737; cyan_uv=C66D949F78F00001501C38C516001543; ag_fid=BmbTLmCJTGovtHdA; sci12=w:1; IPLOC=CN1100; SUV=1411120944032951; networkmp_del=check:1; beans_dmp_1411120944032951=1433236926415; gn11=w:1; gn12=w:1; POPAD2=visit:1; COOKIEMAPPING1=suv:1411120944032951; gj11=w:1; gj12=w:1; TurnAD593=visit:3; TurnAD123=visit:2; TurnAD457=visit:2; ad_D=visit:2; TurnAD269=visit:1; TurnAD742=visit:2; TurnAD260210j3=visit:2; TurnAD268=visit:1; TurnAD589=visit:1; TurnAD267=visit:1; TurnAD588=visit:3; TurnAD266=visit:2; TurnAD587=visit:1; TurnAD265=visit:3; TurnAD264=visit:1; shh11=w:1; shenhui12=w:1; vjlast=1415756643.1433297018.11; sohutag=8HsmeSc5NSwmcyc5NCwmYjc5NywmYSc5NSwmZjc5NCwmZyc5NCwmbjc5NTYsJ2kmOiNsJ3cmOiAsJ2gmOiAsJ2NmOiAsJ2UmOiAsJ20mOiEsJ3QmOiB9; beans_new_turn=%7B%22news-index%22%3A42%2C%22guonei-article%22%3A52%2C%22guoji-article%22%3A45%2C%22social-article%22%3A30%7D",
            }
    return headers

def makePseudoReferer(url=""):
    if url and url.startswith('http') and '://' in url:
        tmp = url.split('//')[1].split('/')[0]
        return "http://%s/" % tmp
    return "http://www.google.com/"

def makePseudoUserAgent():
    if random.random() > 0.5:
        user_agent = random.choice(USER_AGENTS["modern"])
    else:
        user_agent = random.choice(USER_AGENTS["ie"])
    
    # DEBUG iPhone 4
    #user_agent = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5'
    #user_agent = 'curl/7.12.1 (x86_64-redhat-linux-gnu) libcurl/7.12.1 OpenSSL/0.9.7a zlib/1.2.1.2 libidn/0.5.6'
    return user_agent

def parse(url, download_method="GET"):
    content, _ = fetchContent(url, download_method)
    if content:
        return content
    else:
        print "Download fail, sigh!\nquit"

def parseNews(content, url):
    cc = ChinaCities() 
    contentCode = chardet.detect(content)['encoding']
    if "GB" in contentCode or "gb" in contentCode: 
        content = content.decode("gbk", 'ignore').encode("utf-8")

    #infos['web_discovery'] = []
    timestamp = Web_Discovery_Tools.get_date(content)
    title = Web_Discovery_Tools.get_title(content)
    content = Web_Discovery_Tools.get_content(content)
    content = Web_Discovery_Tools.multi_replace(content, d_map)

    city = cc.guessCity(title)
    if city == "":
        city = cc.guessCity(content)
    province = cc.getProvince(city)
    simhash = Simhash(content.decode("utf-8")).value
    item = (timestamp, province, city, content, url, simhash, title)
    return item

    '''
    self.infos['web_discovery'].append( item )
    return self.infos, self.links
    '''

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "No URL specified"
        print "  e.g. python %s 'http://www.google.com/' [POST|GET]" % __file__
    elif len(sys.argv) == 2:
        content = parse(sys.argv[1])
        content = Web_Discovery_Tools.encodeUTF8(content)
        #result = parseNews(content, sys.argv[1])

        date = Web_Discovery_Tools.get_date(content)
        print "date: ", date
        
        title = Web_Discovery_Tools.get_title(content)
        print "title: ", title

        m = Web_Discovery_Tools.get_content(content)
        m = m[:m.find("http")]
        print "content: "
        print m
    else:
        download_method = 'POST' if sys.argv[2].upper() == 'POST' else 'GET'
        parse(sys.argv[1], download_method)
    

