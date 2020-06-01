'''
Created on Feb 27, 2020
The purpose of this module is to send emails to a specified distribution list
for all residents where the inbed status is blank or is no and the reason is blank.

@author: fsells
'''

import sys, os, datetime

from django.core.management.base import BaseCommand, CommandError


from webapp.constants import *
from webapp import logic_census as logic
from webapp import email_sender
from django.conf import settings

HTML_WRAPPER = '''<meta http-equiv="Content-Type" content="text/html; charset=us-ascii">
                    <h3>Incomplete/Error in Nightly Bed Check</h3>
                    <table border="1"><tbody>
                    {}
                    </tbody></table>'''

def TR(tds, htmlclass=None):
    text = ' '.join(tds)
    return '<tr>{}</tr>'.format(text or '')

def TH(text):
    return '<th>{}</th>'.format(text or '')

def TD(text):
    return '<td>{}</td>'.format(text or '')

class Command(BaseCommand):
    help = 'Sends Warnings of errors in NightlyBedcheck data'

    def add_arguments(self, parser):
        parser.add_argument('--testonly', action= 'store_true', help = 'print info only, dont send', default=False)
        
    def format_email_body(self, errors):
        header = 'Unit	RepDate	Room	ResidentName	Status	LevelOfCare	Gender	CurrentAdmitDate	Inbed	Reason	Comments'.split()
        rows = [TR([TH(x) for x in header])]
        for error in errors:
            tr =TR( [TD(error[key]) for key in header] )
            rows.append(tr)
        # for row in rows: print('\n', type(row), row)
        return HTML_WRAPPER.format( '\n'.join(rows) )

    def send_email(self, errors, timetext):
        if errors:
            body=self.format_email_body(errors)
            subject = '{} {} errors reported at {}'.format(settings.EMAIL_SUBJECT_PREFIX, len(errors),  timetext)
        else:
            body=HTML_WRAPPER.format('''<h1>Don't Worry, Be Happy there are no errors reported</H1>''')
            subject = '{} No errors reported at {}'.format(EMAIL_SUBJECT_PREFIX, timetext )  
        email_sender.email_anything(settings.CENSUS_RECIPIENTS, subject, body)

    def handle(self, *args, **options):
        # print('options', options)
        errors = logic.get_errors() 
        now = datetime.datetime.now().strftime('%x %X')
        self.send_email(errors, now)
        # print (subject)
        # print(body)
        # # print('done')
        # print('done')
        
            
            
    
        