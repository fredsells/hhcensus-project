'''
Created on Dec 14, 2019

@author: fsells
'''
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from webapp import models 
from webapp import sql_api
from webapp.constants import *

UNUSED_FIELDS = {None: ['firstname', 'lastname', 'date', 'time','oldloc', 'oldbed', 'dischargeto', 'admitfrom', 'newloc', 'newbed'],
                 ADMISSION:['oldloc', 'oldbed', 'dischargeto'],
                 ROOM_CHANGE:['admitfrom', 'dischargeto', 'oldloc'], 
                 OUT_TO_HOSPITAL:['oldloc', 'newloc', 'newbed', 'admitfrom'],
                 RETURN_FROM_HOSPITAL:['oldloc',  'oldbed', 'dischargeto'],
                 OUT_TO_LEAVE_OF_ABSENCE:['newbed', 'newloc', 'oldloc', 'admitfrom'],
                 RETURN_FROM_LEAVE_OF_ABSENCE :['oldbed', 'oldloc', 'dischargeto'],
                 DISCHARGE:['oldloc', 'newloc', 'newbed', 'admitfrom'],
                 DEATH:['oldloc', 'newloc', 'newbed', 'admitfrom', 'dischargeto'],
                 }

class Choices(object):
    def __init__(self):
        DB = sql_api.DatabaseQueryManager()
        records = DB.get_level_of_care_definitions()
        self.LevelOfCare = [(r['Description'], r['Description']) for r in records]
        records = DB.get_beds()
        records = [ '{}-{}/{}'.format(r['UnitName'], r['RoomName'], r['BedName']) for r in records]
        self.Beds = [ (name,name) for name in records]
        records = DB.get_admit_discharge_locations()
        admitfrom = [r['LocationName'] for r in records if r['isAdmitLocation']]
        dischargeto = [r['LocationName'] for r in records if r['isDischargeLocation']]
        self.AdmittedFrom = [ (x,x) for x in admitfrom]
        self.DischargedTo =  [(x,x) for x in dischargeto]
        self.Patients = patients = DB.get_patients()
        for p in patients:
            p['Letter'] = p['LastName'][0].upper()
            p['CensusStatus'] = p['CensusStatus'].replace(' ', '')  #remove embedded blanks, makes html simpler
        self.StatusChoices = list(set([p['CensusStatus'] for p in patients])) #get unique        
        self.Actions = [ ('0','Select a census type . . .')] + [ (x,x) for x in ACTIONS]
        
CHOICES = Choices()         

class CensusChangeForm(forms.Form):
    action = forms.ChoiceField(label='Select Census Event', choices=CHOICES.Actions, initial='0')
    firstname = forms.CharField(max_length=30,label='First Name')
    lastname  = forms.CharField(max_length=30)
    date      = forms.DateField(label="Date:", widget=forms.TextInput(attrs={'class': "datepicker"}))
    time      = forms.TimeField(label="Time:")
    oldbed = forms.ChoiceField(label='From Bed', choices=CHOICES.Beds)
    newbed = forms.ChoiceField(label='Into Bed', choices=CHOICES.Beds)
    newloc = forms.ChoiceField(label='Level of Care', choices=CHOICES.LevelOfCare)
    oldloc = forms.ChoiceField(label='Prior Level of Care', choices=CHOICES.LevelOfCare)
    admitfrom = forms.ChoiceField(label='Admitted From', choices=CHOICES.AdmittedFrom)
    dischargeto = forms.ChoiceField(label='Discharged To', choices=CHOICES.DischargedTo)
    user = forms.CharField(label='User', max_length=50, widget=forms.TextInput(attrs={'readonly':'readonly'}))
     
    class Meta:
        pass
#         fields = ['action', 'firstname', 'lastname', 'date', 'time']
#         exclude = []
#         widgets = []
#         errors = []
    
    
    def __init__(self,  *args, **kwargs):
        super(CensusChangeForm, self).__init__(*args, **kwargs)
        action = self.fields['action'].get_bound_field(self, 'action').value()
        if action != '0':
            self.initial['action'] = action
            for field_name in UNUSED_FIELDS[action]:
                del self.fields[field_name]
       
