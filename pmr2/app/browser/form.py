import zope.component
import z3c.form.form
from plone.i18n.normalizer.interfaces import IIDNormalizer


class AddForm(z3c.form.form.AddForm):
    """\
    Generic AddForm for the creation of classes in pmr2.app.  Since most
    objects share a similar interface, the process for creating them
    generally follows/fits into this pattern as defined by the methods
    below.

    For data assignment of fields and other custom work, redefine the
    method 'add_data'
    """

    # set clsobj to the object to be created.
    clsobj = None

    def create(self, data):
        """\
        The generic create method.
        """

        if self.clsobj is None:
            raise TypeError('`clsobj` need to be defined')
        id_ = data['title']
        id_ = zope.component.queryUtility(IIDNormalizer).normalize(id_)
        self._name = id_
        self._data = data
        return self.clsobj(self._name, **data)

    def add(self, obj):
        """\
        The generic add method.
        """

        # add the object to context and retrieve it
        self.context[self._name] = obj
        ctxobj = self.context[self._name]

        # assign data
        self.add_data(ctxobj)

        # do what CMFCore does while finishing construction. 
        # insert it into the workflows and reindex
        ctxobj.notifyWorkflowCreated()
        ctxobj.reindexObject()

        self.post_add(ctxobj)
        
    def add_data(self, obj):
        """\
        Generally this format should work:
        obj.title = self._data['title']
        """

        # it would be nice if the data assignment can happen without
        # explicit declaration.
        raise NotImplementedError

    def post_add(self, obj):
        """\
        If needed, extra actions taken can be defined here.
        """
        pass

    def nextURL(self):
        """\
        Generally this is desirable.
        """
        return "%s/%s" % (self.context.absolute_url(), self._name)


class EditForm(z3c.form.form.EditForm):
    """\
    Standard z3c EditForm.
    """
