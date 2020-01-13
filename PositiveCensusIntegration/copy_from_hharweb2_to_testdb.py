import pyodbc
import datetime
DEBUG = True

HHARWEB2 = (r'DRIVER={SQL Server};'
            r'SERVER=HHARWEB2\SQLEXPRESS;'
            r'DATABASE=PositiveCensusReport;'
            r'Trusted_Connection=yes;'    )

POSITIVE_CENSUS_TEST = (r'DRIVER={SQL Server};'
            r'SERVER=HHARWEB2\SQLEXPRESS;'
            r'DATABASE=PositiveCensus_Test;'
            r'Trusted_Connection=yes;'    )


LOCAL_HHdev = (r'DRIVER={SQL Server};'
                r'SERVER=.;'
               #HHSWLSQLDEV01
                r'DATABASE=HHdev;'
                r'Trusted_Connection=yes;'    )

def get_old_data(conn_str):
    Connection = pyodbc.connect(conn_str)
    Cursor = Connection.cursor()
    Cursor.execute('SET NOCOUNT ON')
    Connection.commit()
    sql = '''SELECT pcr.Unit, Room, ResidentNumber, ResidentName, Status, LevelOfCare,Gender
                      ,OrigAdmitDate,  YesNo, Reason, RepDate, Comments
                      , pcr.update_by, update_dt, pcr.create_dt, users.UserName
                FROM [dbo].[PositiveCensusReport] AS pcr
                LEFT JOIN [dbo].[PositiveCensusReportLogins] AS logins 
                    ON pcr.update_by=logins.PositiveCensusReportLoginID
                LEFT JOIN [dbo].[PositiveCensusReportUsers] AS users 
                    ON logins.PositiveCensusReportUserID=users.PositiveCensusReportUserID
                WHERE pcr.RepDate >= '2019-11-15' AND pcr.RepDate <= '2019-11-28'
                ORDER BY pcr.RepDate, Unit, Room
        '''
    Cursor.execute(sql)
    rows = Cursor.fetchall()
    Cursor.close()
    Connection.close()
    return rows

def insert_data(conn_str, data):
    Connection = pyodbc.connect(conn_str)
    Cursor = Connection.cursor()
    Cursor.execute('SET NOCOUNT ON')
    #Cursor.execute('SET IDENTITY_INSERT dbo.PositiveCensusReport  ON')
    Connection.commit()
    sql = '''INSERT  dbo.PositiveCensusReport
                  (Unit ,Room  ,ResidentNumber ,ResidentName
                  ,Status  ,LevelOfCare  ,Gender  ,OrigAdmitDate
                  ,YesNo  ,Reason ,RepDate   ,Comments
                  ,UpdateByID  ,UpdateDatetime  ,CreateDatetime  ,UpdateByName
                    ,Obsolete)   
                 VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                 '''
    Cursor.executemany(sql, data)
    Connection.commit()
    Cursor.close()

if __name__ == '__main__':
    data = get_old_data(HHARWEB2)
    if DEBUG:
        for x in data[:9]: print(len(x), x)
    insert_data(LOCAL_HHdev, data)
    print ('done')