import json
import sys, os, datetime, random
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.db.models import Count, Max, Avg, ExpressionWrapper, F, Sum, Min, Max
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache, cache_control
#from django.contrib.auth.decorators import login_required
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from django.contrib.auth.decorators import permission_required

import calendar
from webapp  import models
from webapp import logic_census
from queue import Full
from django.db import connection
from django.db.models import Q
from django.db.models import  Count, Sum
from webapp import logic_census 


ONEDAY = datetime.timedelta(days=1)    


def oooooooooooooooooooget_summary(units, startdate, enddate):
    SQL = '''SELECT unit, SUM(ndays)
                FROM (
                    SELECT unit, SweepTime, 1 [ndays]
                  FROM [HHBedCheck].[dbo].[bedcheck]
                  WHERE SweepTime >= {} AND SweepTime <= {}
                  AND MRN IS NOT NULL
                  AND (inbed='' or ( inbed='NO' AND reason=''))
                  Group By unit, SweepTime
                  ) AS t
                group by unit  
                '''
        
    sql = SQL.format(startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d'))
    #print(sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    summary = list(cursor.fetchall())
    cursor.close()
    print (summary)
    print ('summary done')
    
    
def ooxxxoooooooooooooooooooooooooget_summary(units, startdate, enddate):    
    print (startdate, enddate)
    month = models.NightlyBedCheck.objects.filter(SweepTime__range=[startdate, enddate])
    ndays = month.values('SweepTime').distinct().count()  #aggregate(total=Count('SweepTime'))
    #counts = month.aggregate(blank=Count('pk', only=Q(inbed='')))
    #print (counts)
    for i in range(ndays):
        censusdate = startdate+datetime.timedelta(days=i)
        thisday = month.filter(SweepTime__date=censusdate, inbed='').values('Unit').aggregate(total=Count('Unit'))
        print('thisday', censusdate,  thisday)
        #blank = month.filter(inbed='').
        #print blank
    print  (ndays)
    print('month', month)

class Command(BaseCommand):
    help = 'copies data from MatrixCare to local DB'

    def add_arguments(self, parser):
        parser.add_argument('--start', action= 'store', help = 'first day of sweep mm/dd/yyyy, for testing',
                            type=lambda s: datetime.datetime.strptime(s, '%m/%d/%Y'),
                            default = datetime.date.today())
        parser.add_argument('--days', action= 'store', help = 'number of days for sweep, for testing', default=1, type=int)
        parser.add_argument('--fakeinput', action= 'store_true', help = 'create fake user entry for testing', default=False)
        


    def handle(self, *args, **options):
        print (options)
        date = datetime.date.today()
        startdate =  options['start'].date()
        ndays = options['days']
        enddate = startdate + datetime.timedelta(days=ndays)
        print (startdate, ndays, enddate)
        #print (startdate, enddate, ndays)
        #month = models.NightlyBedCheck.objects.filter(SweepTime__range=[startdate, enddate]).exclude(Obsolete=1).order_by('SweepTime', 'unit', 'room', 'bed')
        units = list(models.NightlyBedCheck.objects.order_by('Unit').values_list('Unit', flat=True).distinct())
        #print (units)
       ## daily_errors = logic_census.get_errors_by_day_and_unit(startdate, enddate)
        #########for r in daily_errors: print('error', r)
        #print(results)
        #totals = logic_census.get_totals(units, startdate, enddate)
        #for x in totals: print ('total', x)
        #print ( (totals,))
        summary = logic_census.get_error_summary(units,startdate, enddate)
        print(' done')
        
            
            
            


