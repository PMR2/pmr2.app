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
        contents = getter(path)
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
    locations = [r[2:] for r in raw if r.startswith('./')]
    # assert that 'manifest.xml' is included?
    return locations
