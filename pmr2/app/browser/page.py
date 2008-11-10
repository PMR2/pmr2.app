from plone.app.z3cform import layout


class Simple(layout.FormWrapper):
    """\
    A simple view generator/page/template wrapper.  Inherited directly 
    from layout.FormWrapper, as its default registered adapters does 
    everything needed for basic content.
    """

    template = None

    def contents(self):
        if self.template:
            return self.template()
        # XXX use better exception type
        raise ValueError('template need to be specified')

    def label(self):
        # override if necessary.
        return self.context.title_or_id()

