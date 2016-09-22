#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test driver for celeb_age.py"""

from __future__ import unicode_literals

import unittest
import celeb_age as ca

class TestCelebAge(unittest.TestCase):
    """Unit test class for celeb_age"""

    def test_ages(self):
        """Test celeb_age.get_bday good input"""

        age = ca.get_bday
        self.assertEqual((1974, 11, 15), age('chad kroeger'))
        self.assertEqual((1935,  1,  8), age('elvis'))
        self.assertEqual((1990,  4, 15), age('EMMA WATSON'))
        self.assertEqual((-1810, 0,  0), age('hammurabi'))
        self.assertEqual((-69,   0,  0), age('Cleopatra'))
        self.assertEqual((-4,    0,  0), age('jesus'))
        self.assertEqual((1162,  0,  0), age('genghis khan'))
        self.assertEqual((1967,  9, 12), age('louis c.k.'))
        self.assertEqual((1951,  9,  2), age('mark harmon'))
        self.assertEqual((1904,  5, 11), age('salvador dalí'))
        self.assertEqual((1757,  1, 11), age('alexander hamilton'))
        self.assertEqual((1920,  5, 18), age('pope john paul ii'))
        self.assertEqual((1927,  4, 16), age('pope benedict xvi'))
        self.assertEqual((1964,  9,  2), age('keanu reeves'))
        self.assertEqual((1412,   1,  6), age('joan of arc'))

    def test_bad_ages(self):
        """Test celeb_age.get_bday bad input"""

        age = ca.get_bday

        #todo: this should be smart enough to figure out madonna
        self.assertRaises(ca.NoPersonDataException, age, 'madonna')
        self.assertRaises(ca.NoPersonDataException, age, 'tower of hanoi')

        self.assertRaises(ca.NoWikiEntryException, age, '')
        self.assertRaises(ca.NoWikiEntryException,  age, 'blahbloooooo')
        

    def test_wiki_url(self):
        """Test celeb_age.get_name_path function"""

        path = ca.get_name_path
        self.assertEqual('Blah_Bloo',           path('blah bloo'))
        self.assertEqual('Blah_Bloo',           path('   blah   bloo    '))
        self.assertEqual('B',                   path('b'))
        self.assertEqual('Louis_C.K.',          path('loUIS c.k.'))
        self.assertEqual('Kareem_Abdul-Jabbar', path('kareem abdul-jabbar'))
        self.assertEqual('Portugal._The_Man',   path('portugal. the man'))
        self.assertEqual('Salvador_Dalí',       path('salvador dalí'))
        self.assertEqual('Blah_MVI',            path('blah mvi'))


    #def test_parse_person_data(self):
    #    """Test celeb_age.parse_person_data function"""

    #    string = '<!--Metadata: see [[Wikipedia:Persondata]]-->\n' \
    #             '{{Persondata\n' \
    #             '|NAME=Deppe, Adam William\n' \
    #             '|ALTERNATIVE NAMES=Deppe\n' \
    #             '|SHORT DESCRIPTION=blah\n' \
    #             '|DATE OF BIRTH=September 09, 1987\n' \
    #             ' |PLACE OF BIRTH=[[Southampton]]\n' \
    #             '|DATE OF DEATH=\n' \
    #             '|PLACE OF DEATH=\n' \
    #             '}}\n' \
    #             '\n' \
    #             '{{DEFAULTSORT:Cleopatra 7}}\n' \
    #             '[[Category:Cleopatra| ]]\n' \
    #             '[[Category:69&nbsp;BC births]]\n' \
    #             '[[Category:30&nbsp;BC deaths]]\n' \

    #    data = ca.parse_person_data(string)

    #    self.assertEqual(data['NAME'], 'Deppe, Adam William')
    #    self.assertEqual(data['ALTERNATIVE NAMES'], 'Deppe')
    #    self.assertEqual(data['SHORT DESCRIPTION'], 'blah')
    #    self.assertEqual(data['DATE OF BIRTH'], 'September 09, 1987')
    #    self.assertEqual(data['PLACE OF BIRTH'], '[[Southampton]]')
    #    self.assertEqual(None, data.get('DATE OF DEATH'))
    #    self.assertEqual(None, data.get('PLACE OF DEATH'))


    def test_unescape_html(self):
        """Test celeb_age.unescape_html function"""

        self.assertEqual('September, 69 BC', ca.unescape_html('September, 69&nbsp;BC'))

    def test_parse_date(self):
        """Test celeb_age.convert_bday_str_to_date godo input"""

        parse = ca.convert_bday_str_to_date

        self.assertEqual((1987, 9, 9), parse('1987-09-09'))
        self.assertEqual((-49, 0, 0),  parse('c. 49 BC'))
        self.assertEqual((49, 0, 0),   parse('49 AD'))
        self.assertEqual((-100, 1, 0), parse('January, 100 BC'))
        self.assertEqual((-300, 0, 0), parse('3rd century BC'))
        self.assertEqual((-300, 0, 0), parse('3rd CentuRY bc'))
        self.assertEqual((1, 0, 0),    parse('1st century'))
        self.assertEqual((1162, 0, 0), parse('c. 1162'))
        self.assertEqual((2001, 0, 0), parse('2001'))
        self.assertEqual((1234, 0, 0), parse('likely 1234'))
        self.assertEqual((-1234, 0, 0), parse('likely 1234 bc'))

    def test_parse_bad_dates(self):
        """Test celeb_age.convert_bday_str_to_date bad input"""

        parse = ca.convert_bday_str_to_date
        self.assertRaises(ca.NoBirthdayException, parse, 'ljkfsd')
        self.assertRaises(ca.NoBirthdayException, parse, '')
        self.assertRaises(ca.NoBirthdayException, parse, None)
        self.assertRaises(ca.NoBirthdayException, parse, 'yyyy-mm-dd')
        self.assertRaises(ca.NoBirthdayException, parse, 'blah 2001 bc')



if __name__ == '__main__':
    unittest.main()
