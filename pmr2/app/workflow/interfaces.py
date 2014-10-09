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

    subject_template = zope.schema.TextLine(
        title=u'Workflow Notification Subject',
        description=u'Subject line for the workflow notification email.  A '
            'few tokens are available: \n'
            '{event} - The event object. '
                'Try to use {event.transition.new_state_id}.\n'
            '{obj} - The object that has its workflow changed.\n'
                'Try to use {obj.portal_type}.\n'
            '{obj_url} - The URL of the object.\n'
            '{portal_url} - The URL of the site.\n'
            '{title_or_id} - The title or ID of the object.\n'
            'Take care to ensure the attributes are available.',
        required=True,
        default=u'{obj.portal_type} `{title_or_id}` is now '
                 '{event.transition.new_state_id}',
    )

    message_template = zope.schema.Text(
        title=u'Workflow Notification Message Template',
        description=u'The message.  See formatting rules for subject.',
        required=True,
        default=u'Visit {obj_url} for more details.',
    )
