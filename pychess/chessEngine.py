from .models import *
import random


def createNewBoard(game):
    
    # Dictionary describing a bunch of info about the game
    boardState = {}
    boardState['id'] = game.id
    boardState['roomCode'] = game.roomCode
    boardState['player1'] = game.player1.username
    boardState['player2'] = game.player2.username
    boardState['turnNumber'] = 0
    
    # Final entry will be a list of 32 smaller dictionaries describing each piece on the board
    pieceList = []

    for i in range(32):
        piece = {}

        piece['id'] = i

        # Tried to order these as they appear on the board from left to right, top to bottom
        # First 16 are dark pieces, next 16 are light
        if i < 16:
            piece['color'] = 'dark'
        else:
            piece['color'] = 'light'

        # This looks dumb but I'm just trying to set the piece type, again from left to right, top to bottom.
        # First and last 8 are rook, knight, bishop, queen, king, bishop, knight, and rook; middle 16 are all pawns
        if i < 8 or i >= 24:
            if i == 0 or i == 7 or i == 24 or i == 31:
                piece['type'] = 'rook'
            elif i == 1 or i == 6 or i == 25 or i == 30:
                piece['type'] = 'knight'
            elif i == 2 or i == 5 or i == 26 or i == 29:
                piece['type'] = 'bishop'
            elif i == 3 or i == 27:
                piece['type'] = 'queen'
            else:
                piece['type'] = 'king'
        else:
            piece['type'] = 'pawn'

        # Setting each pieces initial position. rank is horizontal pos & file is vertical pos, per chess terminology
        # 0,0 is the top left corner; 8,8 is the bottom right.
        # Generally in chess the rank is notated with a letter 'A' thru 'H' and the file is a number 1 thru 8;
        # with 'A1' being the bottom left corner and 'H8' being the top right. A regular coordinate system is a little easier to work with in code,
        # so I've written a few conversion functions to convert between my coordinate system for doing logic behind the scenes, and the conventional rank-file system to display to the end user.
        if i < 8:
            piece['rank'] = i
            piece['file'] = 0
        elif i >=8 and i < 16:
            piece['rank'] = i - 8
            piece['file'] = 1
        elif i >= 16 and i < 24:
            piece['rank'] = i - 16
            piece['file'] = 6
        else:
            piece['rank'] = i - 24
            piece['file'] = 7

        piece['captured'] = False

        pieceList.append(piece)


    boardState['pieces'] = pieceList

    return boardState


# creates list of every valid space a given piece can move to
def checkPieceMoves(gameState, pieceID):

    piece = gameState['pieces'][pieceID]

    # TODO: should generate accurate absolute board coordinates
    if piece['type'] == 'pawn':
        return {'validMoves': [(4,4)]}
    else:
        return {'validMoves':[]}


# attempts to move a piece on the board. returns True if successful or False otherwise
def move(gameID, piece, position):

    boardState = generateBoardState(gameID)

    # double check that the provided move is valid (should be in the list returned by checkMoves())
    validMoves = checkPieceMoves(boardState, piece['id'])

    if position in validMoves['validMoves']:

        # update the 'move' db with the pieces new position
        newMove = Move(gameID = Game.objects.get(id=gameID), moveNumber = boardState['turnNumber'], pieceID = piece['id'], rankFile = coordToRankFile(position))
        newMove.save()

        return True
    else:
        return False


# recreates the most recent state of the board, given a gameID
def generateBoardState(gameID):
    # generate a fresh board state
    # gather every move from the db with the associated gameID attached
    # create a new board state based on the previous moves that have been made
    
    boardState = createNewBoard(Game.objects.get(id=gameID))

    moveList = Move.objects.filter(gameID = Game.objects.get(id=gameID)).order_by('moveNumber')
    
    # If the moveList is empty, go ahead and return the brand new board
    if not moveList:
        return boardState    


    for move in moveList:
        coords = rankFileToCoord(move.rankFile)
        piece = boardState['pieces'][move.pieceID]
        piece['rank'] = coords[0]
        piece['file'] = coords[1]

        for boardPiece in boardState['pieces']:
            if boardPiece['rank'] == piece['rank'] and boardPiece['file'] == piece['file'] and boardPiece != piece:
                boardPiece['captured'] = True


    return boardState


# accepts a tuple (x,y), returns a string 'RF'
def coordToRankFile(coordinates):
    rankFile = ''
    
    match coordinates[0]:
        case 0:
            rankFile += 'A'
        case 1:
            rankFile += 'B'
        case 2:
            rankFile += 'C'
        case 3:
            rankFile += 'D'
        case 4:
            rankFile += 'E'
        case 5:
            rankFile += 'F'
        case 6:
            rankFile += 'G'
        case 7:
            rankFile += 'H'

    match coordinates[1]:
        case 0:
            rankFile += '8'
        case 1:
            rankFile += '7'
        case 2:
            rankFile += '6'
        case 3:
            rankFile += '5'
        case 4:
            rankFile += '4'
        case 5:
            rankFile += '3'
        case 6:
            rankFile += '2'
        case 7:
            rankFile += '1'

    return rankFile


# accepts a string 'RF', returns a tuple (x,y)
def rankFileToCoord(rankFile):
    xPos = 0
    yPos = 0

    match rankFile[0]:
        case 'A':
            xPos = 0
        case 'B':
            xPos = 1
        case 'C':
            xPos = 2
        case 'D':
            xPos = 3
        case 'E':
            xPos = 4
        case 'F':
            xPos = 5
        case 'G':
            xPos = 6
        case 'H':
            xPos = 7

    match rankFile[1]:
        case '1':
            yPos = 7
        case '2':
            yPos = 6
        case '3':
            yPos = 5
        case '4':
            yPos = 4
        case '5':
            yPos = 3
        case '6':
            yPos = 2
        case '7':
            yPos = 1
        case '8':
            yPos = 0

    return (xPos, yPos)

