#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# IntelUniq
#               -- Intelligence shall be unique 
#
# web_discovery_tools.py: #TODO DESC HERE
#
#--------------------------------------------------------------
#
# Date:     2015-06-02
#
# Author:   gewu@baidu.com
#
#

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------

#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------

import re
import chardet
from chardet.universaldetector import UniversalDetector

class Web_Discovery_Tools(object):
    @classmethod
    def __init__(self):
        pass

    @classmethod
    def get_re_result(self, pat_item, page):
        ret_tmp = pat_item.search(page)
        ret = ""
        if ret_tmp is not None:
            ret = ret_tmp.group(1)
        return ret

    @classmethod
    def multi_replace(self, text , d):
        rx = re.compile("|".join(d.keys()))
        def one_xlat(match):
            return d[match.group(0)]
        return rx.sub(one_xlat, text)

    @classmethod
    def rm_html(self, text):
        re_h = re.compile("</?\w+[^>]*>")
        return re_h.sub("", text)

    @classmethod
    def get_body(self, text):
        ret = text[text.find('<body'):text.rfind('</body>')]
        if ret == "":
            ret = text[text.find('<BODY'):text.rfind('</BODY>')]
        return ret

    @classmethod
    def tag_filter(self, text):
        re_a = re.compile("</a>")
        text = re_a.sub("</a>\n\n\n\n\n", text)   #reduce disturb of the href's description

        re_replace = re.compile(r'<(script|SCRIPT).*?>.*?</(script|SCRIPT)>|'        #filter html tag
                                r'<!.*?-->|<style.*?>.*?</style>|</?\w+[^>]*>', re.DOTALL)
        text = re_replace.sub("", text)

        return text

    @classmethod
    def get_title(self, text):
        re_t = re.compile(r"<h1[^>]*>([^<]+?)</h1>")
        re_h = re.compile(r"<title[^>]*>([^<]+?)</title>")

        match = re_t.search(text)
        if match is None:
            match = re_h.search(text)
            if match is None:
                return ""
        return match.group(1).strip()

    @classmethod
    def get_date(self, text):
        re_d = re.compile(r"\d{4}年\d{1,2}月\d{1,2}日\s*(\d{2}:\d{2})*|\d{4}[\-/]\d{1,2}[\-/]\d{1,2}\s*(\d{1,2}:\d{1,2}|<)")
        ret = re_d.search(text)
        if ret is None:
            return ""
        return ret.group().strip().rstrip("<")

    @classmethod
    def encodeUTF8(self, text):
        ret = ""
        re_c = re.compile(r'<meta[^>]*?charset=(.*?)>')
        match = re_c.search(text)
        
        if match:
            ret = match.group(1)
        else:
            ret = chardet.detect(text)['encoding']
        if "utf" in ret or "UTF" in ret:
            try:
                text.decode("utf-8", "igonre")
            except:
                text = text.decode("gbk", 'ignore').encode("utf-8")
        if "gb" in ret or "GB" in ret:
            text = text.decode("gbk", 'ignore').encode("utf-8")
        return text;
    
    @classmethod
    def get_content(self, text):
        text = self.tag_filter(self.get_body(text))
        lines = text.split("\n")
        lines[:] = [m.strip() for m in lines]

        depth = 4
        content = []
        '''
        for line in lines:
            print "%s, %s" % (len(line), line) 
        return 0
        '''
        j = 0
        preTextLen = 0
        textBeginLen = 180
        headLen = 10
        endLen = 25
        nextTextLen = 200

        while j < depth and j < len(lines):
            preTextLen += len(lines[j])
            j += 1

        i = depth
        while i < len(lines):
            preTextLen += len(lines[i])
            if preTextLen > textBeginLen: 
                j = i           # find start
                while j > 1:
                    if len(lines[j]) < headLen and len(lines[j-1]) < headLen:
                        break
                    j -= 1

                k = i+1          # find end
                endflag = 0
                while k < len(lines) - endLen:
                    if len(lines[k]) < endLen and len(lines[k+1]) < endLen:
                        endflag = True
                        for m in range(1,endLen):
                            if len(lines[k+m]) > nextTextLen:      #next 20 lines length < 100
                                endflag = False
                                break
                    if endflag:
                        break
                    k += 1

                content = lines[j:k+1]
                return "".join(content)
            else:
                preTextLen -= len(lines[i-depth])
            i += 1
        
        ret = lines[0]               #return the longest line
        for l in lines:
            if len(l) > len(ret):
                ret = l
        return ret
        #'''

if __name__ == "__main__":
    pass
