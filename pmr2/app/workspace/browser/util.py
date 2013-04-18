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

def fix_workspace_html_anchors(html, workspace_url, commit_id):
    """
    Fix up the anchors in an HTML file.

    Do this before calling safe_html.
    """

    parser = etree.HTMLParser()
    dom = etree.fromstring(html, parser)

    imgnodes = dom.xpath('.//img')
    for node in imgnodes:
        src = node.attrib.get('src')
        if not src:
            continue

        if not (src.startswith('/') or src.startswith('http://') or
                src.startswith('https://')):
            node.attrib['src'] = '/'.join([
                workspace_url, 'rawfile', commit_id, src])

    anchors = dom.xpath('.//a')
    for node in anchors:
        href = node.attrib.get('href')
        if not href:
            continue

        if not (href.startswith('/') or href.startswith('#') or
                href.startswith('http://') or href.startswith('https://')):
            node.attrib['href'] = '/'.join([
                workspace_url, 'file', commit_id, href])

    result = etree.tostring(dom, encoding='utf-8', method='html')
    return result
