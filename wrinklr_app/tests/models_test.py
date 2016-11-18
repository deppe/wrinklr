from django.test import TestCase
from django.contrib.auth.models import User

import logging
import sys

from unittest.mock import patch

from django.core.exceptions import ValidationError
from ..models import Person
from ..models import Matchup
from ..models import MatchupGuess
from ..celeb_age import NoWikiEntryException

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class TestModels(TestCase):
    def test_person(self):
        p = Person()
        p.save()
        p = Person.objects.all()[0]

        self.assertEqual(p.name, "")
        self.assertEqual(p.birth_date, "")
    
    def test_person_birth_date(self):
        def test_date(date):
            Person(name = "blah", birth_date = date).full_clean()

        #bad dates
        with self.assertRaises(ValidationError):
            test_date("")
            test_date("blah")
            test_date("1")
            test_date("1,2")
            test_date("1,2,")
            test_date("1,2,3,")
            test_date("1,2,3,4")
            test_date("1,2,3,4,5")
            test_date("1,2a,3")
            test_date("1.0,2.0,3.0")

        #good dates
        test_date("1,2,3")
        test_date("-1,2,3")

    def test_fetch_person(self):
        Person(name = "blah", birth_date="1,2,3").save()
        p = Person.get_or_create("blah")
        self.assertEqual(p.birth_date, "1,2,3")

    @patch('wrinklr_app.models.get_bday')
    def test_fetch_person_wiki(self, mock_get_bday):
        mock_get_bday.return_value = (1,2,3)
        p = Person.get_or_create("blah")
        mock_get_bday.assert_called_once_with("blah")
        self.assertEqual(p.birth_date, "1,2,3")

        #Fetch again and get_bday should still only be called once
        p = Person.get_or_create("blah")
        mock_get_bday.assert_called_once_with("blah")
        self.assertEqual(p.birth_date, "1,2,3")

    @patch('wrinklr_app.models.get_bday')
    def test_fetch_person_no_wiki(self, mock_get_bday):
        mock_get_bday.side_effect = NoWikiEntryException
        p = Person.get_or_create("blah")
        self.assertIsNone(p)

    def create_basic_matchup(self):
        p1 = Person(name = "blah1", birth_date="1,1,1")
        p1.save()

        p2 = Person(name = "blah2", birth_date="2,2,2")
        p2.save()

        u = User(username="blah")
        u.save()

        m = Matchup(person1=p1, person2=p2, creator=u)
        m.save()
        return m, p1, p2, u

    def test_fetch_matchup(self):
        m, p1, p2, u = self.create_basic_matchup()

        def assert_matchup(m):
            self.assertEqual(m.person1.name, "blah1")
            self.assertEqual(m.person1.birth_date, "1,1,1")
            self.assertEqual(m.person2.name, "blah2")
            self.assertEqual(m.person2.birth_date, "2,2,2")
            self.assertEqual(m.creator.username, "blah")

        # Assert get_or_create returns the matchup
        m = Matchup.get_or_create(p1, p2, u)
        assert_matchup(m)

        # Assert second save returns first matchup
        u = User(username="blah2")
        m = Matchup.get_or_create(p1, p2, u)
        assert_matchup(m)

        # Assert swapping order of p1, p2 still gets the matchup
        m = Matchup.get_or_create(p2, p1, u)
        assert_matchup(m)

        # Assert all previous get_or_create only created one matchup
        self.assertEqual(len(Matchup.objects.all()), 1)

        # Assert we can't we can't insert the same matchup twice
        with self.assertRaises(ValidationError):
            Matchup(person1=p1, person2=p2, creator=u).full_clean()
        with self.assertRaises(ValidationError):
            Matchup(person1=p2, person2=p1, creator=u).full_clean()
    
    def test_matchup_guess(self):
        m, p1, p2, u = self.create_basic_matchup()
        g = MatchupGuess.create_guess(p1, m, u)
        self.assertTrue(g.result)

    def test_matchup_bad_guess(self):
        m, p1, p2, u = self.create_basic_matchup()
        g = MatchupGuess.create_guess(p2, m, u)
        self.assertFalse(g.result)

