from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
import json
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import *
from . import chessEngine
import string, random

def index(request):
    if request.user.is_authenticated:
        localGames = Game.objects.filter(player1 = request.user, player2 = request.user)
        return render(request, 'pychess/index.html', {'localGames':localGames})
    else:
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

    if request.method == 'GET':
        room = request.GET.get('room')
        if room == None:
            # create a new game entry in the DB
            # local games will use the same player name for both player 1 and player 2
            newRoomCode = generateNewRoomCode()
            newGame = Game(roomCode = newRoomCode, player1=request.user, player2=request.user, isActive=True)
            newGame.save()
            response = redirect('localGame')
            response['Location'] += f'?room={newRoomCode}'
            return response
        else:
            game = Game.objects.get(roomCode = room)
            return render(request, 'pychess/localGame.html', {'gameID':game.id})


def networkGame(request):
    if request.method == "GET":
        room = request.GET.get('room')

        # If room == none, it's a new game. Generate a room code, create a game entry, and redirect to the newly created game
        if room == None:
            # generate a new room code and attempt to create a new game entry in the DB
            newRoomCode = generateNewRoomCode()
            newGame = Game(roomCode = newRoomCode, player1=request.user, isActive=True)
            newGame.save()
            response = redirect('networkGame')
            response['Location'] += f'?room={newRoomCode}'
            return response
        
        # If there's a room code in the GET data, this is an already existing game. 
        else:
            # get the game data from the DB
            game = Game.objects.get(roomCode = room)

            # If the user is listed as either player1 or player2 already; just render the game.
            if game.player1 == request.user or game.player2 == request.user:
                return render(request, 'pychess/networkGame.html', {'gameID':game.id, 'roomCode':room})
            
            # If the user is NOT listed as a player already, but there is no player 2 listed; make the user player2, update the game entry, and render the game.
            elif game.player2 == None:
                print("made it to this block")
                game.player2 = request.user
                game.save()
                return render(request, 'pychess/networkGame.html', {'gameID':game.id, 'roomCode':room})
            
            # TODO: If the user is not listed as a player, and the game is full already; redirect to the spectate page to join game as a spectator.
            else:
                redirect(play)



def review(request):
    return render(request, 'pychess/review.html')


def spectate(request):
    return render(request, 'pychess/spectate.html')





# API =====================

# Takes a gameID and returns a gameState object
def getGameState(request):
    if request.method =='GET':
        try:
            gameID = request.GET.get('gameID')
        except:
            return JsonResponse({'error':'game does not exist'})
        
        return JsonResponse(chessEngine.generateBoardState(gameID))
    else:
        return JsonResponse({'error':'invalid request method'}, status=405)


# Sends the list of moves to the frontend to display in the info panel
def getMoveList(request):
    if request.method == "POST":
        data = json.loads(request.body)
        gameState = data.get('state')
        moveList = []
        rawMoveList = Move.objects.filter(gameID=Game.objects.get(id=gameState['id']))

        for move in rawMoveList:
            newMove = {}
            newMove['turn'] = move.moveNumber + 1
            newMove['pieceID'] = move.pieceID
            newMove['position'] = move.rankFile
            moveList.append(newMove)

        responseObject = {}
        responseObject['moveList'] = moveList

        return JsonResponse(responseObject)
    else:
        return JsonResponse({"error":"invalid request method"}, status=405)

# takes some info about a piece on the board and returns a list of all of its valid moves
def checkMoves(request):
    
    if request.method == 'POST':

        # get some information about the piece to move from the POST request data
        data = json.loads(request.body)
        gameState = data.get('state')
        pieceID = data.get('pieceID')

        # call the chessEngine to generate a list of valid moves for the given piece
        moveList = chessEngine.checkPieceMoves(gameState, pieceID)

        # return the list of moves to the front end
        return JsonResponse(moveList)
    
    else:
        return JsonResponse({'error':'invalid request method'}, status=405)


# Takes a gameID, a piece, and a desired position to move to. Will verify the move is legal, and will update the database accordingly and generate a new board state.
def submitMove(request):

    if request.method == 'POST':
        
        # get the info about the requested move from the POST request data
        data = json.loads(request.body)
        piece = data.get('piece')
        position = (data.get('rank'), data.get('file'))
        gameID = data.get('game')

        if(chessEngine.move(gameID, piece, position)):
            return JsonResponse({'message':'success'})
        else:
            return JsonResponse({'message':'failure'})
        
        
    else:
        return JsonResponse({'error':'invalid request method'}, status=405)


# Executes once at the start of each turn; checks for any conditions that result in a draw or checkmate.
def checkForWinCondition(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        gameState = data.get('state')
        color = data.get('color')

        # Checks if there are too few pieces to perform a checkmate.
        if chessEngine.checkForInsufficientMaterial(gameState):
            activeGame = Game.objects.get(id=gameState['id'])
            activeGame.isActive = False
            activeGame.save()
            return JsonResponse({'message':'draw'})

        # Counts the legal moves the active player can make
        validMoveCount = chessEngine.countValidMoves(gameState,color)

        # If the player has no legal moves, the game ends in either a checkmate or a stalemate, depending on whether they're currently in check.
        if validMoveCount == 0:
            if chessEngine.isInCheck(gameState,color):
                activeGame = Game.objects.get(id=gameState['id'])
                activeGame.isActive = False
                activeGame.winner = activeGame.player2
                activeGame.save()
                return JsonResponse({'message':'checkmate'})
            else:
                activeGame = Game.objects.get(id=gameState['id'])
                activeGame.isActive = False
                activeGame.save()
                return JsonResponse({'message':'stalemate'})
        
        # If validMoveCount is -1, that indicates that the King is the only piece that can move. The opposing players moves should then be counted.
        # If the opposing player ALSO shows -1 moves, then the Kings are the only pieces that can move and the game ends in a draw.
        elif validMoveCount == -1:
            if color == 'light':
                opposingMoveCount = chessEngine.countValidMoves(gameState,'dark')
            elif color == 'dark':
                opposingMoveCount = chessEngine.countValidMoves(gameState, 'light')

            if opposingMoveCount == -1:
                activeGame = Game.objects.get(id=gameState['id'])
                activeGame.isActive = False
                activeGame.save()
                return JsonResponse({'message':'draw'})
            else:
                return JsonResponse({'message':'no win'})

        else:
            return JsonResponse({'message':'no win'})
    else:
        return JsonResponse({'error':'invalid request method'}, status=405)


# Generates a room code; string of 6 random numbers & capital letters. Used for players to join network games, and for some game identification purposes.
def generateNewRoomCode():
    
    # Start a loop, create a code, and check if a game already exists with that code
    while True:
        roomCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        try:
            Game.objects.get(roomCode=roomCode)

        # objects.get should throw an exception if it can't find a db entry; so if an exception is thrown, the new code is good, and the loop should break
        # if no exception is thrown, that means objects.get found an entry, so go back to step 1 and try again
        except:
            break

    return roomCode