'''
Business logic to connect views/urls to database/models
This module SHOULD contain no logic specific to the 
web api
 Author: Fred Sells  10/29/2019
 '''



import sys, os, datetime, random, calendar, itertools


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
    units = models.NightlyBedCheck.objects.filter(Obsolete=obsolete).order_by('Unit').values_list('Unit', flat=True).distinct()
    return list(units)


# def get_errors_by_day_and_unit(startdate, enddate):
#     results = []
#     date = startdate
#     while date <= enddate:
#         totals = models.NightlyBedCheck.objects.filter(RepDate=date).exclude(Inbed='YES').exclude(Inbed='NO', Reason='').values('Unit').annotate(total=Count('RepDate'))
#         errors = dict(date=date)
#         for total in totals:
#             errors[total['Unit']]=total['total']
#         results.append ( errors)
#         date += ONEDAY
#     return results


# def get_error_summary(units, startdate, enddate):
#     ndays = enddate-startdate
#     ndays = 1+ndays.days
#     print(startdate, enddate, ndays)
#     census = models.NightlyBedCheck.objects.filter(RepDate__range=[startdate, enddate]).exclude(ResidentNumber='')
#     partial_census = dict(zip(units,[0]*len(units)))
#     full_census = dict(zip(units,[0]*len(units)))
#     totals = dict(zip(units,[ndays]*len(units)))
#     nonedone = dict(zip(units,[ndays]*len(units)))
#     totals['title'] = 'Totals'
#     full_census['title']='Days of Full Census Done'
#     partial_census['title'] = 'Days of Partial Census Done'
#     nonedone['title'] = 'Days of No Census Done'
#     date = startdate
#     days_with_census = census.values('RepDate').distinct().count()#aggregate(days=Count('SweepTime'))
#     print(ndays, days_with_census, '<<<<<<<<<<<<<<<<<<<<<<<<<<')
#     while date <= enddate:
#         #print(date)
#         aday = census.filter(RepDate=date)
#         for unit in units:
#             aunit = aday.filter(Unit=unit)
#             if aunit.exclude(Inbed='YES').exclude(Inbed='NO', Reason='').values('Unit').count():
#                 partial_census[unit] += 1
#             if aunit.filter(Inbed='YES').values('Unit').count():
#                 full_census[unit] += 1
#             if aunit.filter(Inbed='NO').exclude(Reason='').values('Unit').count():
#                 full_census[unit] += 1
#             nonedone[unit] = 1+ndays-days_with_census-full_census[unit]
            
#         date += ONEDAY
#     keys = ['title', 'total'] + units
#     results = []
    
#     for census in [full_census, nonedone, partial_census, totals]:
#         census['total'] = sum(census[unit] for unit in units)
#         results.append(census)
    
#     for key in keys:
#         for result in results: 
#             pass #print( ', '.join( [str(result[key]) for key in keys]))
#     return results
        


# def count_days_with_errors(units, ndays, errors):
#     return []
# '''
#     counter = dict(zip(units, [0]*len(units)))
#     full = None
#     for unit in units:
#         ndays = sum(1 for error in errors if error.get(unit,0)>0)
#         counter[unit]=ndays
#     print ('counter', counter)
#     return
#     details = [ error.pop('date') for error in errors]
#     for de in details: print ('details', de)
#     return
#     sql = sql.format(startdate.strftime('%Y-%m-%d'), enddate.strftime('%Y-%m-%d'))
#     #print(sql)
#     cursor.execute(sql)
#     summary = list(cursor.fetchall())
#     cursor.close()
#     print('summary', summary)
#     for s in summary:
#         unit, inbed, count = s
#         inbed = inbed or 'blank'   # cannot use '' later on, too confusing.
#         results[unit][inbed]=count
   
#     results['total']['blank']= sum([x.get('blank',0) for x in results.values()])
#     results['total']['NO']= sum([x.get('NO',0) for x in results.values()])
    
#     #print ('totals', results)
#     return results # a list of all units where first entry is unit name and second entry is dictionary of YES/NO/Blank counts
# '''
#############################################################################################
#@utilities.record_elapsed_time
# def get_all_patients():
#     patients = models.mydataPatients.objects.all().order_by('LastName', 'FirstName').values()



#     return patients


def get_beds(unit, obsolete=0, date=None):
    queryset = models.NightlyBedCheck.objects.filter(Obsolete=obsolete, Unit=unit).order_by('Unit', 'Room')
    return queryset

class MonthlySummaryComputer(object):
    @utilities.record_elapsed_time
    def __init__(self, startdate):
        # self.units=get_units()
        ndays = calendar.monthrange(startdate.year, startdate.month)[1]
        enddate = datetime.date(year=startdate.year, month=startdate.month, day=ndays)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxdaterange', startdate, enddate, ndays)
        queryset = models.NightlyBedCheck.objects.filter(RepDate__range=[startdate, enddate]).order_by('RepDate', 'Unit')
        units = queryset.order_by('Unit').values_list('Unit', flat=True).distinct()
        repdates =  queryset.order_by('RepDate').values_list('RepDate', flat=True).distinct()
        #print(len(queryset), units)
        #print (repdates)
        zeroes = [0] * len(units)
        grid = self.get_empty_grid(repdates, units)
        grid = self.populate_grid(grid, queryset)
        self.grid=grid
        self.units_with_errors = dict(zip(units, zeroes))
        self.total_days_with_nothing_done_by_unit = dict(zip(units, zeroes))
        self.get_totals(units, grid)
        print('errors', self.units_with_errors)
        print('nonedone', self.total_days_with_nothing_done_by_unit)

    def get_empty_grid(self, repdates, units):
        grid = {}
        zeroes = [0] * len(units)
        for date in repdates:
                grid[date]=dict(zip(units, zeroes))
        return grid

    def populate_grid(self, grid, queryset):
        residents = queryset.exclude(ResidentName='').exclude( Inbed='YES')
        #residents = residents.filter(Unit='GL')  #simplify for testing
        for x in residents:
            if (x.Inbed=='') or (x.Inbed=='No' and x.Reason != ''): 
                pass
            else:
                print('resident',x.ResidentName, x.RepDate, x.Unit, x.Inbed, x.Reason)
                grid[x.RepDate][x.Unit] += 1
        return grid
    
    def get_totals(self, units, grid):
        self.maxdays = max_days = len(set(grid.keys()))
        zeroes = [0] * len(units)
        fullcensus = dict(zip(units, zeroes))
        nocensus = dict(zip(units, zeroes))
        partialcensus = dict(zip(units, zeroes))
        totals = dict(zip(units, zeroes))
        for row in grid.values():
            for unit in units:
                if row[unit] == max_days:        nocensus[unit] += 1
                elif row[unit] > 0:              partialcensus[unit] += 1
                else:                            fullcensus[unit] += 1
                totals[unit] = max_days
        self.totals = [fullcensus, nocensus, partialcensus, totals]
        for row in self.totals:  row['total']= sum(row.values())
        fullcensus['title'] = 'Days of Full Census Done'
        nocensus['title'] = 'Days of No Census Done'
        partialcensus['title'] = 'Days of Partial Census Done'
        totals['title'] = 'Totals'
        fullcensus['background'] = 'green'
        nocensus['background'] = '#cc3300'
        partialcensus['background'] = 'red'
        totals['background'] = 'blue'
 
 
    def print_grid(self, grid):
        print ('----------------------------------------------------')
        for date in grid.keys():
            print(date, grid[date])

    def get_details_by_day_x_unit(self):
        return self.grid
 
           


    