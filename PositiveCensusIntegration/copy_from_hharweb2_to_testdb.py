import pyodbc
import datetime
DEBUG = True

HHARWEB2 = (r'DSN=copybedchecks32;'
            r'UID=copybedchecks;'
            r'PWD=RepresentativeDreamAdmireFaint2;'  )

POSITIVE_CENSUS_TEST = (r'DRIVER={SQL Server};'
            r'SERVER=HHARWEB2\SQLEXPRESS;'
            r'DATABASE=PositiveCensus;'
            r'Trusted_Connection=yes;'    )


LAPTOP = (r'DRIVER={SQL Server};'
                r'SERVER=.;'
               #HHSWLSQLDEV01
                r'DATABASE=FredTesting;'
                r'Trusted_Connection=yes;'    )

HHSWLDEV02 = (  #this works, even though UID and PWD are defined in ODBC DSN 32 bit
    r'DSN=censusapps32;'
    r'UID=hhcensus;'
    r'PWD=Plan-Tree-Scale-Model-Seed-9;'
    )  


def get_old_data(Connection):
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
                WHERE pcr.RepDate >= '2020-03-29' AND pcr.RepDate <= '2020-04-02'
                ORDER BY pcr.RepDate, Unit, Room;
        '''
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
    
def execute(source, destination, DEBUG=False):
    data = get_old_data(source)
    for x in data[:9]: print('census', x)
    print('nrecords', len(data))
    if DEBUG:
        print('DEBUG=True, no data written to DB')
    else:
        insert_data(destination, data)
        print ('data inserted into target')
    print ('done')

if __name__ == '__main__':
    source = pyodbc.connect(HHARWEB2)
    target = pyodbc.connect(HHSWLDEV02)
    execute(source, target, DEBUG=False)
    