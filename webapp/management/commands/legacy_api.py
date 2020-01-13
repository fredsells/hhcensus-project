'''
Created on Nov 28, 2019

@author: fsells
'''

conn_str = (r'DRIVER={SQL Server};'
#works                r'SERVER=PS-6KR5WF2;'
                r'SERVER=.;'  #Also works and is not dependent on computer name for a local server version.
#Fails                r'SERVER=.\localhost;'
                
                r'DATABASE=HHdev;'
                r'Trusted_Connection=yes;'    )

def get_legacy_data(conn_str, startdate, enddate):
    pass

if __name__ == '__main__':
    pass