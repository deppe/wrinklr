from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from .models import Person
from .models import Matchup
from .models import MatchupGuess

def input_celebs(request, person1=None, person2=None):
    if request.method == 'POST':
        return input_celebs_post(request)
    elif request.method == 'GET':
        context = {
            'matchups': Matchup.objects.all()
        }

        return render(request, 'wrinklr_app/input_celebs.html', context)

@login_required
def input_celebs_post(request):
    name1, name2 = request.POST['person1'], request.POST['person2']
    person1, person2 = Person.get_or_create(name1), Person.get_or_create(name2)

    if not person1 or not person2:
        def create_dict(n, p):
            return {'name': n, 'valid': bool(p)}

        context = {
            'person1': create_dict(name1, person1),
            'person2': create_dict(name2, person2),
            'matchups': Matchup.objects.all()
        }
        return render(request, 'wrinklr_app/input_celebs.html', context)
    else:
        matchup = Matchup.get_or_create(person1=person1, 
                                        person2=person2, 
                                        creator=request.user)
        return redirect('wrinklr_app:matchup', matchup_id=matchup.id)


def age(request):
    person1 = Person.get_or_create(request.GET['person1'])
    person2 = Person.get_or_create(request.GET['person2'])
    return render_age(request, person1, person2)

def render_age(request, person1, person2):
    person1 = get_celeb_obj(person1)
    person2 = get_celeb_obj(person2)

    olderStr = "same age"
    if person1['n_days'] > person2['n_days']:
        name = person1['name']
    elif person1['n_days'] < person2['n_days']:
        name = person2['name']

    olderStr = name + ' is older'

    context = {
        'celebs': [person1, person2],
        'older': olderStr
    }

    return render(request, 'wrinklr_app/age.html', context)

def matchup(request, matchup_id):
    if request.method == 'POST':
        return matchup_post(request, matchup_id)

    elif request.method == 'GET':
        matchup = get_object_or_404(Matchup, id=matchup_id)
        user_guess = MatchupGuess.objects.filter(matchup=matchup, user=request.user)

        if user_guess:
            return redirect('wrinklr_app:matchup_results', matchup_id=matchup_id)
        else:
            context = { 
                'matchup': matchup
            }
            return render(request, 'wrinklr_app/matchup.html', context)

@login_required
def matchup_post(request, matchup_id):
    person = Person.objects.get(id=request.POST['guess_person_id'])
    matchup = Matchup.objects.get(id=matchup_id)
    MatchupGuess.create_guess(person, matchup, request.user)

    return redirect('wrinklr_app:matchup_results', matchup_id=matchup.id)

@login_required
def matchup_results(request, matchup_id):
    matchup = get_object_or_404(Matchup, id=matchup_id)
    guesses = MatchupGuess.objects.filter(matchup=matchup)
    user_guess = guesses.filter(user=request.user)

    if not user_guess:
        return redirect('wrinklr_app:matchup', matchup_id=matchup_id)
    else:
        context = {
            'user_guess': user_guess[0],
            'matchup': matchup,
            'guesses': guesses
        }
        return render(request, 'wrinklr_app/matchup_results.html', context)


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('wrinklr_app:input_celebs')

    elif request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

