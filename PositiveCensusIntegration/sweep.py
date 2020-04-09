'''
Created on Jul 10, 2019

@author: fsells
'''
import datetime
import random
from django.core.management.base import BaseCommand, CommandError

from webapp  import models

from . import mydata_api 
from . import local_db_api

class Command(BaseCommand):
    help = 'copies data from MatrixCare to local DB'

    def add_arguments(self, parser):
        parser.add_argument('--start', action= 'store', help = 'first day of sweep mm/dd/yyyy, for testing',
                            type=lambda s: datetime.datetime.strptime(s, '%m/%d/%Y'),
                            default = datetime.date.today())
        parser.add_argument('--days', action= 'store', help = 'number of days for sweep, for testing', default=1, type=int)
        parser.add_argument('--fakeinput', action= 'store_true', help = 'create fake user entry for testing', default=False)
        
    def fake_user_input(self, hhdb, nos=0, blanks=0):
        hhdb.mark_current_inbed_yes()
        if blanks==0 and nos==0: return 
        beds = models.BedCheck.objects.filter(Obsolete=0).order_by('unit', 'room', 'bed')
        for i, bed in enumerate(beds):
            print (i, bed)
            if i < nos:
                bed.inbed='No'
                bed.reason = random.choice(models.REASON_CHOICES)[0]
                bed.updatedby = 'fredtesting'
                bed.updatetime=datetime.datetime.now()
                bed.save()
            elif i < nos+blanks:
                bed.updatedby = 'fredtesting'
                bed.updatetime=datetime.datetime.now()
                bed.inbed = ''
                bed.save()
            else:
                break
                
        

    def handle(self, *args, **options):
        fake_input = options['fakeinput']
        print ('fakeit', fake_input)
        mydata = mydata_api.MyDataQueryManager()
        hhdb = local_db_api.HHDB()
        firstday =  options['start'] 
        ndays = options['days']
        almost_midnight = ' 11:45:00 PM'
        for n in range(ndays):
            sweeptime = firstday + datetime.timedelta(days=n)
            texttime = sweeptime.strftime('%m/%d/%Y') + almost_midnight
            beds = mydata.get_beds_x_patients( texttime)
            #for b in beds: print (b)
            hhdb.insert_bed_occupancy(beds)
            if fake_input:
                self.fake_user_input(hhdb, nos=3, blanks=2)
            print ('sweeptime={} nrecords={}'.format( texttime, len(beds)))

        print('sweep done')
        
            
            
            
        