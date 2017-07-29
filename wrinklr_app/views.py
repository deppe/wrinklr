from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from wrinklr_app import slack

import json

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

@csrf_exempt
def slack_slash(request):
    if request.method == 'POST':
        text = request.POST['text']
        response_url = request.POST['response_url']

        name1, name2 = slack.parse_slash_command(text) 

        if not name1 or not name2:
            response = slack.form_parse_error(text)
        else:
            person1 = Person.get_or_create(name1)
            person2 = Person.get_or_create(name2)

            err_names = []
            if not person1: err_names.append(name1)
            if not person2: err_names.append(name2)

            if err_names:
                response = slack.form_error_response(err_names)
            else:
                # Make slack user in case it doesn't exist
                user = User.objects.get_or_create(username='slack')[0]

                matchup = Matchup.get_or_create(person1=person1, 
                                                person2=person2, 
                                                creator=user)
                response = slack.form_slash_response(matchup)

        slack.respond_to_url(response_url, response)

        return HttpResponse()

@csrf_exempt
def slack_action(request):
    if request.method == 'POST':
        payload = json.loads(request.POST['payload'])
        response_url = payload['response_url']
        callback_id = payload['callback_id']
        person_id = payload['actions'][0]['value']

        matchup_id = slack.parse_callback_id(callback_id)
        matchup = Matchup.objects.get(id=matchup_id)
        guess = Person.objects.get(id=person_id)

        response = slack.form_action_response(guess, matchup)
        slack.respond_to_url(response_url, response)

    return HttpResponse()
