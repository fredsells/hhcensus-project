
import pyodbc

LAPTOP_SQLEXPRESS = (
        r'DRIVER={SQL Server Native Client 10.0};'
        r'SERVER=.\SQLEXPRESS;'
        r'DATABASE=HHBedCheck;'
        r'Trusted_Connection=yes;'
    )

LAPTOP_SQL= (
        r'DRIVER={SQL Server};'
        r'SERVER=.;'
        r'DATABASE=HHdev;'
        r'Trusted_Connection=yes;'
    )

HH_DEV = (r'DRIVER={SQL Server};'
                r'SERVER=HHSWLSQLDEV01;'
                r'DATABASE=FredTesting;'
                r'Trusted_Connection=yes;'    )
  
conn_str = LAPTOP_SQL


class HHDB(object):
    def __init__(self):
        self.Connection = pyodbc.connect(conn_str)
        Cursor = self.Connection.cursor()
        Cursor.execute('SET NOCOUNT ON') 
        self.Connection.commit()
        
    def insert_bed_occupancy(self, data):
        Cursor = self.Connection.cursor()
        Cursor.execute('SET IDENTITY_INSERT dbo.bedcheck OFF')
        Cursor.execute('UPDATE dbo.PositiveCensusReport SET Obsolete=1')
        self.Connection.commit()
        print(type(data))
        print('\n\ninsert', data[0])
        sql = '''INSERT INTO dbo.PositiveCensusReport 
                (Unit, Room, ResidentNumber, ResidentName, Status, LevelOfCare, Gender, OrigAdmitDate, RepDate, Obsolete)
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)'''
        Cursor.executemany(sql, data)
        self.Connection.commit()
        Cursor.close()
        
    def mark_current_inbed_yes(self):
        Cursor = self.Connection.cursor()
        SQL = '''UPDATE dbo.bedcheck SET inbed='YES' WHERE obsolete=0'''
        Cursor.execute(SQL)
        self.Connection.commit()
        Cursor.close()        
        
    def close(self):
        self.Connection.close()
            
        
def unittest():        
    DB = HHDB()
    Cursor = DB.Connection.cursor()
    #################print (dir(Cursor))
    Cursor.execute('SET NOCOUNT ON') 
    Cursor.execute('SELECT 123')  
    results = Cursor.fetchone()
    print ('cursor returned ', results)
    DB.close()
    print (' unittest done')

if __name__ == '__main__': unittest()

