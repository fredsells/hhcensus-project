import datetime
from . import mydatav02
from . import hharweb2db_api

ONEDAY = datetime.timedelta(days=1)
#SweepTime = datetime.datetime.strptime('2019-11-03 23:45', '%Y-%m-%d %H:%M')
SweepTime = datetime.datetime.now()
Tomorrow = SweepTime.date() + ONEDAY
##########print (SweepTime, Tomorrow )


def execute():
    mydata = mydatav02.MyDataQueryManager()
    #tomorrow = datetime.date.today() + ONEDAY
    #rptdate = tomorrow.strftime('%Y-%m-%d')
    beds = mydata.get_beds_x_patients(SweepTime)
    for bed in beds:
        if bed[2] is None:
            for i in range(2, len(bed)):
                bed[i]=''
            bed[-1] = None  #AdmitDate
    for b in beds: print(b)
    #now = datetime.datetime.now()
    hharweb2db_api.insert_bed_occupancy(beds, Tomorrow.strftime('%Y-%m-%d'))
    print( 'Sweep Completed at', SweepTime, 'repdate=', Tomorrow, 'records=', len(beds))
    return len(beds)


if __name__ == '__main__':
    pass
    nbeds = execute()
