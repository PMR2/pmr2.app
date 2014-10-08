import zope.interface
import zope.schema


class ISettings(zope.interface.Interface):

    wf_change_recipient = zope.schema.TextLine(
        title=u'Workflow Notification Email Address',
        description=u'The email address to use as the recipient for PMR2 '
                     'workflow state changes, if enabled.',
        required=False,
    )

    wf_send_email = zope.schema.Bool(
        title=u'Send email on workflow state change.',
        required=False,
    )

    wf_change_states = zope.schema.List(
        title=u'Workflow states to notify',
        description=u'Workflow states that require an email to be sent, '
                     'one per line.',
        required=False,
        value_type=zope.schema.TextLine(),
    )
