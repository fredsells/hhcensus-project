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



import django.db.models.functions as x
from django.contrib.auth.decorators import permission_required


from .models import BedCheck, INBED_CHOICES, REASON_CHOICES
from webapp import logic_census
from setuptools._vendor.six import _urllib_request_moved_attributes, _meth_self


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
        

def get_beds(unit='G1', obsolete=0, date=None):
    queryset = BedCheck.objects.filter(Obsolete=obsolete, unit=unit).order_by('unit', 'room', 'bed')
    return queryset
    
     
def logout(request):
    return render(request, 'webapp/logout.html', {})    

def _update_bed(change, user, now):
    bed = BedCheck.objects.get(pk=change.id)
    print (bed)
    bed.inbed=change.inbed
    bed.reason=change.reason
    bed.comment=change.comment
    bed.updatedby = user
    bed.updatetime = now
    errors = bed.save()
    print(errors)
    return True

def get_totals_by_unit(date):
    beds = BedCheck.objects.filter(SweepTime__date=date, inbed='YES').order_by('unit', 'room', 'bed')
    totals = beds.values('unit').annotate(total=Count('unit')).order_by('unit')
    results = dict()
    for total in totals:
        results[total['unit']]=total['total']
    return results

def census_tracking(request):
    date = request.GET.get("date", None) 
    if date:
        date = datetime.datetime.strptime(date, '%m/%d/%Y')
    else:
        date = datetime.date.today()
    beds = BedCheck.objects.filter(SweepTime__date=date).exclude(inbed='YES').exclude(lastname=None).order_by('unit', 'room', 'bed')
    beds = beds##[30:40] #todo remove this
    totals_by_unit = get_totals_by_unit(date)
    pairs = totals_by_unit.items()
    context = dict(date=date, beds=beds, totals=pairs)
    return render(request, 'webapp/censustracking.html', context)
        
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def census_edit(request):
    if request.method=='GET':
        unit = request.GET.get('unit', DEFAULT_UNIT)
        print ('processing GET for', unit)
        beds = get_beds(unit)
        for bed in beds:
            if bed.CurrentAdmitDate == None: continue #nobody in the bed
            bed.CurrentAdmitDate = bed.CurrentAdmitDate.strftime('%#m/%#d/%Y')
#        beds = beds[25:30]  #good test data
        maxdate = datetime.date.today()
        context = dict(user='frederick.sells', 
                       unit=unit, 
                       units=logic_census.get_units(),
                       inbed_choices = INBED_CHOICES, 
                       reason_choices = REASON_CHOICES,
                       beds=beds, 
                       sweepdate = maxdate.strftime('%A -  %B %#d, %Y'))
        x = render(request, 'webapp/bedcheck.html', context)
        return x

@csrf_exempt
def save_changes(request):
        user = 'fredtest'
        now = datetime.datetime.now()
        if request.is_ajax(): 
            data = json.loads(request.body.decode("UTF-8"))
            print('json data', data)
            unit = data.get('unit', 'xxx' )
            patients = data.get('patients', [])
            for p in patients: 
                print('p', p)
                bed = BedCheck.objects.get(pk=p['id'])
                bed.inbed=p['inbed']
                bed.reason=p['reason']
                bed.comment=p['comment']
                bed.updatedby = user
                bed.updatetime=now
                bed.save(update_fields=['inbed', 'reason', 'comment', 'updatedby', 'updatetime'])
                print('saved', bed.id, bed.reason, bed.comment, bed.inbed, bed.lastname)

            context = {'comment': 'update successful'}
            return JsonResponse(context)
        else:
            return HttpResponse('request was not json', request)
    
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
    print('daterange', startdate, enddate, ndays)
    errors = logic_census.get_errors_by_day_and_unit(startdate, enddate)
    totals = logic_census.get_error_summary(units, startdate, enddate)
    context = dict(months=months, selectedmonth=startdate, errors=errors, units=units, totals=totals)
    
    return render(request, 'webapp/month_summary.html', context)
    
    
