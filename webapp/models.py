from django.db import models
import datetime
from django.utils import timezone
from rest_framework import serializers
# Create your models here.
from django.db import models
from unittest.util import _MAX_LENGTH
import os

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

class BedCheck(models.Model):
 #   id = models.IntegerField(primary_key=True)
    unit = models.CharField(max_length=10) #usually 2 #from PatientGroupAbbreviation
    room = models.CharField(max_length=6)
    bed =  models.CharField(max_length=5)
    mrn = models.CharField(max_length=9, null=True)
    patientID = models.IntegerField( null=True)
    lastname = models.CharField(max_length=50, null=True)
    firstname=models.CharField(max_length=50, null=True)
    CurrentAdmitDate = models.DateTimeField( null=True)
    CensusStatus = models.CharField(max_length=30, null=True)
    SweepTime = models.DateTimeField()
    Obsolete = models.IntegerField(default = 0)
    gender = models.CharField(max_length=1, null=True)
    LevelOfCare = models.CharField(max_length=20, null=True)
    inbed = models.CharField(max_length=6, null=True, blank=True, default='',choices=INBED_CHOICES, verbose_name='inbed')
    reason = models.CharField(max_length=80, null=True, blank=True, default='', choices=REASON_CHOICES)
    comment = models.CharField(max_length=80, null=True, blank=True, default='')
    updatedby = models.CharField(max_length=80, null=True, blank=True, default='')
    updatetime =models.DateTimeField(null=True)
    

    def __unicode__(self):
        return '{} {} {}'.format(self.unit, self.room, self.bed)

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.unit, self.room, self.bed)

    class Meta:
        db_table = 'bedcheck'
        managed = True

