from cStringIO import StringIO
import zipfile

from lxml import etree

def build_omex(storage):
    try:
        raw_manifest = storage.file('manifest.xml')
        locations = parse_manifest(raw_manifest)
    except PathNotFoundError:
        # XXX should raise a incompatible type.
        return None
    return _process(storage.file, locations)

def _process(getter, locations):
    stream = StringIO()
    zf = zipfile.ZipFile(stream, mode='w')
    for path in locations:
        try:
            contents = getter(path)
        except:
            # XXX figure out how to propagate this to users.
            continue
        znfo = zipfile.ZipInfo(path)
        znfo.file_size = len(contents)
        znfo.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(znfo, contents)
    zf.close()
    return stream.getvalue()

def parse_manifest(raw_manifest):
    et = etree.parse(StringIO(raw_manifest))
    raw = et.xpath('//o:omexManifest/o:content/@location', namespaces={
        'o': 'http://identifiers.org/combine.specifications/omex-manifest'
    })
    locations = []
    for r in raw:
        if r.startswith('./'):
            locations.append(r[2:])
            continue
        if r.startswith('http://') or r.startswith('https://'):
            # ignore external resources for now
            continue
        locations.append(r)

    # assert that 'manifest.xml' is included?
    return locations
