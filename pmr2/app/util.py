# a list of known processor and the content type to use.
known_processors = {
    'pmr2_processor_legacy_tmpdoc2html': {
        'ext': '.doc.html',
        'class': 'ExposureDocument',
    },
    'pmr2_processor_legacy_cellml2html_mathml': {
        'ext': '.cellml.html',
        'class': 'ExposureMathDocument',
    },
}

# default, no processor
no_processor = {
    'ext': '.html',
    'clsobj': 'ExposureDocument',
}

def ExposureDocGenerator(data):
    # XXX be dumb for now.  no default values.  auto failure
    import pmr2.app.content
    processor = known_processors.get(data['transform'])
    klass = getattr(pmr2.app.content, processor['class'])
    name = data['filename'] + processor['ext']
    return klass(oid=name)
