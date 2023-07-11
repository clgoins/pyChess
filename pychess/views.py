from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import *
from . import chessEngine

# Create your views here.


def index(request):
    return render(request, 'pychess/index.html')

def loginView(request):

    if request.method == 'POST':
        # Grab users info from POST request data
        username = request.POST['username']
        password = request.POST['password']

        # Attempt to authenticate user
        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request,user)
            return redirect(index)
        else:
            return render(request, 'pychess/login.html', {"message":"Invalid username or password."})

    else:
        return render(request, 'pychess/login.html')

def logoutView(request):
    logout(request)
    return redirect(index)


def register(request):
    if request.method == "POST":
        # Grab the new users info from the POST request data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        passwordConfirm = request.POST['passwordConfirm']

        # Make sure the password matches the confirmation password
        if(password != passwordConfirm):
            return render(request, 'pychess/register.html', {"message":"Passwords do not match."})
        
        # Attempt to add user to database
        try:
            newUser = User.objects.create_user(username,email,password)
            newUser.save()
        except IntegrityError:
            return render(request, 'pychess/register.html', {"message":"Username already exists."})
        
        login(request, newUser)

        return redirect(index)
                          
    else:
        return render(request, 'pychess/register.html')
    

def newGame(request):
    return render(request, 'pychess/play.html')

def localGame(request):
    pass

def networkGame(request):
    pass

def review(request):
    return render(request, 'pychess/review.html')

def spectate(request):
    return render(request, 'pychess/spectate.html')
