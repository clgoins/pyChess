from .models import *


def createNewBoard():
    boardState = {}
    boardState['turnNumber'] = 0
    boardState['dp1'] = {'rank':0, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp2'] = {'rank':1, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp3'] = {'rank':2, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp4'] = {'rank':3, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp5'] = {'rank':4, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp6'] = {'rank':5, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp7'] = {'rank':6, 'file':1, 'captured':False, 'hasMoved':False}
    boardState['dp8'] = {'rank':7, 'file':1, 'captured':False, 'hasMoved':False}

    boardState['lp1'] = {'rank':0, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp2'] = {'rank':1, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp3'] = {'rank':2, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp4'] = {'rank':3, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp5'] = {'rank':4, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp6'] = {'rank':5, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp7'] = {'rank':6, 'file':6, 'captured':False, 'hasMoved':False}
    boardState['lp8'] = {'rank':7, 'file':6, 'captured':False, 'hasMoved':False}

    boardState['dr1'] = {'rank':0, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['dn1'] = {'rank':1, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['db1'] = {'rank':2, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['dq1'] = {'rank':3, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['dk1'] = {'rank':4, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['db2'] = {'rank':5, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['dn2'] = {'rank':6, 'file':0, 'captured':False, 'hasMoved':False}
    boardState['dr2'] = {'rank':7, 'file':0, 'captured':False, 'hasMoved':False}

    boardState['lr1'] = {'rank':0, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['ln1'] = {'rank':1, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['lb1'] = {'rank':2, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['lq1'] = {'rank':3, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['lk1'] = {'rank':4, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['lb2'] = {'rank':5, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['ln2'] = {'rank':6, 'file':7, 'captured':False, 'hasMoved':False}
    boardState['lr2'] = {'rank':7, 'file':7, 'captured':False, 'hasMoved':False}

    return boardState

def checkMoves(gameID, pieceID, pieceInfo):

    # generate current board state
    # create list of every valid space the given piece can move to

    # TODO: should generate accurate absolute board coordinates
    if pieceID[1] == 'p':
        return {'validMoves': [(0,1)]}
    else:
        return {'validMoves':[]}


# attempts to move a piece on the board. returns True if successful or False otherwise
def move(gameID, pieceID, position):
    boardState = generateBoardState(gameID)

    # position will be a string 'px_y' where x & y are the desired coordinates. This converts that string to a tuple of ints to work with.
    try:
        posX = int(position[1])
        posY = int(position[3])
    except ValueError:
        return False 
    coordinates = (posX,posY)

    # double check that the provided move is valid (should be in the list returned by checkMoves())
    validMoves = checkMoves(gameID, pieceID, boardState[pieceID])
    if coordinates in validMoves['validMoves']:

        # update the 'move' db with the pieces new position
        newMove = Move(gameID = Game.objects.get(id=gameID), moveNumber = boardState['turnNumber'], piece = pieceID, rankFile = coordToRankFile(coordinates))
        newMove.save()
        return True
    else:
        return False


# recreates the most recent state of the board, given a gameID
def generateBoardState(gameID):
    # generate a fresh board state
    # gather every move from the db with the associated gameID attached
    # create a new board state based on the previous moves that have been made
    
    boardState = createNewBoard()
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

