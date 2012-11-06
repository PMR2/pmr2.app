from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from pmr2.z3cform import page

from pmr2.app.exposure.browser.templates import path


class ExposureCreateInterceptPage(page.SimplePage):
    """\
    Direct users to the proper way to create exposures.
    """

    label = u'Create Exposure'
    template = ViewPageTemplateFile(path('exposure_create.pt'))
