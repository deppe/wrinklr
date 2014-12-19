import requests
import re
from BeautifulSoup import BeautifulSoup

class NoBirthdayException(Exception):
    pass

def getPersonInfo(person):

    url = 'https://en.wikipedia.org/wiki/' + getNamePath(person)
    print url

    r = requests.get(url)
    soup = BeautifulSoup(r.text)

    bday = getBDay(soup)
    if not bday:
        bday = getPersondataBDay(soup)

    if bday is None:
        raise NoBirthdayException

    print bday
    return bday

def getNamePath(person):
    return "_".join([name.capitalize() for name in person.split()])


def getBDay(soup):
    bday = None
    for span in soup.findAll('span'):

        classAttr = span.get('class')
        if classAttr ==  'bday':
            bday = tuple(int(x) for x in span.string.split('-'))
            break

    return bday

def getPersondataBDay(soup):
    bday = None
    for tr in soup.findAll('tr'):

        tds = tr.findAll('td')

        if len(tds) == 2:
            if isDateOfBirthPersondata(tds[0]):
                birthdateStr = tds[1].string

                #handle the 'c. 1728 BC' case
                result = re.match("c. ([0-9]+) (BC)?", birthdateStr)
                if result:
                    year, bc = result.groups()
                    factor = -1 if bc else 1

                    #bc is a negative year
                    bday = (int(year) * factor, 0, 0)
                    break
    return bday

def isDateOfBirthPersondata(td):
    return td.get('class') == 'persondata-label' and td.string == 'Date of birth'

if __name__ == "__main__":
    main()