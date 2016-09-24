from django.shortcuts import render
import datetime

import celeb_age.celeb_age as celeb_age

# Create your views here.

def input_celebs(request):
    return render(request, 'wrinklr_app/input_celebs.html', {})

def age(request):
    celeb1 = get_celeb_obj(request.GET['celeb1'])
    celeb2 = get_celeb_obj(request.GET['celeb2'])

    olderStr = "same age"
    if celeb1['nDays'] > celeb2['nDays']:
        olderStr = celeb1['name'] + ' is older'
    elif celeb1['nDays'] < celeb2['nDays']:
        olderStr = celeb2['name'] + ' is older'

    context = {
        'celebs': [celeb1, celeb2],
        'older': olderStr
    }

    return render(request, 'wrinklr_app/age.html', context)

def get_celeb_obj(name):
    try:
        birthdate = celeb_age.get_bday(name)
        ageStr, nDays = get_age_info(birthdate)
    except (celeb_age.NoPersonDataException, celeb_age.NoWikiEntryException, celeb_age.NoBirthdayException):
        ageStr = '?'
        nDays = 0

    return {
        'name': name, 
        'age': ageStr,
        'nDays': nDays
    }

def get_age_info(birthdate):
    now = get_now()
    days =  nDays(now) - nDays(birthdate)

    ageStr = str(int(days/365)) + ' years old (born ' +  str(birthdate) + ')'
    return ageStr, days

def get_now():
    now = datetime.datetime.utcnow().date()
    return (now.year, now.month, now.day)

def nDays(date):
    year, month, day = date
    factor = -1 if year < 0 else 1

    return factor * (abs(year) * 365 + month * 30 + day)



