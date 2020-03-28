'''
Created on Jan 16, 2020

@author: fsells
'''

from django.core.mail import send_mail as django_send_mail
import datetime

from webapp import utilities
from webapp import email_notification_templates as templates
from webapp.constants import *

#  = 'Admission'
#  = 'Room Change' 
#  = 'Out to Hospital'
# RETURN_FROM_HOSPITAL = 'Return from Hospital'
#  = 'Out to Leave of Absence'
# RETURN_FROM_LEAVE_OF_ABSENCE ='Return from Leave of Absence'
#  = 'Discharge'
#  = 'Deceased'


#['firstname', 'lastname', 'date', 'time','oldloc', 'oldbed', 'dischargeto', 'admitfrom', 'newloc', 'newbed'],

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
        recipient_list = ['frederick.sells@riverspringhealth.org'],
        fail_silently=False,
        html_message = html
    )
    return


