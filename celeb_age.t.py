import unittest
import celeb_age
from BeautifulSoup import BeautifulSoup


class TestCelebAge(unittest.TestCase):
    def testAges(self):
        age = celeb_age.getBDay
        self.assertEqual((1974, 11, 15), age('chad kroeger'))
        self.assertEqual((1935,  1,  8), age('elvis'))
        self.assertEqual((1990,  4, 15), age('EMMA WATSON'))
        self.assertEqual((-1728, 0,  0), age('hammurabi'))
        self.assertEqual((-69,   0,  0), age('Cleopatra'))
        self.assertEqual((-1,   0,  0), age('jesus')) #1st century, 7-2 BC


        self.assertRaises(celeb_age.NoBirthdayException, age, 'tower of hanoi')
        self.assertRaises(celeb_age.NoBirthdayException, age, 'blahbloooooo')

    def testParseBornHtml(self):
        bs = celeb_age.BSoup
        text = ('<tr>\n'
                '<th scope="row" style="text-align:left">Born</th>\n'
                '<td><span style="display:none">(<span class="bday">1974-11-15</span>)</span> November 15, 1974 <span class="noprint ForceAgeToShow">(age&#160;40)</span><br />\n'
                '<a href="/wiki/Hanna,_Alberta" title="Hanna, Alberta">Hanna</a>, <a href="/wiki/Alberta" title="Alberta">Alberta</a>, <a href="/wiki/Canada" title="Canada">Canada</a></td>\n'
                '</tr>\n')

        self.assertEqual(celeb_age.getBDayString(bs(text)), '1974-11-15')

        text = ('<tr>\n'
                '<td class="persondata-label" style="color:#aaa;">Date of birth</td>\n'
                '<td>November 15, 1974</td>\n'
                '</tr>\n')

        self.assertEqual(celeb_age.getPersondataBDayString(bs(text)), 'November 15, 1974')

        text = ('</tr>\n' \
                '<tr>\n' \
                '<td class="persondata-label" style="color:#aaa;">Date of birth</td>\n' \
                '<td>January, 69&#160;BC</td>\n' \
                '</tr>\n')

        self.assertEqual(celeb_age.getPersondataBDayString(bs(text)), 'January, 69 BC')


        text = ('<tr>\n' \
                '<th >Born</th>\n' \
                '<td>7-2 BC</td>\n' \
                '</tr>\n')

        self.assertEqual(celeb_age.getBornString(bs(text)), '7-2 BC')

    def testParseDateString(self):
        parse = celeb_age.convertBDayStrToDate

        self.assertEqual((1987, 9, 9), parse('1987-09-09'))
        self.assertEqual((-49, 0, 0), parse('c. 49 BC'))
        self.assertEqual((49, 0, 0), parse('49 AD'))
        self.assertEqual((-100, 0, 0), parse('January, 100 BC'))
        self.assertEqual((-201, 0, 0), parse('3rd century BC'))


if __name__ == '__main__':
    unittest.main()