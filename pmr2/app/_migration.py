import traceback
from logging import getLogger
logger = getLogger('pmr2.app.migration')

import zope.component


def file_docgen_to_annotation(file):
    annotation = zope.component.queryAdapter(file, name='docgen')
    if not annotation:
        logger.error('Could not adapt to docgen for %s' % file)
        return None

    # annotation.source = file.docview_gensource
    # annotation.generator = file.docview_generator

    # XXX workaround some acquistion flustercuck....
    annotation.__class__.source.__set__(annotation, file.docview_gensource)
    annotation.__class__.generator.__set__(annotation, file.docview_generator)

    if file.views:
        if u'docgen' not in file.views:
            file.views = [u'docgen'] + file.views
    else:
        file.views = [u'docgen']
