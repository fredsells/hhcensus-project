'''
Created on Dec 30, 2019

@author: fsells
'''


ALL_BEDS = '''
        SELECT facbed.BedID
     , facbed.RoomID
     , facroom.PatientGroupID AS UnitID
     , RTRIM(LTRIM(patgrp.Abbreviation)) AS UnitName
     , RTRIM(LTRIM(facroom.RoomName)) AS RoomName
     , RTRIM(LTRIM(facbed.BedName)) AS BedName
/*     , RTRIM(LTRIM(facroom.RoomName)) +'/' + RTRIM(LTRIM(facbed.BedName)) AS RoomAndBed
     , fac.Name [FacilityName]
     , fac.FacilityTypeCode [FacilityTypeCode]
     , fac.NationalProviderID 
     , cert.BeginDate
     , cert.EndDate
     , cert.BedTypeID
     , bedtype.BedTypeDesc*/
      FROM [STVSNF].[FacilityBed] AS facbed
      JOIN STVSNF.FacilityBedCert as cert ON cert.BedId=facbed.bedid
      JOIN STVSNF.FacilityRoom AS facroom ON  facroom.RoomID=facbed.RoomID
      JOIN STVSNF.PatientGroup AS patgrp ON patgrp.PatientGroupID=facroom.PatientGroupID
--      JOIN STVSNF.Facility AS fac ON fac.Facilityid=cert.FacilityID
--      LEFT JOIN STVSNF.FacilityBedType AS bedtype on bedtype.BedTypeID=cert.BedTypeID
      WHERE facbed.DeletedFlag=0
          OR facroom.DeletedFlag=0
          OR cert.DeletedFlag=0
          OR patgrp.DeletedFlag=0
--          OR fac.DeletedFlag=0
 --         OR bedtype.DeletedFlag=0
     ORDER BY UnitName, RoomName, BedName
    '''

ALL_PATIENTS = '''SELECT * FROM [STVSNF].[Patient] WHERE DeletedFlag = 0 ORDER BY LastName, FirstName'''

LEVEL_OF_CARE_DEFINITIONS = '''SELECT * FROM [STVSNF].Census_LevelOfCare
                                      WHERE DeletedFlag = 0
                                      AND FacilityID=15 --SNF'''

CENSUS_ADMIT_DISCHARGE_LOCATION = '''SELECT * FROM STVSNF.Census_AdmitDischargeLocation 
                                     WHERE DeletedFlag=0
                                     ORDER BY LocationName'''


CENSUS_LOA = '''SELECT * FROM [STVSNF].[Census_LOA]   
                WHERE DeletedFlag=0 AND FacilityID=15  --SNF
                ORDER BY Description '''

