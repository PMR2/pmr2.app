from random import getrandbits
import re
from lxml import etree

import zope.component

import pmr2.mercurial.utils

def set_xmlbase(xml, base):
    try:
        dom = etree.fromstring(xml)
    except:
        # silently aborting on invalid input.
        return xml
    dom.set('{http://www.w3.org/XML/1998/namespace}base', base)
    result = etree.tostring(dom, encoding='utf-8', xml_declaration=True)
    return result

def obfuscate(input):
    try:
        text = input.decode('utf8')
    except UnicodeDecodeError:
        text = input
    return ''.join(['&#%d;' % ord(c) for c in text])

def short(input):
    return pmr2.mercurial.utils.filter(input, 'short')

def isodate(input):
    return pmr2.mercurial.utils.filter(input, 'isodate')

re_simple_date = re.compile('^[0-9]{4}(-[0-9]{2}){0,2}')
def simple_valid_date(input):
    try:
        return re_simple_date.search(input)
    except:
        return False
