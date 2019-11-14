from django import template 

register = template.Library()


def lookup(somedictionary, somekey):
    #return 77
    return somedictionary.get(somekey, None)

register.filter('lookup', lookup)