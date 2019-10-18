'''
Created on Jul 7, 2019

@author: fsells
'''

import json
import sys, os, datetime, random
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.db.models import Count, Max, Avg
from django.db.models.functions import Lower
from django.db.models import Sum
from django.db.models import F
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache, cache_control
#from django.contrib.auth.decorators import login_required


import django.db.models.functions as x
from django.contrib.auth.decorators import permission_required


from .models import BedCheck, INBED_CHOICES, REASON_CHOICES
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
    
def get_units( obsolete=0, date=None): 
    units = BedCheck.objects.filter(Obsolete=obsolete).order_by('unit').values_list('unit', flat=True).distinct()
    return units
     
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
    
def census_tracking(request):
    date = request.GET.get("date", datetime.date.today())    
    beds = BedCheck.objects.filter(unit='G1').exclude(lastname=None, inbed='Yes').order_by('unit', 'room', 'bed')
    beds = beds[30:40] #todo remove this
    context = dict(date=date, beds=beds)
    print(context)
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
                       units=get_units(),
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
            print ('got ajax')
            print ('Raw Data:', request.body)
            data = json.loads(request.body.decode("UTF-8"))
            print('json data', data)
            unit = data.get('unit', 'xxx' )
            print(unit, 'unit')
            patients = data.get('patients', [])
            for p in patients: 
                x = MyObject(p)
                _update_bed(x, user, now)

            context = {'comment': 'update successful'}
            return JsonResponse(context)
            #return render(request, 'webapp/home.html', context)
            #return redirect('home')
            #return render(request, 'webapp:home.html', context)
        else:
            return HttpResponse('request was not json', request)
    

