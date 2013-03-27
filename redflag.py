"""
    Mailgun Mailer
    --------------

    Send outgoing mail using requests, jutil, and mailgun.

"""

import requests

from jutil.decorators import constant
from jutil.environment import Deployment

MAILGUN_API_URL = unicode("https://api.mailgun.net/v2")
MAILGUN_MESSAGES_SUFFIX = unicode("messages")

_mailgun_api_key = None
_mailgun_domain = None
_default_name = unicode("")
_default_email = unicode("")
_new_comment_subject = unicode("A comment on task ")


class _Mail(object):

    """Mail constants for interacting with incoming mail from MailGun.

    http://documentation.mailgun.net/user_manual.html#receiving-messages

    """

    @constant
    def RECIPIENT(self):
        return "recipient"

    @constant
    def SENDER(self):
        return "sender"

    @constant
    def FROM(self):
        return "from"

    @constant
    def TO(self):
        return "to"

    @constant
    def SUBJECT(self):
        return "subject"

    @constant
    def BODY_TEXT(self):
        return "body-plain"

    @constant
    def BODY_HTML(self):
        return "body-html"

    @constant
    def BODY_TEXT_STRIPPED(self):
        return "stripped-text"

    @constant
    def BODY_HTML_STRIPPED(self):
        return "stripped-html"

    @constant
    def STRIPPED_SIGNATURE(self):
        return "stripped-signature"

    @constant
    def ATTACHMENT_COUNT(self):
        return "attachment-count"

    @constant
    def ATTACHMENT_X(self):
        return "attachment-x"

    @constant
    def TIMESTAMP(self):
        return "timestamp"

    @constant
    def TOKEN(self):
        return "token"

    @constant
    def SIGNATURE(self):
        return "signature"

    @constant
    def MESSAGE_HEADERS(self):
        return "message-headers"

    @constant
    def CONTENT_ID_MAP(self):
        return "content-id-map"

    @constant
    def TEXT(self):
        return "text"

    @constant
    def API(self):
        return "api"

MAIL = _Mail()


def initialize(api_key, domain, email, name=None):
    """Set the api key and domain for the mailgun account to use."""
    global _mailgun_api_key
    global _mailgun_domain
    global _default_name
    global _default_email

    _mailgun_api_key = api_key
    _mailgun_domain = domain
    _default_email = email
    if name:
        _default_name = name
    else:
        _default_name = _get_default_sender_name()


def send_comment_on_task(service, task_id, recipient, message):
    """Send an smtp email for a task using Mailgun's API.

    Parameters
    ----------
    service : str
    task_id : id
    recipient : str
        Formatted as "Name <email@domain.com>"
    message : str

    """
    from_email = unicode("{}-{}-comment@{}").format(
            service,
            task_id,
            _mailgun_domain)

    subject = unicode("{} {}.").format(_new_comment_subject, task_id)
    send_email_as_jack(
            from_email,
            recipient,
            subject,
            message)


def send_email_to_customer(customer, subject, body_text):
    """Send email to customer from Jackalope."""
    print 'customer', customer
    recipient = _format_email_with_name(customer.full_name, customer.email)
    return send_email_from_jack(recipient, subject, body_text)


def send_internal_email_from_service(service, id, subject, body_text):
    """Send internal email from a service."""
    recipient = unicode("{}-{}@{}").format(service, id, _mailgun_domain)
    return send_email_from_jack(recipient, subject, body_text)


def send_email_from_jack(recipient, subject, body):
    """Send a smtp email using Mailgun's API with 'Jack Lope' as the sender
    and return the response dict.

    Parameters
    ----------
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    return send_email(_get_default_sender(), recipient, subject, body)


def send_email_as_jack(sender_email, recipient, subject, body):
    """Send a smtp email using Mailgun's API with 'Jack Lope' as
    the name and the sender_email as the email, and return the response dict.

    Parameters
    ----------
    sender_email `str`
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    sender = _format_email_with_name(_default_name, sender_email)
    return send_email(sender, recipient, subject, body)


def send_email(sender, recipient, subject, body):
    """Send a smtp email using Mailgun's API and return the response dict.

    Parameters
    ----------
    sender : `str`
        Formatted as "Name <email@domain.com>"
    recipient : `str`
        Formatted as "Name <email@domain.com>"
    subject : `str`
    body : `str`

    """
    print 'send_email', sender, recipient, subject, body
    data_dict = {
            MAIL.FROM: sender,
            MAIL.TO: [recipient],
            MAIL.SUBJECT: subject,
            MAIL.TEXT: body
            }
    url = unicode("{}/{}/{}").format(
            MAILGUN_API_URL,
            _mailgun_domain,
            MAILGUN_MESSAGES_SUFFIX)
    response = requests.post(
            url,
            auth=(MAIL.API, _mailgun_api_key),
            data=data_dict)

    return response.text


def _get_default_sender():
    return _format_email_with_name(_default_name, _default_email)


def _format_email_with_name(name, email):
    return unicode("{} <{}>").format(name, email)


def _get_default_sender_name():
    name = ""

    if Deployment.is_prod():
        name = "Jack Lope"
    elif Deployment.is_staging():
        name = "Jack Staging"
    elif Deployment.is_dev():
        name = "Jack Dev"

    return unicode(name)
