from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import *
from . import chessEngine
import string, random

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
    

def play(request):
    return render(request, 'pychess/play.html')


def localGame(request):
    return render(request, 'pychess/localGame.html', {'board':chessEngine.generateBoard(1)})


def networkGame(request):
    if request.method == 'GET':
        if request.GET['g'] == 'new':
            # Create and render a new game, along with a message to the user containing their room code to share with their friend

            # Generate a room code (random string of characters and numbers, 6 characters long). If a game already exists with that code, generate a new one. Once a unique code is found, break out of the loop.
            while True:
                roomCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                try:
                    Game.objects.get(roomCode=roomCode)
                except:
                    break

            newGame = Game(roomCode=roomCode, player1=request.user, isActive=True)
            newGame.save()

            return render(request, 'pychess/networkGame.html', {'newGame':True, 'roomCode':roomCode})
        
        elif request.GET['g'] == 'join':
            # Should render a form to prompt the user for a room code to join
            return render(request, 'pychess/networkGame.html', {'newGame':False})
        
    elif request.method == 'POST':
        # this is where the room code should be submitted in the event that the user is joining an existing game
        pass
    else:
        return redirect(index)


def review(request):
    return render(request, 'pychess/review.html')


def spectate(request):
    return render(request, 'pychess/spectate.html')


# API =====================

def getBoardState(request):
    pass

def checkMoves(request):
    pass

def submitMove(request):
    pass