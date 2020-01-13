'''
Created on Dec 28, 2019

@author: fsells

This module bypasses Django ORM and uses pyodbc to increase speed where needed.
'''

import sys, datetime, os
import pyodbc
from webapp import utilities
from webapp import sql_queries_MatrixCare as SQL

BIDW_50582_HebrewHome = ( #this works w/o opening any VPN, etc.
    r'Driver={SQL Server};'
    r'Server=mydatahost5.matrixcarecloud.com,41434\CUSPVIMANDBS05;'
    r'Database=BIDW_50582_HebrewHome;'
    r'Trusted_Connection=yes;'
    
    )

LOCAL_LAPTOP = ( 
        r'DRIVER={SQL Server};'
        r'SERVER=.;'
        r'DATABASE=FredTesting;'
        r'Trusted_Connection=yes;'   )



class DatabaseQueryManager(object):
    '''
    classdocs
    '''


    def __init__(self, conn_str = BIDW_50582_HebrewHome, DEBUG=False):
        self.CONNECTION_STRING = conn_str
        self.DEBUG = DEBUG
        self._get_connection()
        
    def _get_connection(self):
        self.Connection = pyodbc.connect(self.CONNECTION_STRING)
        cursor = self.Connection.cursor()
        cursor.execute("SELECT 1")  #will raise exception if connection fails
        cursor.close()


    def get_something(self, sql, *args, include_column_names=True):
        cursor = self.Connection.cursor()
        cursor.execute(sql, *args)
        records = cursor.fetchall() 
        names = tuple([column[0] for column in cursor.description] )
        #print(names)
        #print (records[0])
        records = [dict(zip(names, row )) for row in records] 

        #for r in records: print(r)
        cursor.close()
        return records
         
    @utilities.record_elapsed_time        
    def get_beds(self):
        records = self.get_something(SQL.ALL_BEDS)
        return records

    @utilities.record_elapsed_time        
    def get_patients(self):
        records = self.get_something(SQL.ALL_PATIENTS)
        return records

    @utilities.record_elapsed_time        
    def get_level_of_care_definitions(self):
        records = self.get_something(SQL.LEVEL_OF_CARE_DEFINITIONS)
        return records

    @utilities.record_elapsed_time        
    def get_leave_of_absence_definitions(self):
        records = self.get_something(SQL.CENSUS_LOA)
        return records
    
    @utilities.record_elapsed_time        
    def get_admit_discharge_locations(self):
        records = self.get_something(SQL.CENSUS_ADMIT_DISCHARGE_LOCATION)
        return records


def unittest():
    mydata = DatabaseQueryManager(conn_str = BIDW_50582_HebrewHome)
    loc = mydata.get_level_of_care_definitions()
    return
    beds = mydata.get_beds()
    patients = mydata.get_patients()
    loa = mydata.get_leave_of_absence_definitions()
    locations = mydata.get_admit_discharge_locations()

if __name__ == '__main__':
    print ('starting sql api')
    unittest()
    print ('ending sql api')