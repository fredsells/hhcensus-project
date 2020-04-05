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
    units = models.NightlyBedCheck.objects.order_by('Unit').values_list('Unit', flat=True).distinct()
    return list(units)



def get_beds(unit, repdate=None):
    date = repdate or datetime.date.today()
    queryset = models.NightlyBedCheck.objects.filter(RepDate=date, Unit=unit).order_by('Unit', 'Room')
    for bed in queryset:
        if bed.Inbed not in ('Yes', 'No') and bed.ResidentName != '':
            print ('bed', bed.Unit, bed.Room, bed.Inbed, bed.ResidentName, bed.RepDate, date)
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
 
           


    