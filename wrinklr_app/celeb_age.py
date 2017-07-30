"""Test driver for celeb_age.py"""
# coding=utf-8

import requests
import re
import logging
import pprint
from string import capwords
from bs4 import BeautifulSoup

logger = logging.getLogger('wrinklr')

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

    date = person_data.get('birth_date', '')

    bday = convert_bday_str_to_date(date)

    logger.info('Returning bday %s' % repr(bday))

    return bday

def get_person_data(person):
    """Lookup wikipedia page and return Persondata dictionary"""

    if not person:
        raise NoWikiEntryException("Empty person name")

    request = {
        'format'   : 'json',
        'action'   : 'query',
        'prop'     : 'revisions',
        'titles'   : get_wiki_name_path(person),
        'rvprop'   : 'content',
        'continue' : '',
        'redirects' : '' #necessary to automatically resolve redirects
    }
    
    url = 'http://en.wikipedia.org/w/api.php' 

    # Call API
    result = requests.get(url, params=request)

    final_url = result.url
    logger.info('Requested data from %s' % final_url)

    result = result.json()

    if 'error' in result: 
        logger.error(result['error'])
        raise CelebAgeException(result['error'])

    if 'warnings' in result: 
        logger.warning(result['warnings'])

    for page in result['query']['pages'].values():
        try:
            page_data = page['revisions'][0]['*']
        except KeyError:
            err_str = ('could not parse http response from url %s. result: %s') % (final_url, repr(result['query']))
            raise NoWikiEntryException(err_str)

        #Only care about the first page. It's possible this will have to be extended to parse subsequent pages
        return parse_person_data(page_data)


def parse_person_data(markup):
    """Parse a wikipedia article and return a dictionary of Persondata"""

    infobox = extract_infobox(markup)

    person_data = {}
    for item in infobox.split('\n'):
        matches = re.search(r"^\s*\|\s*(.*?)\s*=(.*)$", item)
        if matches:
            key, value = [val.strip() for val in matches.groups()]
            if key and value:
                person_data[unescape_html(key)] = unescape_html(value)

    logger.debug(pprint.pformat(person_data))
    return person_data

def extract_infobox(string):
    start = find_infobox_start(string)
    end = find_infobox_end(string[start:])
    return string[start:start + end]

def find_infobox_start(string):
    infobox = "{{Infobox "
    start = string.find(infobox)

    if start == -1:
        raise NoPersonDataException('No %s item' % infobox)

    return start

def find_infobox_end(string):
    if string[:2] != '{{':
        raise NoPersonDataException('Malformed input to find_infobox_end' % infobox)

    stack = []
    for match in re.finditer(r"({{|}})", string):
        s = match.group(1)
        if s == '{{':
            stack.append(s)
        elif s == '}}':
            stack.pop()
            if len(stack) == 0:
                return match.end()

    raise NoPersonDataException('Malformed input to find_infobox_end' % infobox)

def get_wiki_name_path(string, delim='_'):
    """Convert a person name string into a wikipedia path"""

    capitalized_words = []
    for name in string.split():
        if name.find('.') != -1:
            capitalized_words.append(capwords(name, '.'))
        elif name.find('-') != -1:
            capitalized_words.append(capwords(name, '-'))
        elif is_roman_numeral(name):
            capitalized_words.append(name.upper())
        else:
            capitalized_words.append(name.capitalize())

    string = delim.join(capitalized_words)
    return string

def is_roman_numeral(string):
    if not string:
        return False

    roman_nums = "ivxlcdm"
    return all(c in roman_nums for c in string)

def convert_bday_str_to_date(bday_string):
    """Extract year, month, day from date string"""

    logger.debug('Parsing date string: "%s"' % bday_string)

    if not bday_string:
        err_str = 'Could not parse date from "%s"' % bday_string
        logger.warning(err_str)
        raise NoBirthdayException(err_str)

    bday_string = re.sub("<.*>", "", bday_string)

    date = parse_standard_date(bday_string)

    if not date:
        date = parse_nonstandard_date(bday_string)

    if not date:
        raise NoBirthdayException

    return date

def parse_standard_date(bday_string):
    match = re.match("^\{\{(.*)\}\}.*$", bday_string)

    if not match:
        return

    bday_string = match.group(1)
        
    def is_int(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    date = filter(is_int, bday_string.split('|'))
    date = tuple(map(int, date))

    date += (0, 0)
    return date[:3]

def parse_nonstandard_date(bday_string):
    bday_string = re.sub(r"(c\.|likely|\(age \d+\))", "", bday_string, flags=re.IGNORECASE).strip()

    bday_string = re.sub(r"\{\{(efn|sfn|notelist|reflist|citation).*", "", bday_string, flags=re.IGNORECASE).strip()
    bday_string = re.sub(r"\<ref.*", "", bday_string, flags=re.IGNORECASE).strip()
    bday_string = re.sub(r"(\{\{|\}\})", "", bday_string).strip()
    bday_string = re.sub(r" or .*", "", bday_string).strip()

    regex = {
        #'2001-01-15'
        (r"^(\d{4})-(\d{2})-(\d{2})$", ('year', 'month', 'day')),

        # January 15, 2001
        (r"^(\w+)\s+(\d+),\s+(\d+)$", ('monthStr', 'day', 'year')),

        # 15 January 2001 BC
        (r"^(\d+)\s+(\w+)\s+(\d+)\s*(\bBC\b|\bAD\b)?$", ('day', 'monthStr', 'year', 'bc')),

        # 15 January BC 2001
        (r"^(\d+)\s+(\w+)\s+(\bBC\b|\bAD\b)\s+(\d+)$", ('day', 'monthStr', 'bc', 'year')),

        #January, 2001 BC
        (r"^(\w+),?\s+(\d+)\s*(\bBC\b|\bAD\b)?$", ('monthStr', 'year', 'bc')),

        #c. 2001 BC
        #likely 2001 BC
        (r"^([0-9]+)\s*(\bBC\b|\bAD\b|\bBCE\b)?$", ('year', 'bc')),

        #2001st cenutury BC
        (r"^([0-9])+..\s+century\s*(\bBC\b|\bAD\b)?$", ('century', 'bc'))
    }

    tokens = bday_string.split('|')

    for token in tokens:
        date = None
        for expr, groups in regex:
            matches = re.search(expr, token, flags=re.IGNORECASE)

            if matches:
                matches_dict = dict(zip(groups, matches.groups()))

                logger.debug('hit: "%s" "%s"' % (expr,  repr(matches.groups())))
                date = create_date_from_matches(matches_dict)

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

    is_bc = era and era.upper()[:2] == 'BC'

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

    soup = BeautifulSoup(html, "html.parser")

    if soup.string:
        return soup.string.replace(u'\xa0', ' ')
    else:
        return html

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

