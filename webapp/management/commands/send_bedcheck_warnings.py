'''
Created on Feb 27, 2020

@author: fsells
'''
'''
Created on Jul 10, 2019

@author: fsells
'''
import sys, os, datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail as django_send_mail



from webapp.constants import *


class Command(BaseCommand):
    help = 'Sends Warnings of errors in PositiveCensusReport (bedcheck) data'

    def add_arguments(self, parser):
        parser.add_argument('--testonly', action= 'store_true', help = 'print info only, dont send', default=False)
        
   
                


    def handle(self, *args, **options):
        print('options', options)
        testonly = options['testonly']        

        print('done', testonly)
        
            
            
            
        