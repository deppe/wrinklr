from django.db import models

# Create your models here.

class Person(models.Model):
    name = models.CharField(max_length = 200)
    birthday = models.CommaSeparatedIntegerField(max_length = 3)
    date_updated = models.DateField(auto_now = True)
    date_created = models.DateField(auto_now_add = True)


    def __repr__(self):
        return ' '.join(['Name: ' + repr(self.name),
                        'Birthday: ' + repr(self.birthday),
                        'Date Updated: ' + repr(self.date_updated),
                        'Date Created: ' + repr(self.date_created)])
