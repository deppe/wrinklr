from django.shortcuts import render
import datetime

import celeb_age.celeb_age as celeb_age

# Create your views here.

def input_celebs(request):
    return render(request, 'wrinklr_app/input_celebs.html', {})

def age(request):
    celeb1 = getCelebObj(request.GET['celeb1'])
    celeb2 = getCelebObj(request.GET['celeb2'])

    olderStr = "same age"
    if celeb1['nDays'] > celeb2['nDays']:
        olderStr = celeb1['name'] + ' is older'
    elif celeb1['nDays'] < celeb2['nDays']:
        olderStr = celeb2['name'] + ' is older'

    context = {
        'celebs': [celeb1, celeb2],
        'older': olderStr
    }

    print context
    return render(request, 'wrinklr_app/age.html', context)

def getCelebObj(name):
    try:
        birthdate = celeb_age.getBDay(name)
        ageStr, nDays = getAgeInfo(birthdate)
    except (celeb_age.NoPersonDataException, celeb_age.NoWikiEntryException, celeb_age.NoBirthdayException):
        ageStr = '?'
        nDays = 0

    return {
        'name': name, 
        'age': ageStr,
        'nDays': nDays
    }

def getAgeInfo(birthdate):
    now = getNow()
    days =  nDays(now) - nDays(birthdate)

    ageStr = str(days/365) + ' years old (born ' +  str(birthdate) + ')'
    return ageStr, days

def getNow():
    now = datetime.datetime.utcnow().date()
    print now
    return (now.year, now.month, now.day)

def nDays(date):
    year, month, day = date
    factor = -1 if year < 0 else 1

    return factor * (abs(year) * 365 + month * 30 + day)



