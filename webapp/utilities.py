'''
Created on Dec 28, 2019

@author: fsells
'''

import time, sys                                                

def record_elapsed_time(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print ('%r executed in  %2.2f sec' % (method.__name__,  te-ts) )
        return result

    return timed

@record_elapsed_time
def testor(n):
    for i in range(n):
        x = i**i
    return 'done'

def unittest():
    results = testor(1000)
    print(results)
    
if __name__=='__main__':
    unittest()    
    
