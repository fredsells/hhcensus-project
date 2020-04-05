'''
Created on Jul 7, 2019

@author: fsells
'''

import json
import sys, os, datetime, random
from dateutil.relativedelta import relativedelta
import calendar

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.db.models import Count, Max, Avg, Sum, F
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache, cache_control
#from django.contrib.auth.decorators import login_required
#from setuptools._vendor.six import _urllib_request_moved_attributes, _meth_self
import django.db.models.functions as x
from django.contrib.auth.decorators import permission_required


from .models import NightlyBedCheck, INBED_CHOICES, REASON_CHOICES, CensusChangeLog
from webapp import logic_census
from webapp import sql_api 
from webapp import forms
from . import sql_api
from webapp import email_sender
from webapp.utilities import record_elapsed_time



DEFAULT_UNIT = 'G1'

class MyObject:
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)
        
    def __repr__(self):
        pairs = list(self.__dict__.items())
        pairs.sort()
        pairs = ['%s=%s'%p for p in pairs]
        text = ', '.join(pairs)
        return text

def home(request):
    print('---------------------rendering home')
    context = {}
    return render(request, 'webapp/home.html', context)
        


     
def logout(request):
    return render(request, 'webapp/logout.html', {})    

def _update_bed(change, user, now):
    bed = NightlyBedCheck.objects.get(pk=change.id)
    print (bed)
    bed.inbed=change.inbed
    bed.reason=change.reason
    bed.comment=change.comment
    bed.updatedby = user
    bed.updatetime = now
    errors = bed.save()
    print(errors)
    return True



def census_tracking(request): ###############################################################
    date = request.GET.get("date", None) 
    if date:
        date = datetime.datetime.strptime(date, '%m/%d/%Y').date()
    else:
        date = datetime.date.today()
    residents = NightlyBedCheck.objects.filter(RepDate=date).exclude(ResidentName='').order_by('Unit', 'Room', )
    NotYes = residents.exclude(Inbed='YES')
    InbedBlank = NotYes.filter(Inbed='')
    InbedNoReasonBlank = NotYes.filter(Inbed='No', Reason='')
    errors = InbedBlank | InbedNoReasonBlank
    errors.order_by('unit', 'Room')
    totals = residents.values_list('Unit').annotate(total=Count('Unit')).order_by('Unit')
    context = dict(date=date, beds=errors, totals=totals)
    return render(request, 'webapp/censustracking.html', context)
        
def resident_location(request):
    unit = request.GET.get('unit', DEFAULT_UNIT)
    date = datetime.date.today()
    beds = logic_census.get_beds(unit, obsolete=0)
    context = dict(user='frederick.sells', 
                    unit=unit, 
                    units = logic_census.get_units(),
                    beds = beds,
                    repdate = beds[0].RepDate
                    )
    return render(request, 'webapp/resident_location.html', context)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def census_edit(request):
    if request.method=='GET':
        unit = request.GET.get('unit', DEFAULT_UNIT)

        print ('processing GET for', unit)
        beds = logic_census.get_beds(unit)
        for bed in beds:
            #print(bed)
            if bed.CurrentAdmitDate == None: continue #nobody in the bed
            bed.CurrentAdmitDate = bed.CurrentAdmitDate.strftime('%#m/%#d/%Y')
#        beds = beds[25:30]  #good test data
        maxdate = datetime.date.today()
        context = dict(user='frederick.sells', 
                       unit = unit,
                       units=logic_census.get_units(),
                       inbed_choices = INBED_CHOICES, 
                       reason_choices = REASON_CHOICES,
                       beds=beds, 
                       sweepdate = maxdate.strftime('%A -  %B %#d, %Y'))
        x = render(request, 'webapp/bedcheck.html', context)
        return x
    

@csrf_exempt
def save_changes(request):  ###########saves changes to In Bed status page.
        user = 'fredtest'
        now = datetime.datetime.now()
        if request.is_ajax(): 
            data = json.loads(request.body.decode("UTF-8"))
            ###############################################################print('json data', data)
            unit = data.get('unit', 'xxx' )
            patients = data.get('patients', [])
            for p in patients: 
                print('json', p)
                bed = NightlyBedCheck.objects.get(pk=p['id'])
                bed.Inbed=p['inbed']
                bed.Reason=p['reason']
                bed.Comments=p['comment']
                bed.UpdatedByName = user
                bed.UpdateDatetime=now
                bed.save()###update_fields=['Inbed', 'Reason', 'Comments', 'UpdatedByName', 'UpdateDatetime'])
                print('saved {}'.format(bed))

            context = {'comment': 'update successful'}
            return JsonResponse(context)
        else:
            return HttpResponse('request was not json', request)


@record_elapsed_time    
def monthly_summary(request):
    units=logic_census.get_units()
    this_month = datetime.date.today().replace(day=1)
    months = [ this_month-relativedelta(months=i) for i in range(12)]
    startdate = request.GET.get('start', None)
    if startdate:
        startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d').date()
    else:
        startdate = this_month
    ndays = calendar.monthrange(startdate.year, startdate.month)[1]
    enddate = datetime.date(year=startdate.year, month=startdate.month, day=ndays)
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxdaterange', startdate, enddate, ndays)
    Summarizer = logic_census.MonthlySummaryComputer(startdate)

    errors = Summarizer.get_details_by_day_x_unit()
    print('errors', errors.keys())
    # totals = logic_census.get_error_summary(units, startdate, enddate)
    context = dict(months=months, selectedmonth=startdate, units=units, errors=errors, maxdays=Summarizer.maxdays,  totals=Summarizer.totals)
    
    return render(request, 'webapp/month_summary.html', context)
    
    
###############################################################################################

def notifications(request):
    TEMPLATE = 'webapp/testform.html'
    USER='frederick.sells'
    FORM_CLASS = forms.CensusChangeForm
    if request.method == 'POST':
        values =  dict(request.POST.items())
        values.pop('csrfmiddlewaretoken', None)  #don't need this
        values.pop('btnSubmit', None)
        values['timestamp'] = datetime.datetime.now()
        email_sender.email_census_edit_notification(**values)
        date = values.pop('date')
        time = values.pop('time')
        values['eventtime'] = datetime.datetime.strptime( date+time, '%m/%d/%Y%H:%M')  
        record = CensusChangeLog(**values)
        record.save()
        return redirect('/webapp/notifications')
#         form = form_class(request.POST)
#         if form.is_valid():
#             pass  # does nothing, just trigger the validation
#             print('posting form', form)
    else:  ####################################  GET method ##################################
        print('processing GET', request)
        action = request.GET.get('action', '0')
        if action == None:
            return render(request, TEMPLATE)
        else:
            patients=forms.CHOICES.Patients
            status_choices=forms.CHOICES.StatusChoices
            form = FORM_CLASS(initial= dict(action=action, user=USER))
            context = dict(form=form, action=action, patients=patients, status_choices = status_choices)
            return render(request, TEMPLATE, context)
        
        