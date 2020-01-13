import pyodbc
import datetime
import platform


PRODUCTION = (r'DRIVER={SQL Server};'
            r'SERVER=HHARWEB2\SQLEXPRESS;'
            r'DATABASE=PositiveCensusReport;'
            r'Trusted_Connection=yes;'    )

TEST = (r'DRIVER={SQL Server};'
            r'SERVER=HHARWEB2\SQLEXPRESS;'
            r'DATABASE=PositiveCensus_Test;'
            r'Trusted_Connection=yes;'    )

HHSWLSQLDEV01 = (r'DRIVER={SQL Server};'
                r'SERVER=HHSWLSQLDEV01;'
                r'DATABASE=FredTesting;'
                r'Trusted_Connection=yes;'    )

LAPTOP_SQL= (
        r'DRIVER={SQL Server};'
        r'SERVER=.;'
        r'DATABASE=HHdev;'
        r'Trusted_Connection=yes;'
    )

if platform.uname().node == 'PS-6KR5WF2':
    conn_str = LAPTOP_SQL
else:
    conn_str = PRODUCTION

YESNO = ''
REASON= ''
COMMENTS = ''


def reformat(row, rptdate):
    (Unit, Room, ResidentNumber, ResidentName, Status, LevelOfCare, Gender, AdmitDate) = row
    cleanup = (Unit, Room, ResidentNumber, ResidentName, Status, LevelOfCare, Gender, AdmitDate, YESNO, REASON,  rptdate, COMMENTS)
    return cleanup

def insert_bed_occupancy( beds, rptdate):
    beds = [reformat(bed, rptdate) for bed in beds[1:]] #drop header row
    ##################################for d in data: print('insert', d)
    Connection = pyodbc.connect(conn_str)
    Cursor = Connection.cursor()
    test = Cursor.execute('SELECT 333')  #test connection
    Cursor.execute('SET NOCOUNT ON')
    Connection.commit()
    sql = '''INSERT INTO dbo.PositiveCensusReport 
              (Unit, Room, ResidentNumber, ResidentName, Status, LevelOfCare, Gender
              , OrigAdmitDate, YesNo, Reason, RepDate, Comments)
              VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    Cursor.executemany(sql, beds)
    Connection.commit()
    Cursor.close()
    Connection.close()

        
def unittest():
    Connection = pyodbc.connect(conn_str)
    Cursor = Connection.cursor()
    test = Cursor.execute('SELECT 333')
    results = Cursor.fetchone()
    print ('unittest connection', results)
    Cursor.execute('SELECT TOP 10 * FROM [dbo].[PositiveCensusReport]')
    results = Cursor.fetchall()
    for r in results: print ('unittest', r)

if __name__ == '__main__':
    unittest()
    #DB = HHDB()
    #DB.mark_all_obsolete()
    print ('done')
