from django.shortcuts import redirect

def home(request):
    return redirect('wrinklr_app:input_celebs')

