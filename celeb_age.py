import requests
import re
from BeautifulSoup import BeautifulSoup

BSoup = lambda x: BeautifulSoup(x, convertEntities=BeautifulSoup.HTML_ENTITIES)

class NoBirthdayException(Exception):
    pass

def getBDay(person):
    soup = getWikiHTML(person)
    bdays = getAllBDays(soup)

    if not bdays:
        raise NoBirthdayException

    print 'bdays:', bdays
    return bdays[0]

def getWikiHTML(person):
    url = 'https://en.wikipedia.org/wiki/' + getNamePath(person)
    print url

    r = requests.get(url)
    return BSoup(r.text)

def getAllBDays(soup):
    funcs = [
        getBDayString,
        getPersondataBDayString,
        getBornString
    ]

    bdays = []

    for func in funcs:
        bday = func(soup)

        if bday:
            bdays.append(convertBDayStrToDate(bday))

    return bdays


def getNamePath(person):
    return "_".join([name.capitalize() for name in person.split()])


def getBDayString(soup):
    for span in soup.findAll('span'):
        classAttr = span.get('class')
        if classAttr ==  'bday':
            return unescapeHTML(span.string)
            # bday = tuple(int(x) for x in span.string.split('-'))
            # break

    return None

# def getBornRowString(soup):
#     for th in soup.findAll('th'):
#         classAttr = span.get('class')
#         if classAttr ==  'bday':
#             return unescapeHTML(span.string)
#             # bday = tuple(int(x) for x in span.string.split('-'))
#             # break

#     return None

def getBornString(soup):
    for tr in soup.findAll('tr'):
        foundName = False

        for content in tr.contents:
            
            if htmlNameIs(content, 'th') and content.string == 'Born':
                foundName = True

            if foundName and htmlNameIs(content, 'td') and content.string:
                return unescapeHTML(content.string)

            #return unescapeHTML(span.string)

def getPersondataBDayString(soup):
    for tr in soup.findAll('tr'):
        tds = tr.findAll('td')
        if len(tds) == 2 and isDateOfBirthPersondata(tds[0]):
            return unescapeHTML(tds[1].string)
    return None

def htmlNameIs(element, tag):
    try:
        return True if element.name == tag else False
    except:
        return False

def convertBDayStrToDate(bdayString):
    print 'date string:', bdayString

    #'1987-09-09'
    matches = re.search(r"(\d{4})-(\d{2})-(\d{2})", bdayString)
    if matches:
        return tuple(int(x) for x in matches.groups())
    
    #'c. 6210 BC'
    matches = re.search(r"(c\.)?\s*([0-9]+)\s+(\bBC\b|\bAD\b)", bdayString)
    if matches:
        c, year, bc = matches.groups()
        factor = -1 if bc.upper() == 'BC' else 1

        #bc is a negative year
        return (int(year) * factor, 0, 0)

    #'January, 6210 BC'
    matches = re.search(r"(\w+),\s+([0-9]+)\s+(\bBC\b|\bAD\b)", bdayString)
    if matches:
        month, year, bc = matches.groups()
        factor = -1 if bc.upper() == 'BC' else 1

        #bc is a negative year
        return (int(year) * factor, 0, 0)

    #1st century BC
    matches = re.search(r"([0-9])+..\s+century\s+(\bBC\b|\bAD\b)", bdayString)
    if matches:
        century, bc = matches.groups()

        factor = -1 if bc.upper() == 'BC' else 1

        year = ((int(century) - 1) * 100 + 1) * factor

        return (year, 0, 0)


    return None

def unescapeHTML(string):
    return string.replace(u'\xa0', ' ')

def isDateOfBirthPersondata(td):
    return td.get('class') == 'persondata-label' and td.string == 'Date of birth'



    

if __name__ == "__main__":
    main()