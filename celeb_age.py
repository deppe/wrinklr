import requests
from BeautifulSoup import BeautifulSoup

def getPersonInfo(person):

    url = 'https://en.wikipedia.org/wiki/' + getNamePath(person)
    print url

    r = requests.get(url)

    soup = BeautifulSoup(r.text)
    for span in soup.findAll('span'):
        # print span
        if span.get('class') == 'bday':
            bday = span.string

    print bday

    year, month, day = tuple(int(x) for x in bday.split('-'))
    return year, month, day

def getNamePath(person):
    return "_".join([name.capitalize() for name in person.split()])



if __name__ == "__main__":
    main()