'''
Business logic to connect views/urls to database/models
This module SHOULD contain no logic specific to the 
web api
 Author: Fred Sells  10/29/2019
 '''



import sys, os, datetime, random
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Max, Avg, Sum, F
from django.db.models.functions import Lower
from django.db import connection

from webapp import models
from webapp import utilities
from setuptools._vendor.six import _meth_self


DEBUG = False
ONEDAY = datetime.timedelta(days=1)

def get_units( obsolete=0, date=None): 
    units = models.PositiveCensusReport.objects.filter(Obsolete=obsolete).order_by('unit').values_list('unit', flat=True).distinct()
    return list(units)


def get_errors_by_day_and_unit(startdate, enddate):
    results = []
    date = startdate
    while date <= enddate:
        totals = models.PositiveCensusReport.objects.filter(SweepTime__date=date).exclude(inbed='YES').exclude(inbed='NO', reason='').values('unit').annotate(total=Count('SweepTime'))
        errors = dict(date=date)
        for total in totals:
            errors[total['unit']]=total['total']
        results.append ( errors)
        date += ONEDAY
    return results


def get_error_summary(units, startdate, enddate):
    ndays = enddate-startdate
    ndays = 1+ndays.days
    print(startdate, enddate, ndays)
    census = models.PositiveCensusReport.objects.filter(SweepTime__date__range=[startdate, enddate]).exclude(mrn='')
    partial_census = dict(zip(units,[0]*len(units)))
    full_census = dict(zip(units,[0]*len(units)))
    totals = dict(zip(units,[ndays]*len(units)))
    nonedone = dict(zip(units,[ndays]*len(units)))
    totals['title'] = 'Totals'
    full_census['title']='Days of Full Census Done'
    partial_census['title'] = 'Days of Partial Census Done'
    nonedone['title'] = 'Days of No Census Done'
    date = startdate
    days_with_census = census.values('SweepTime').distinct().count()#aggregate(days=Count('SweepTime'))
    print(ndays, days_with_census, '<<<<<<<<<<<<<<<<<<<<<<<<<<')
    while date <= enddate:
        #print(date)
        aday = census.filter(SweepTime__date=date)
        for unit in units:
            aunit = aday.filter(unit=unit)
            if aunit.exclude(inbed='YES').exclude(inbed='NO', reason='').values('unit').count():
                partial_census[unit] += 1
            if aunit.filter(inbed='YES').values('unit').count():
                full_census[unit] += 1
            if aunit.filter(inbed='NO').exclude(reason='').values('unit').count():
                full_census[unit] += 1
            nonedone[unit] = 1+ndays-days_with_census-full_census[unit]
            
        date += ONEDAY
    keys = ['title', 'total'] + units
    results = []
    
    for census in [full_census, nonedone, partial_census, totals]:
        census['total'] = sum(census[unit] for unit in units)
        results.append(census)
    
    for key in keys:
        for result in results: 
            pass #print( ', '.join( [str(result[key]) for key in keys]))
    return results
        


def count_days_with_errors(units, ndays, errors):
    return []
'''
    counter = dict(zip(units, [0]*len(units)))
    full = None
    for unit in units:
        ndays = sum(1 for error in errors if error.get(unit,0)>0)
        counter[unit]=ndays
    print ('counter', counter)
    return
    details = [ error.pop('date') for error in errors]
    for de in details: print ('details', de)
    return
    sql = sql.format(startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d'))
    #print(sql)
    cursor.execute(sql)
    summary = list(cursor.fetchall())
    cursor.close()
    print('summary', summary)
    for s in summary:
        unit, inbed, count = s
        inbed = inbed or 'blank'   # cannot use '' later on, too confusing.
        results[unit][inbed]=count
   
    results['total']['blank']= sum([x.get('blank',0) for x in results.values()])
    results['total']['NO']= sum([x.get('NO',0) for x in results.values()])
    
    #print ('totals', results)
    return results # a list of all units where first entry is unit name and second entry is dictionary of YES/NO/Blank counts
'''
#############################################################################################
#@utilities.record_elapsed_time
# def get_all_patients():
#     patients = models.mydataPatients.objects.all().order_by('LastName', 'FirstName').values()
#     return patients