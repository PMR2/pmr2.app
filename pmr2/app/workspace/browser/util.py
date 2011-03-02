from lxml import etree

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
