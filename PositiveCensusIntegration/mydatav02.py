'''
Created on Sep 17, 2019

@author: fsells
'''
import sys, datetime, os
import pyodbc

LOCAL_LINK_VIEWS = (r'DRIVER={SQL Server};'
                r'SERVER=HHSWLSQLDEV01;'
                r'DATABASE=FredTesting;'
                r'Trusted_Connection=yes;'    )


SQL = '''
SET NOCOUNT ON
  
DECLARE @SweepDate DATETIME = ? --'2019-10-28 23:45:00'
--SELECT @SweepDate
 --SELECT --pse.PatientID, pse.StartDate, pse.CensusType , count(*)
 --bed.UnitName, bed.RoomAndBed, pat.LastName, pat.FirstName, loc.LocID, loc.Description [LoCDescription], pse.*
 
 DECLARE @ResidentsTbl TABLE (
	[BedID] INT NULL,
	[ResidentNumber] [nvarchar](50) NULL,
	[ResidentName] [nvarchar](50) NULL,
	[Status] [nvarchar](50) NULL,
	[LevelOfCare] [nvarchar](50) NULL,
	[Gender] [nvarchar](50) NULL,
	[OrigAdmitDate] [datetime] NULL
) 
 INSERT INTO @ResidentsTbl
 SELECT pse.BedID, pat.MedicalRecordNumber,  pat.LastName+' '+ pat.FirstName [Name], pse.LastStatus, loc.Description [LevelOfCare], pat.sex , pse.AdmitDate
 FROM mydataPatientStayElement AS pse
 JOIN (
	 SELECT PatientID, MAX(StartDate) AS StartDate
	 FROM mydataPatientStayElement 
	 WHERE  @SweepDate BETWEEN StartDate AND EndDate
	 AND CensusType NOT IN (3,4,7,8,9) -- ignore outpatients
	 GROUP BY PatientID
	 ) AS last ON last.PatientID=pse.PatientID AND last.StartDate=pse.StartDate
JOIN mydataPatient AS pat ON pat.PatientID=pse.PatientID
LEFT JOIN mydataCensus_LevelOfCare AS loc on loc.LOCID = pse.LOCID and pse.FacilityID=loc.FacilityID 
WHERE pse.CensusType IN (1,2,5,6)


SELECT UnitName, RoomAndBed, ResidentNumber, ResidentName, Status, LevelOfCare, Gender, OrigAdmitDate
From mydataBed AS bed
LEFT JOIN @ResidentsTbl AS res on res.BedID=bed.BedID
Order By  UnitName, RoomAndBed
'''


class MyDataQueryManager(object):
    '''
    classdocs
    '''


    def __init__(self, conn_str = LOCAL_LINK_VIEWS, DEBUG=False):
        self.DEBUG = DEBUG
        self.Connection = pyodbc.connect(conn_str)
        cursor = self.Connection.cursor()
        cursor.execute("SELECT 1")  #will raise exception if connection fails

    def get_something(self, sql, *args):
        cursor = self.Connection.cursor()
        cursor.execute(sql, *args)
        names = [column[0] for column in cursor.description]
        records = cursor.fetchall()  
        return [names] + records
         
    def get_beds_x_patients(self, sweeptime):
        sql = SQL
        records = self.get_something(sql, sweeptime)
        return records

        
def unittest():
    mydata = MyDataQueryManager()
    sweeptime = datetime.datetime.now()
    records = mydata.get_beds_x_patients(sweeptime)
    for p in records: print('bed_patient', p)
    print ('mydata_api unittest done', len(records))
        
if __name__ == '__main__':
    unittest()