from django.db import models
import datetime
from django.utils import timezone
from rest_framework import serializers
# Create your models here.
from django.db import models
from unittest.util import _MAX_LENGTH
import os

from django.db import connection

from webapp import utilities

def ooooooooooooooooooooooooooooooooooooget_all_patients_from_mydata():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM dbo.mydataPatient ORDER BY LastName, FirstName")
        rows = cursor.fetchall()
    return rows
@utilities.record_elapsed_time
def get_all_beds():
    with connection.cursor() as cursor:
        cursor.execute("SELECT UnitName+'-'+RoomAndBed [Bed] FROM dbo.mydataBed ORDER BY UnitName, RoomAndBed")
        rows = cursor.fetchall()
    return rows


INBED_CHOICES = (  ('',''),  #indicates not answered
                   ('Yes','Yes'),
                  ('No','No'),
                 
                )

REASON_CHOICES = (
            ("" ,""),
            ("Admission","Admission"),
            ("Discharge","Discharge"),
            ("Expiration","Expiration"),
            ("Out to Hospital","Out to Hospital"),
            ("Out to Leave of Absence","Out to Leave of Absence"),
            ("Return from Hospital","Return from Hospital"),
            ("Return from Leave of Absence","Return from Leave of Absence"),
            ("Room Change","Room Change"),
        )

class oooooPositiveCensusReport(models.Model):
 #   id = models.IntegerField(primary_key=True)
    Unit = models.CharField(max_length=10) #usually 2 #from PatientGroupAbbreviation
    room = models.CharField(max_length=6)
    bed =  models.CharField(max_length=5)
    mrn = models.CharField(max_length=9, null=True)
    patientID = models.IntegerField( null=True)
    lastname = models.CharField(max_length=50, null=True)
    firstname=models.CharField(max_length=50, null=True)
    CurrentAdmitDate = models.DateTimeField( null=True)
    CensusStatus = models.CharField(max_length=30, null=True)
    SweepTime = models.DateTimeField()
    Obsolete = models.IntegerField(default = 0, db_column='obsolete')
    Gender = models.CharField(max_length=1, null=True)
    LevelOfCare = models.CharField(max_length=20, null=True)
    inbed = models.CharField(max_length=6, null=True, blank=True, default='',choices=INBED_CHOICES, verbose_name='inbed')
    reason = models.CharField(max_length=80, null=True, blank=True, default='', choices=REASON_CHOICES)
    comment = models.CharField(max_length=80, null=True, blank=True, default='')
    updatedby = models.CharField(max_length=80, null=True, blank=True, default='')
    updatetime =models.DateTimeField(null=True)
    

    def __unicode__(self):
        return '{} {} {}'.format(self.Unit, self.room, self.bed)

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.Unit, self.room, self.bed)

    class Meta:
        db_table = 'bedcheck'
        managed = False
        
class PositiveCensusReport(models.Model):
 #   id provided automatically by framework
    Unit = models.CharField(max_length=50, null=True) #usually 2 #from PatientGroupAbbreviation
    Room = models.CharField(max_length=50) #actually room/bed to match legacy
    ResidentNumber = models.CharField(max_length=50, null=True)
    ResidentName = models.CharField(max_length=100, null=True)
    Status = models.CharField(max_length=50, null=True)
    LevelOfCare = models.CharField(max_length=50, null=True)
    Gender = models.CharField(max_length=50, null=True)
    OrigAdmitDate = models.DateTimeField(null=True)
    YesNo = models.CharField(max_length=50, null=True, blank=True, default='',choices=INBED_CHOICES, verbose_name='inbed')
    Reason = models.CharField(max_length=300, null=True, blank=True, default='', choices=REASON_CHOICES)
    RepDate = models.DateField(null=True)
    Comments = models.CharField(max_length=300, null=True, blank=True, default='')    
    update_by = models.CharField(max_length=80, null=True, blank=True, default='')
    update_dt =models.DateTimeField(null=True)
    Obsolete = models.IntegerField(default = 0)
    

    def __unicode__(self):
        return '{} {} {}'.format(self.Unit, self.room, self.bed)

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.Unit, self.room, self.bed)
        
    class Meta:
        db_table = 'PositiveCensusReport'
        managed = False
        
class CensusActionType(models.Model):
    Id = models.CharField(max_length=10, primary_key=True, null=False)
    Description = models.CharField(max_length=80, null=False)
    
    def __unicode__(self):
        return '{}={}'.format(self.Id, self.Description)

    def __str__(self):
        return '{}={}'.format(self.id, self.description)
        
    class Meta:
        pass
        db_table = 'webapp_CensusActionType'
        #managed = False
        
################################ mydata models after here ######################################

# class mydataPatients(models.Model):  #see views defined for mydata
#     PatientID = models.IntegerField(primary_key=True)
#     LastName = models.CharField(max_length=50, null=True)
#     FirstName = models.CharField(max_length=50, null=True)
#     RoomNumber = models.CharField(max_length=151, null=True)
#     CensusStatus = models.CharField(max_length=30, null=True)
#     
#     def __unicode__(self):
#         return '{}, {}'.format(self.LastName, self.FirstName)
# 
#     def __str__(self):
#         return '{}, {}'.format(self.LastName, self.FirstName)
#         
#     class Meta:
#         db_table = 'mydataPatient'
#         managed = False       


class CensusChangeLog(models.Model):
    action = models.CharField(max_length=50, default='error')
    
    
class mydataBed(models.Model):  #see views defined for mydata
    BedID = models.IntegerField(primary_key=True)
    UnitName = models.CharField(max_length=50, null=True)
    RoomAndBed = models.CharField(max_length=50, null=True)
   
    def __unicode__(self):
        return '{}, {}'.format(self.UnitName, self.RoomAndBed)

    def __str__(self):
        return '{}, {}'.format(self.UnitName, self.RoomAndBed)
        
    class Meta:
        db_table = 'mydataBed'
        managed = False           
    
def get_all_bed_choices():
    beds = mydataBed.objects.all().order_by('UnitName', 'RoomAndBed')
    choices = [(bed.BedID, '{}-{}'.format(bed.UnitName, bed.RoomAndBed)) for bed in beds]
    for c in choices: print(c)
    return choices
