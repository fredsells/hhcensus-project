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

SAGELY2 = '''SELECT 
	pat.MedicalRecordNumber
	, pat.LastName [Resident_Last]
	, pat.FirstName [Resident_First]
	, CONVERT(VARCHAR(12), DateOfBirth, 101) [DOB]
	, NULL [LevelOfCare] --unit goes here
	, pat.MiddleName [MiddleName]
	, NULL [MaidenName] -- not used
	, pat.PreferredName [Nickname]
	, NULL [Phone] --@
	, NULL [Email] -- not used
	, CONCAT(ec.FirstName, ' ', ec.LastName) [EmergencyName] --@
	, phone.EmergencyPhone [EmergencyPhone] --@
	, pat.Sex [Gender]
	, NULL [Ethnicity] --not used
	, NULL [HomeTown] -- not used
	, pse.LastStatus [Status]
	, CONVERT(VARCHAR(12), pse.AdmitDate, 101) [MoveInDate]
	, bed.RoomName [Room]
	, SUBSTRING(bed.UnitName, 2, 1) [Floor]
	, NULL [Diabetic]
	, NULL [HearingImpairment]
	, NULL [SpeechImpairment]
	, NULL [VisionImpairment]
	, NULL [TherapyAnimal]
	, NULL [RequireCaine]
	, NULL [RequiresMotorScooter]
	, NULL [RequiresWalker]
	, NULL [RequiresWheelchair]
	, NULL [AdvanceCareDirective]
	, NULL [Excursions]
	, 'Form not Received' [three commas]
FROM ( 
	SELECT * 
	FROM mydata.vwPatientStayElementLatest
	WHERE LastStatus='In House'
	OR (LastStatus IN ('Expired', 'Discharged', 'Discharged RE') AND StartDate > DATEADD(day, -30, GETDATE() )  )
	) AS pse
JOIN mydata.Patient AS pat ON pat.PatientID = pse.PatientID
JOIN mydata.FacilityUnitRoomBed AS bed ON bed.BedID=pse.BedID
LEFT JOIN (
	SELECT PatientID, ContactID 
	FROM (
			SELECT PatientID
				,  ContactID
				, ROW_NUMBER() OVER(PARTITION BY PatientID, ContactID ORDER BY CallPriority DESC)     AS rk
			FROM mydata.PatientContact
			 WHERE EmergencyContact = 1
		  ) AS f
	WHERE f.rk=1
    ) AS pcx on pcx.PatientID = pat.PatientID
LEFT JOIN mydata.Contact AS ec ON ec.ContactID = pcx.ContactID
LEFT JOIN (
	SELECT xph.ContactID
		, CASE ph.AreaCode
			WHEN NULL THEN NULL
			ELSE CONCAT('(', ph.AreaCode, ') ', ph.Prefix, '-', ph.Suffix) 
		END [EmergencyPhone] --@
		, ROW_NUMBER() OVER(PARTITION BY ContactID ORDER BY ph.isPrimary DESC, pt.SortOrder ASC)     AS rk
	FROM mydata.ContactPhoneXref AS xph
	JOIN mydata.Phone AS ph ON ph.PhoneID = xph.PhoneID
	JOIN mydata.PhoneType AS pt ON pt.PhoneTypeID=ph.PhoneTypeID
	WHERE pt.PHoneTypeID in (1,4)  -- eliminate fax
	) AS phone ON ec.ContactID=phone.ContactID
  '''