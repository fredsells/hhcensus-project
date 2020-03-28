'''
Created on Jul 10, 2019

@author: fsells
'''
import datetime
import random
from django.core.management.base import BaseCommand, CommandError


from webapp  import models
from webapp import sql_api 
from webapp.management.commands import local_db_api
from webapp.utilities import DataObject
ONE_HOUR = datetime.timedelta(hours=1)

class Command(BaseCommand):
    help = 'copies census data from local mydata tables  to local NightlyBedCheck in the same database'

    def add_arguments(self, parser):
        parser.add_argument('--start', action= 'store', help = 'first day of sweep mm/dd/yyyy, for testing',
                            type=lambda s: datetime.datetime.strptime(s, '%m/%d/%Y'),
                            default = datetime.date.today())
        parser.add_argument('--days', action= 'store', help = 'number of days for sweep, for testing', default=1, type=int)
        parser.add_argument('--fakeinput', action= 'store_true', help = 'create fake user entry for testing', default=False)
        
    def fake_user_input(self, hhdb, nos=0, blanks=0):
        hhdb.mark_current_inbed_yes()
        if blanks==0 and nos==0: return 
        for unit in ['G1', 'G2', 'S2']:
            beds = models.NightlyBedCheck.objects.filter(Obsolete=0, Unit=unit).order_by('room')
            for i, bed in enumerate(beds):
                if i<3: continue
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
                
    def reformat(self, row, reportdate):
        #print('row', row)
        #unit, room, bed, resident_number, patient_id, lastname, firstname, admitdatetime, status, sweepdatetime, dummy, gender, loc = row
        row.AdmitDate = row.AdmitDate.strftime('%m/%d/%Y %H%M %A')
        #rep_date = sweepdatetime + ONE_HOUR
        #newrow = unit, '{}/{}'.format(room, bed), resident_number, '{} {}'.format(lastname, firstname), status, loc, gender, admitdatetime, rep_date
        newrow = (row.UnitName, row.RoomAndBed, row.MedicalRecordNumber, row.Name, row.LastStatus, row.LevelOfCare, row.Sex, row.AdmitDate, reportdate)
        #print ('new', newrow)
        return newrow

    def get_scrubbed_beds_and_occupants(self, mydata,  querydate=None, reportdate=None):
        records = mydata.get_all_beds_and_current_occupants()
        #records = [DataObject(r) for r in records]
        #[print(r) for r in records[:9]]
        #records = [self.reformat(r, reportdate) for r in records]
        return records

    def save_bedcheck_data(self, records, reportdate):
        records = [DataObject(r) for r in records]
        for r in records:
           # print(r)



            bed = models.NightlyBedCheck()
            bed.Unit = r.UnitName
            bed.Room = r.RoomAndBed
            bed.ResidentNumber = r.MedicalRecordNumber
            bed.ResidentName =r.Name
            bed.Status = r.LastStatus
            bed.LevelOfCare = r.LevelOfCare
            bed.Gender = r.Sex
            bed.CurrentAdmitDate = r.AdmitDate
            bed.RepDate = reportdate.date()
            bed.save()
    

    def handle(self, *args, **options):
        fake_input = options['fakeinput']
        firstday =  options['start'] 
        ndays = options['days']
        almost_midnight = ' 11:45:00 PM'
        #######################################################################
        NOW = datetime.datetime.now()
        REPORT_DATE = NOW + ONE_HOUR
        
        NOW= NOW.date()
        print(REPORT_DATE)
        mydata = sql_api.DatabaseQueryManager()
        hhdb = local_db_api.HHDB()
        for n in range(ndays):
            records = self.get_scrubbed_beds_and_occupants(mydata, reportdate=REPORT_DATE.strftime('%m/%d/%Y'))
            self.save_bedcheck_data(records, REPORT_DATE)
        #     #records = [('G1', '150/D', '525377', 'Tirado Ines', 'In House', 'Level 2', 'F', '2016-12-01 20:00:00.0000000')]#, '03/23/2020')]
        #     records = records[:2]
        #     for r in records: print(r)
        #     hhdb.insert_bed_occupancy(records)
        # return

        
            # sweeptime = firstday + datetime.timedelta(days=n)
            # texttime = sweeptime.strftime('%m/%d/%Y') + almost_midnight
            # beds = mydata.get_beds_x_patients( texttime)
            # header = beds.pop(0)
            # #print (header)
            # beds = [ self.reformat(bed) for bed in beds]
            # hhdb.insert_bed_occupancy(beds)
            # continue
            # if fake_input:
            #     self.fake_user_input(hhdb, nos=3, blanks=2)
            # print ('sweeptime={} nrecords={}'.format( texttime, len(beds)))

        print('sweep done')
        
            
            
            
        