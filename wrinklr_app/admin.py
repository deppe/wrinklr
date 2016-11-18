from django.contrib import admin
from wrinklr_app.models import Person
from wrinklr_app.models import Matchup
from wrinklr_app.models import MatchupGuess

# Register your models here.

admin.site.register(Person)
admin.site.register(Matchup)
admin.site.register(MatchupGuess)
