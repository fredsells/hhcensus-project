'''
Created on Jul 10, 2019

@author: fsells
'''
import pyodbc
import datetime
from django.core.management.base import BaseCommand, CommandError


DEBUG = True

HHARWEB2 = (r'DSN=copybedchecks32;'
            r'UID=copybedchecks;'
            r'PWD=RepresentativeDreamAdmireFaint2;'  )

POSITIVE_CENSUS_TEST = (r'DRIVER={SQL Server};'
            r'SERVER=HHARWEB2\SQLEXPRESS;'
            r'DATABASE=PositiveCensus;'
            r'Trusted_Connection=yes;'    )


# LAPTOP = (r'DRIVER={SQL Server};'  no longer doing any work on laptop, too many db connection problesm.
#                 r'SERVER=.;'
#                #HHSWLSQLDEV01
#                 r'DATABASE=FredTesting;'
#                 r'Trusted_Connection=yes;'    )

HHSWLDEV02 = (  #this works, even though UID and PWD are defined in ODBC DSN 32 bit
    r'DSN=censusapps32;'
    r'UID=hhcensus;'
    r'PWD=Plan-Tree-Scale-Model-Seed-9;'
    )  

CONNECTIONS = dict (dev=HHSWLDEV02, prod=None)

ONE_HOUR = datetime.timedelta(hours=1)

def get_old_data(Connection, start, end):
    #Connection = pyodbc.connect(conn_str)
    Cursor = Connection.cursor()
    #Cursor.execute('SET NOCOUNT ON')
    #Connection.commit()
    sql = '''
             SELECT pcr.Unit, Room, ResidentNumber, ResidentName, Status, LevelOfCare,Gender
                      ,OrigAdmitDate,  YesNo, Reason, RepDate, Comments
                      , pcr.update_by, update_dt, pcr.create_dt, users.UserName
                FROM [dbo].[PositiveCensusReport] AS pcr
                LEFT JOIN [dbo].[PositiveCensusReportLogins] AS logins 
                    ON pcr.update_by=logins.PositiveCensusReportLoginID
                LEFT JOIN [dbo].[PositiveCensusReportUsers] AS users 
                    ON logins.PositiveCensusReportUserID=users.PositiveCensusReportUserID
                WHERE pcr.RepDate BETWEEN '{}' AND '{}'
                ORDER BY pcr.RepDate, Unit, Room;
        '''
    sql = sql.format(start, end)
    print (sql)
    Cursor.execute(sql)
    rows = Cursor.fetchall()
    Cursor.close()
    Connection.close()
    return rows

def insert_data(Connection, data):
    #Connection = pyodbc.connect(conn_str)
    Cursor = Connection.cursor()
    Cursor.execute('SET NOCOUNT ON')
    #Cursor.execute('SET IDENTITY_INSERT dbo.PositiveCensusReport  ON')
    Connection.commit()
    sql = '''INSERT  dbo.NightlyBedCheck
                  (Unit ,Room  ,ResidentNumber ,ResidentName
                  ,Status  ,LevelOfCare  ,Gender  ,CurrentAdmitDate
                  ,Inbed  ,Reason ,RepDate   ,Comments
                  ,UpdateByID  ,UpdateDatetime  ,CreateDatetime  ,UpdateByName
                    ,Obsolete)   
                 VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                 '''
    Cursor.executemany(sql, data)
    Connection.commit()
    Cursor.close()    

def execute(source, destination, startdate, enddate, save):
    data = get_old_data(source, startdate, enddate)
    print('nrecords=', len(data))
    if save:
        insert_data(destination, data)
        print ('data inserted into target')
    else:
        for x in data[:9]: print('census', x)
        print('DEBUG=True, no data written to DB')

    print ('done')

class Command(BaseCommand):
    help = 'copies census data from HHARWEB2 PositiveCensusReport to local/prod NightlyBedCheck'

    def add_arguments(self, parser):
        parser.add_argument('--start', action= 'store', help = 'first day of sweep mm/dd/yyyy, for testing',
                            type=lambda s: datetime.datetime.strptime(s, '%m/%d/%Y'),
                            default = datetime.date.today())
        parser.add_argument('--end', action= 'store', help = 'first day of sweep mm/dd/yyyy, for testing',
                            type=lambda s: datetime.datetime.strptime(s, '%m/%d/%Y'),
                            default = datetime.date.today())

        parser.add_argument('--target', action='store', help='dev (default) for dev server, prod for production server'  ,
                            default = 'dev')
        parser.add_argument('--save', action= 'store_true', help = 'required to write data to target', default=False)
        



    def handle(self, *args, **options):
        sourcestring = HHARWEB2
        targetname = options['target']
        targetstring = CONNECTIONS[targetname]
        startdate = options['start']
        enddate = options['end']
        save = options['save']
        print(options)
        print (targetname, startdate, enddate, save, targetstring)
        source = pyodbc.connect(sourcestring)
        target = pyodbc.connect(targetstring)
        execute(source, target, startdate, enddate, save)
        print('copy done')

    

        
            
            
            
        