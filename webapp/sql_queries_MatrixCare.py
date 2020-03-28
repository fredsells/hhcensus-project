'''
Created on Dec 30, 2019

@author: fsells
'''


ALL_BEDS = ''' SELECT * FROM mydata.FacilityUnitRoomBed ORDER BY UnitName, RoomName, BedName   '''

ALL_PATIENTS = '''
                  SELECT pat.*, stay.BedID, 
                  IIF( stay.LOCID IS NULL, '', loc.Description )  [LevelOfCare] ,
                  IIF( stay.BedID IS NULL, '', CONCAT(bed.UnitName, '-', bed.RoomName, '/', bed.BedName) ) AS RoomAndBed 
                  FROM mydata.Patient   AS pat
                  LEFT JOIN mydata.vwPatientStayElementLatest AS stay ON  stay.PatientID=pat.PatientID
                  LEFT JOIN mydata.Census_LevelOfCare AS loc on loc.LOCID = stay.LOCID and stay.FacilityID=loc.FacilityID 
                  LEFT JOIN mydata.FacilityUnitRoomBed AS bed on bed.BedID = stay.BedID
                  ORDER BY LastName, FirstName
                '''

LEVEL_OF_CARE_DEFINITIONS = '''SELECT * FROM mydata.Census_LevelOfCare WHERE FacilityID=15 --SNF'''

CENSUS_ADMIT_DISCHARGE_LOCATION = '''SELECT * FROM mydata.Census_AdmitDischargeLocation ORDER BY LocationName'''

CENSUS_LOA = '''SELECT * FROM mydata.Census_LOA   WHERE  FacilityID=15  ORDER BY Description '''

All_BEDS_AND_CURRENT_OCCUPANTS = '''
          SELECT UnitName, CONCAT(RoomName, '/', BedName) AS RoomAndBed, MedicalRecordNumber
          ,  CONCAT(LastName,' ', FirstName) [Name]
          , LastStatus, LevelOfCare, Sex, OriginalAdmtDt, AdmitDate
        FROM mydata.vwAllBedsAndCurrentOccupants 
        ORDER BY UnitName, RoomName, BedName
        '''