'''
Created on Jan 16, 2020

@author: fsells
'''

from django.core.mail import send_mail as django_send_mail
import datetime

from webapp import utilities
from webapp import email_notification_templates as templates
from webapp.constants import *
from django.conf import settings

TESTONLY_EMAIL_ADDRESSEES = ['frederick.sells@RiverSpringHealth.org', 
                             'Jonathan.Clark@riverspringhealth.org', 
                             'Antonique.Martin@riverspringhealth.org']

PRODUCTION_EMAIL_ADDRESSEES = ['censusnotification@hebrewhome.org']    

FROM_EMAIL_ADDRESS = 'no-reply@hebrewhome.org'

def get_recipients():
    if settings.DEBUG:
        return TESTONLY_EMAIL_ADDRESSEES
    else:
        return PRODUCTION_EMAIL_ADDRESSEES




def get_email_body(values):
    print (values.items())
    timestamp = values['timestamp']
    values['date'] = timestamp.strftime('%m/%d/%Y')
    values['time']= timestamp.strftime('%I:%M %p')
    template = templates.get_html_template(values['action'])
    body = template.format(**values)
    print (body)
    return body


def email_census_edit_notification(**values): 
    (subject, html) = templates.get_subject_and_body(values)
    subject = 'TESTING ONLY' + subject
    django_send_mail(
        subject = subject,
        message = 'plain text not supported',
        from_email = NO_REPLY,
        recipient_list = get_recipients(),
        fail_silently=False,
        html_message = html
    )
    return

def email_anything(subject, body ):
    print('sendint to', get_recipients())
    print(subject)
    print(body)
    django_send_mail(
        subject = 'TESTING '+subject,
        message = 'plain text not supported',
        from_email = NO_REPLY,
        # recipient_list = ['Frederick.Sells@riverspringhealth.org'], #get_recipients(),
        recipient_list = get_recipients(),
        fail_silently=False,
        html_message = body
        )
    return

