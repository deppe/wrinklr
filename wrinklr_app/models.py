import logging
import datetime

from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from .celeb_age import get_bday
from .celeb_age import get_wiki_name_path
from .celeb_age import NoPersonDataException, NoWikiEntryException, NoBirthdayException

logger = logging.getLogger('wrinklr')

def validate_birth_date(value):
    usage = 'provide three ints in form "year,month,day"'
    tokens = value.split(',')
    if len(tokens) != 3:
        raise ValidationError(usage)

    try:
        for t in tokens:
            int(t) 
    except ValueError:
        raise ValidationError(usage)


class Person(models.Model):
    name = models.CharField(max_length = 200)
    birth_date = models.CharField(default = '', max_length = 20, validators=[validate_birth_date])
    date_updated = models.DateField(auto_now = True)
    date_created = models.DateField(auto_now_add = True)


    def _age_in_days(self):
        birth_date = Person.birth_date_to_list(self.birth_date)
        now = self._now()
        return self._n_days(now) - self._n_days(birth_date)

    def _age_str(self):
        birth_date = Person.birth_date_to_list(self.birth_date)
        return str(int(self.age_in_days/365)) + ' years old (born ' +  str(birth_date) + ')'

    # Derived properties
    age_in_days = property(_age_in_days)
    age_str = property(_age_str)

    @staticmethod
    def _now():
        now = datetime.datetime.utcnow().date()
        return (now.year, now.month, now.day)

    @staticmethod
    def _n_days(date):
        year, month, day = date
        factor = -1 if year < 0 else 1
        return factor * (abs(year) * 365 + month * 30 + day)
    
    @staticmethod
    def birth_date_to_str(birth_date):
        return ','.join(map(str, birth_date))

    @staticmethod
    def birth_date_to_list(birth_date):
        return [int(x) for x in birth_date.split(',')]

    # This should be used instead of Person() constructor.
    # It will properly format the 'name' field
    @staticmethod
    def init(**kwargs):
        name = kwargs.get('name')
        if name:
            kwargs['name'] = Person.format_name(name)
        return Person(**kwargs)

    @staticmethod
    def format_name(name):
        return get_wiki_name_path(name, " ")

    @staticmethod
    def get_or_create(name):
        person = None
        try:
            #Try to get from db
            name = Person.format_name(name)
            person = Person.objects.get(name=name)
        except ObjectDoesNotExist:
            #create from wikipedia
            person = Person.create_from_wiki(name)
        return person

    @staticmethod
    def create_from_wiki(name):
        try:
            birth_date = get_bday(name)
        except (NoPersonDataException, NoWikiEntryException, NoBirthdayException):
            logger.warn("Could not find wikipedia page for '%s'", name)
            return None

        person = Person(
            name = Person.format_name(name),
            birth_date = Person.birth_date_to_str(birth_date)
        )

        try:
            person.full_clean()
        except ValidationError:
            logger.warn("Could not validate %s", person)
            return None

        #TODO: error handling in save
        person.save()
        return person

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ', '.join(['Name: ' + self.name,
                          'Birthday: ' + self.birth_date,
                          'Updated: ' + repr(self.date_updated),
                          'Created: ' + repr(self.date_created)])

class Matchup(models.Model):
    person1 = models.ForeignKey(Person, models.PROTECT, related_name='person1')
    person2 = models.ForeignKey(Person, models.PROTECT, related_name='person2')
    creator = models.ForeignKey(User, models.PROTECT)
    date_updated = models.DateField(auto_now = True)
    date_created = models.DateField(auto_now_add = True)

    def _older(self):
        if self.person1.age_in_days > self.person2.age_in_days:
            return self.person1
        else:
            return self.person2

    # Derived properties
    older = property(_older)

    class Meta:
        unique_together = ('person1', 'person2')

    @staticmethod
    def get_or_create(person1, person2, creator):
        def get(p1, p2):
            try:
                matchup = Matchup.objects.get(person1=p1, person2=p2)
            except Matchup.DoesNotExist:
                matchup = None
            return matchup

        matchup = get(person1, person2)
        if not matchup:
            matchup = get(person2, person1)

        if not matchup:
            matchup = Matchup(person1=person1, person2=person2, creator=creator)
            matchup.full_clean()
            matchup.save()

        return matchup

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ', '.join(['Person1: ' + self.person1.name,
                          'Person2: ' + self.person2.name,
                          'Creator: ' + self.creator.username,
                          'Updated: ' + repr(self.date_updated),
                          'Created: ' + repr(self.date_created)])

class MatchupGuess(models.Model):
    matchup = models.ForeignKey(Matchup, models.PROTECT)
    user = models.ForeignKey(User, models.PROTECT)
    guess = models.ForeignKey(Person, models.PROTECT)
    result = models.BooleanField(default = False)
    date_updated = models.DateField(auto_now = True)
    date_created = models.DateField(auto_now_add = True)

    def _result_str(self):
        if self.matchup.older.id == self.guess.id:
            return 'Correct, %s is older.' % self.guess.name
        else:
            return 'Incorrect, %s is younger.' % self.guess.name


    # derived properties
    result_str = property(_result_str)
    property

    class Meta:
        unique_together = ('matchup', 'user')

    @staticmethod
    def create_guess(person, matchup, user):
        correct = matchup.older.id == person.id
        guess = MatchupGuess(matchup=matchup, 
                             user=user,
                             guess=person,
                             result=correct)

        guess.full_clean()
        guess.save()
        return guess

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ', '.join(['Person1: ' + self.matchup.person1.name,
                          'Person2: ' + self.matchup.person2.name,
                          'Guess: '   + self.guess.name,
                          'User: '    + self.user.username,
                          'Updated: ' + repr(self.date_updated),
                          'Created: ' + repr(self.date_created)])

