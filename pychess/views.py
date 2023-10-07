from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
import json
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import *
from . import chessEngine
import string, random

def index(request):
    if request.user.is_authenticated:
        # Local games are all the games where the user is both player1 and player2
        localGames = Game.objects.filter(player1 = request.user, player2 = request.user, isActive=True)
        
        activeNetworkGames = [] 

        # Grab a list of games where the user is ONLY player1 and add it to the master list
        netGameQuery = Game.objects.filter(player1 = request.user, isActive=True).exclude(player2 = request.user)
        for game in netGameQuery:
            activeNetworkGames.append(game)

        # Do the same for games where the user is ONLY player2
        netGameQuery = Game.objects.filter(player2 = request.user,isActive=True).exclude(player1 = request.user)
        for game in netGameQuery:
            activeNetworkGames.append(game)

        # Grab a list of completed games (isActive=False) that the user was involved in; and count how many wins, losses, and draws there were
        completedGames = {}
        completedGames['wins'] = 0
        completedGames['draws'] = 0
        completedGames['losses'] = 0

        netGameQuery = Game.objects.filter(player1 = request.user, isActive=False).exclude(player2=request.user)
        for game in netGameQuery:
            if game.winner == request.user:
                completedGames['wins'] += 1
            elif game.winner == None:
                completedGames['draws'] += 1
            else:
                completedGames['losses'] += 1

        netGameQuery = Game.objects.filter(player2 = request.user, isActive=False).exclude(player1=request.user)
        for game in netGameQuery:
            if game.winner == request.user:
                completedGames['wins'] += 1
            elif game.winner == None:
                completedGames['draws'] += 1
            else:
                completedGames['losses'] += 1

        
        return render(request, 'pychess/index.html', {'localGames':localGames, 'networkGames':activeNetworkGames, 'completedGames':completedGames})
    
    else:
        return redirect(loginView)


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
    return redirect(loginView)


def register(request):
    if request.method == "POST":
        # Grab the new users info from the POST request data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        passwordConfirm = request.POST['passwordConfirm']

        # Make sure the username field is not left blank
        if username == "":
            return render(request, 'pychess/register.html', {"message":"Username field cannot be left blank."})

        # Do the same for the password field
        if password == "":
            return render(request, 'pychess/register.html', {"message":"Password field cannot be left blank."})

        # If this were going to be a real website; this is probably where I should check that the password has a minimum number of characters; uppercase, numbers, special characters, etc.

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
   
    
@login_required
def play(request):
    
    if request.method == "GET":
        return render(request, 'pychess/play.html')
    
    # POST request will come from user submitting a room code on the play page
    elif request.method == "POST":
        # Get the request room code from POST data
        roomCode = request.POST['roomCode']

        # Check if a game exists with that code. If so, redirect to networkGame with that room code.
        if Game.objects.filter(roomCode=roomCode).exists():
            game = Game.objects.get(roomCode=roomCode)
            
            # If player1 == player2, the game is actually a local game. This Join form isn't really intended for rejoining local games, but there's no reason not to send the user to the right place.
            if game.player1 != game.player2:
                response = redirect('networkGame')
                response['Location'] += f'?room={roomCode}'
                return response
            
            else:
                response = redirect('localGame')
                response['Location'] += f'?room={roomCode}'
                return response

        # Otherwise, redirect back to the play page with an error message
        else:
            return render(request, 'pychess/play.html', {"message":"Game does not exist! Did you enter the room code correctly?"})
    else:
        return JsonResponse({"message":"invalid request method"}, status=405)


@login_required
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


@login_required
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
    else:
        return JsonResponse({"message":"invalid request method"}, status=405)


@login_required
def review(request):
    
    if request.method == "GET":
        # Generate a queryset of games that the user was a part of
        gameQuery = Game.objects.filter(player1 = request.user) | Game.objects.filter(player2 = request.user)

        # Extract some info from the queryset and add each game to a list to pass to the front end to display. Opponent name; room code; local/network game
        games = []
        for query in gameQuery:
            # Only look at the game if it's no longer active; otherwise discard it
            if not query.isActive:

                

                # For network games; determine which player the user is, and store the opposing users name in "opponent"
                # If player1 == player2; it's a local game
                if query.player1 != query.player2:
                    gameType = "Network"
                    opponent = query.player2 if request.user == query.player1 else query.player1
                
                # For local games, there's no opponent name to display
                else:
                    gameType = "Local"
                    opponent = "---"

                # Create a list entry that contains the info to be displayed           
                game = {}
                game['gameType'] = gameType
                game['opponent'] = opponent

                if query.winner == request.user:
                    game['outcome'] = "WIN"
                elif query.winner == None:
                    game['outcome'] = "DRAW"
                else:
                    game['outcome'] = "LOSE"

                game['roomCode'] = query.roomCode

                # Add the list entry to the master list
                games.append(game)

        return render(request, 'pychess/review.html', {"games":games})

    else:
        return JsonResponse({"error":"Invalid request method"}, status=405)


@login_required
def reviewGame(request, roomCode):

    # Get some initial info from the provided roomCode to pass to the front end
    game = Game.objects.get(roomCode=roomCode)

    return render(request,'pychess/reviewGame.html', {'gameID':game.id, 'roomCode':roomCode, 'player1':game.player1, 'player2':game.player2})


def spectate(request):
    # On initial vist; present user with a form to enter a room code
    if request.method == "GET":
        return render(request, 'pychess/spectate.html')
    
    # Grab the room code; generate a board state, and allow the user to watch the game. Generate an error if the room code is invalid.
    elif request.method == "POST":

        roomCode = request.POST['roomCode'].upper()

        if Game.objects.filter(roomCode=roomCode).exists():

            gameID = Game.objects.get(roomCode=roomCode).id
            print(gameID)
            return render(request, 'pychess/spectateGame.html', {"gameID":gameID})
        
        else:

            return render(request, 'pychess/spectate.html', {"message":"Invalid room code!"})
        
    else:
        return JsonResponse({"error":"invalid request method"}, status=405)





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
        gameID = data.get('gameID')
        moveList = []
        rawMoveList = Move.objects.filter(gameID=gameID)

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