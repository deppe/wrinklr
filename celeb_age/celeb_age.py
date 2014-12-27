"""Test driver for celeb_age.py"""
# coding=utf-8

from __future__ import unicode_literals

import requests
import re
from string import capwords
from BeautifulSoup import BeautifulSoup
#from urllib2 import quote

class CelebAgeException(Exception):
    """Generic exception for the celeb_age module"""
    pass

class NoBirthdayException(CelebAgeException):
    """Failure to parse birthday string"""
    pass

class NoPersonDataException(CelebAgeException):
    """Failure to parse Persondata from wiki"""
    pass

class NoWikiEntryException(CelebAgeException):
    """Failure to find wikipedia page"""
    pass

def get_bday(person): 
    """Get birthday for person using wikipedia"""

    person_data = get_person_data(person)

    date = person_data.get('DATE OF BIRTH', '')

    bday = convert_bday_str_to_date(date)

    return bday

def get_person_data(person):
    """Lookup wikipedia page and return Persondata dictionary"""

    if not person:
        raise NoWikiEntryException("Empty person name")

    request = {
        'format'   : 'json',
        'action'   : 'query',
        'prop'     : 'revisions',
        'titles'   : get_name_path(person),
        'rvprop'   : 'content',
        'continue' : '',
        'redirects' : '' #necessary to automatically resolve redirects
    }

    
    url = 'http://en.wikipedia.org/w/api.php' 

    # Call API
    result = requests.get(url, params=request)

    final_url = result.url
    print 'Requested data from %s' % final_url

    result = result.json()

    if 'error' in result: 
        raise CelebAgeException(result['error'])

    if 'warnings' in result: 
        print result['warnings']

    for page in result['query']['pages'].itervalues():
        try:
            page_data = page['revisions'][0]['*']
        except KeyError:
            err_str = ('could not parse http response from url %s. result: %s') % (final_url, repr(result['query']))
            raise NoWikiEntryException(err_str)

        #Only care about the first page. It's possible this will have to be extended to parse subsequent pages
        return parse_person_data(page_data)


def parse_person_data(markup):
    """Parse a wikipedia article and return a dictionary of Persondata"""

    start = markup.find('{{Persondata')
    if start == -1:
        raise NoPersonDataException('No {{Persondata ... }} item')

    end = markup.find('}}', start) - 1

    person_data = {}
    for item in markup[start : end].split('\n'):
        matches = re.search(r"^\s*\|(.*)=(.*)$", item)
        if matches:
            key, value = [val.strip() for val in matches.groups()]
            if key and value:
                person_data[unescape_html(key)] = unescape_html(value)

    return person_data

def get_name_path(string):
    """Convert a person name string into a wikipedia path"""

    capitalized_words = []
    for name in string.split():
        if name.find('.') != -1:
            capitalized_words.append(capwords(name, '.'))
        elif name.find('-') != -1:
            capitalized_words.append(capwords(name, '-'))
        else:
            capitalized_words.append(name.capitalize())

    string = '_'.join(capitalized_words)
    return string
    #return quote(string.encode('utf-8'))

def convert_bday_str_to_date(bday_string):
    """Extract year, month, day from date string"""

    print 'parsing date string: "%s"' % bday_string

    if not bday_string:
        err_str = 'Could not parse date from "%s"' % bday_string
        raise NoBirthdayException(err_str)

    regex = {
        #'2001-01-15'
        (r"^(\d{4})-(\d{2})-(\d{2})$", ('year', 'month', 'day')),

        # January 15, 2001
        (r"^(\w+)\s+(\d+),\s+(\d+)$", ('monthStr', 'day', 'year')),

        # 15 January 2001
        (r"^(\d+)\s+(\w+)\s+(\d+)$", ('day', 'monthStr', 'year')),

        #January, 2001 BC
        (r"^(\w+),\s+(\d+)\s+(\bBC\b|\bAD\b)?$", ('monthStr', 'year', 'bc')),

        #c. 2001 BC
        (r"^(c\.)?\s*([0-9]+)\s*(\bBC\b|\bAD\b)?$", ('_', 'year', 'bc')),

        #2001st cenutury BC
        (r"^([0-9])+..\s+century\s*(\bBC\b|\bAD\b)?$", ('century', 'bc'))
    }

    date = None
    for expr, groups in regex:
        matches = re.search(expr, bday_string, flags=re.IGNORECASE)

        if matches:
            matches_dict = dict(zip(groups, matches.groups()))

            print 'hit: "%s" "%s"' % (expr,  repr(matches.groups()))
            date = create_date_from_matches(matches_dict)

    if not date:
        raise NoBirthdayException

    return date

#todo: this should be a class
def create_date_from_matches(matches):
    """Extract year, month, day from date string regex matches"""
    day = int(matches.get('day', 0))
    month = get_month(matches)
    year = get_year(matches)

    return year, month, day


def get_month(matches):
    """Extract integer month [1-12] from date string regex matches"""
    month = matches.get('monthStr')

    if month:
        month = month_to_int(month)
    else:
        month = matches.get('month', 0)

    return int(month)

def get_year(matches):
    """Extract integer year from date string regex matches. 
       BC years are negative.
       If only a century is given, return the earliest year for that century.
       2nd Century -> year 101, 2nd Century BC -> year -200"""

    era = matches.get('bc', '')
    century = matches.get('century')

    is_bc = era and era.upper() == 'BC'

    if century:
        if is_bc:
            year = int(century) * 100
        else:
            year = ((int(century) - 1) * 100) + 1
    else:
        year = int(matches.get('year'))

    factor = -1 if is_bc else 1
    return year * factor

def unescape_html(html):
    """Unescape whitespace in html string"""

    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    return soup.string.replace(u'\xa0', ' ')

def month_to_int(month):
    """Convert month string to integer [1-12]"""
    return {
        'January':   1,
        'February':  2,
        'March':     3,
        'April':     4,
        'May':       5,
        'June':      6,
        'July':      7,
        'August':    8,
        'September': 9,
        'October':  10,
        'November': 11,
        'December': 12,
    }[month]

