from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from .models import Person
from .models import Matchup
from .models import MatchupGuess

def input_celebs(request):
    if request.method == 'POST':
        return input_celebs_post(request)
    elif request.method == 'GET':
        return input_celebs_render(request)

@login_required
def input_celebs_post(request):
    name1, name2 = request.POST['person1'], request.POST['person2']
    person1, person2 = Person.get_or_create(name1), Person.get_or_create(name2)

    if not person1 or not person2:
        def create_dict(n, p):
            return {'name': n, 'valid': bool(p)}

        return input_celebs_render(request,
                                   person1=create_dict(name1, person1), 
                                   person2=create_dict(name2, person2))

    else:
        matchup = Matchup.get_or_create(person1=person1, 
                                        person2=person2, 
                                        creator=request.user)
        return redirect('wrinklr_app:matchup', matchup_id=matchup.id)

def input_celebs_render(request, person1=None, person2=None):
        guesses = []
        if not request.user.is_anonymous():
            guesses = MatchupGuess.objects.filter(user=request.user)
        open_matchups = Matchup.objects.exclude(id__in=[x.matchup.id for x in guesses])

        context = {
            'guesses': guesses,
            'open_matchups': open_matchups,
            'person1': person1,
            'person2': person2
        }

        return render(request, 'wrinklr_app/input_celebs.html', context)




def age(request):
    if 'name' in request.GET:
        person = Person.create_from_wiki(request.GET['name'])

    if not person:
        person = Person.init(name='Error')

    context = {
        'person': person
    }
    return render(request, 'wrinklr_app/age.html', context)

def matchup(request, matchup_id):
    if request.method == 'POST':
        return matchup_post(request, matchup_id)

    elif request.method == 'GET':
        matchup = get_object_or_404(Matchup, id=matchup_id)

        user_guess = None
        if not request.user.is_anonymous():
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
        context = {
            'form': UserCreationForm(),
            'navbar_text': 'Register'
        }
        return render(request, 'wrinklr_app/register.html', context)

def navbar_login(request):
    if request.method == 'GET':
        if 'login' in request.GET:
            return redirect('wrinklr_app:login')
        elif 'register' in request.GET:
            return redirect('wrinklr_app:register')
        elif 'logout' in request.GET:
            return redirect('wrinklr_app:logout')

