from .models import *
import json


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
        piece['hasMoved'] = False

        pieceList.append(piece)


    boardState['pieces'] = pieceList

    return boardState


# creates list of every valid space a given piece can move to
def checkPieceMoves(gameState, pieceID):

    piece = gameState['pieces'][pieceID]
    validMoves = []

    # This creates a list of tuples with the coordinates of every occupied space, and only the occupied spaces. 
    # We care about what color piece occupies the space, but not about any other information about the piece.
    piecePositionList = []
    for boardPiece in gameState['pieces']:
        if not boardPiece['captured']:
            piecePositionList.append((boardPiece['rank'], boardPiece['file'], boardPiece['color']))

    # If the piece is a pawn or a king that has special moves; check whether those special moves are allowed here:
    if piece['type'] == 'pawn':
        
        # Regular pawn capturing
        checkLeft = piece['rank'] - 1
        checkRight = piece['rank'] + 1
        if piece['color'] == 'light':
            opposingColor = 'dark'
            checkVert = piece['file'] - 1
        elif piece['color'] == 'dark':
            opposingColor = 'light'
            checkVert = piece['file'] + 1

        if (checkRight,checkVert, opposingColor) in piecePositionList:
            validMoves.append((checkRight,checkVert))

        if (checkLeft,checkVert, opposingColor) in piecePositionList:
            validMoves.append((checkLeft,checkVert))

        # En Passant
        # Promotions
        

    if piece['type'] == 'king':
        # Castling
        if not piece['hasMoved']:
            if piece['color'] == 'light':
                pass
            elif piece['color'] == 'dark':
                pass


    # Grabs a list of directions the given piece is allowed to move
    for direction in getMovementPattern(piece):

        # Step in that direction one space at a time, up to the max number of spaces a piece is allowed to move on one turn
        for i in range(getMovementDistance(piece)):
            # Start by getting the absolute board coordinate of the space we're checking
            posX = piece['rank'] + direction[0] * (i + 1)
            posY = piece['file'] + direction[1] * (i + 1)
            
            # Make sure the space is within the bounds of the board. If it's not, break out of the loop and move on to the next direction
            if posX > 7 or posX < 0 or posY > 7 or posY < 0:
                break
            
            # Make sure the piece isn't moving into a space occupied by another piece
            positionIsOccupied = False
            for boardPiece in gameState['pieces']:
                if not boardPiece['captured']:
                    if posX == boardPiece['rank'] and posY == boardPiece['file'] and piece != boardPiece:
                    
                        # If it is, and the piece is the same color as the piece occupying the square to move to,
                        # don't add the move and break out of the loop to check a new direction (can't move through same colored pieces)
                        if boardPiece['color'] == piece['color'] or piece['type'] == 'pawn':
                            positionIsOccupied = True
                        
                        # Otherwise, add the move first and then break out of loop to check a new direction
                        else:
                            positionIsOccupied = True
                            # Simulate the move before allowing it to happen. If the player moves themselves into check, the move is not allowed
                            virtualGameState = simulateMove(gameState, piece['id'], (posX,posY))
                            if not isInCheck(virtualGameState, piece['color']):
                                validMoves.append((posX,posY))

            if positionIsOccupied:
                break

            virtualGameState = simulateMove(gameState, piece['id'], (posX,posY))
            if not isInCheck(virtualGameState, piece['color']):
                validMoves.append((posX,posY))

    return {'validMoves':validMoves}


# moves a piece and creates a copy of the board state; without committing the move to the DB or altering the main gameState.
# Used for verifying that a player cannot move themselves into check, per Chess rules
def simulateMove(gameState, pieceID, position):
    
    # Creates a deep copy of the gameState object; so as not to modify any of the values in the gameState while working
    virtualGameState = json.loads(json.dumps(gameState))
    vPiece = virtualGameState['pieces'][pieceID]

    vPiece['rank'] = position[0]
    vPiece['file'] = position[1]
    vPiece['hasMoved'] = True
    virtualGameState['turnNumber'] += 1

    for boardPiece in virtualGameState['pieces']:
            if boardPiece['rank'] == vPiece['rank'] and boardPiece['file'] == vPiece['file'] and boardPiece != vPiece:
                boardPiece['captured'] = True

    return virtualGameState


# Checks if a player is in check. Returns True if so, or False otherwise.
def isInCheck(gameState, color):

    print("Begin Check:")

    if color == 'light':
        king = gameState['pieces'][28]
    elif color == 'dark':
        king = gameState['pieces'][4]

    boardPieces = gameState['pieces']

    cardinalDirections = [(1,0),(-1,0),(0,1),(0,-1)]
    ordinalDirections = [(1,1),(1,-1),(-1,1),(-1,-1)]
    knightSpaces = [(1,2),(-1,2),(1,-2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]


    # Check north, south, east, and west until we hit a piece. If the piece is a rook or a queen, return True. 
    # If the piece is a King, and it's only one space away, return True.
    print("Checking cardinal directions:")
    for direction in cardinalDirections:
        pieceFound = False
        for distance in range(8):
            checkX = king['rank'] + (direction[0] * (distance + 1))
            checkY = king['file'] + (direction[1] * (distance + 1))
            print(f"Checking space ({checkX,checkY})")
            # If the check space is out of bounds, break and start searching in a new direction
            if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                break

            # Begin checking the positions of the pieces on the board against the new checkX and checkY
            for piece in boardPieces:
                
                # If a piece is found, check its type and distance.
                if piece['captured'] == False and piece['rank'] == checkX and piece['file'] == checkY:
                    pieceFound = True
                    print(f"Piece found: {piece['color']} {piece['type']} at ({piece['rank']}, {piece['file']})")
                    if piece['color'] != king['color'] and (piece['type'] == 'rook' or piece['type'] == 'queen'):
                        print("King in check")
                        return True
                    elif piece['type'] == 'king' and distance == 1 and piece['color'] != king['color']:
                        print("King in check")
                        return True
                
                # If a piece is found that doesn't place the king in check, break out of both inner loops and search in a new direction
                if pieceFound:
                    print("No check found; changing directions")
                    break

            if pieceFound:
                    break    


    # Check diagonally in all four directions until a piece is hit. If the piece is a bishop or queen, return True
    # If the piece is a Pawn or a King, and it's only one space away, return True.
    # Pawns are weird because they can only capture NE/NW or SE/SW depending on their color
    print("Checking ordinal directions:")
    for direction in ordinalDirections:
        pieceFound = False
        for distance in range(8):
            checkX = king['rank'] + (direction[0] * (distance + 1))
            checkY = king['file'] + (direction[1] * (distance + 1))
            print(f"Checking space ({checkX,checkY})")

            # If the check space is out of bounds, break and start searching in a new direction
            if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                break

            # Begin checking the positions of the pieces on the board against the new checkX and checkY
            for piece in boardPieces:
                
                # If a piece is found, check its type and distance.
                if piece['captured'] == False and piece['rank'] == checkX and piece['file'] == checkY:
                    pieceFound = True
                    print(f"Piece found: {piece['color']} {piece['type']} at ({piece['rank']}, {piece['file']})")
                    if piece['color'] != king['color'] and (piece['type'] == 'bishop' or piece['type'] == 'queen'):
                        print("King in check")
                        return True
                    elif piece['type'] == 'king' and distance == 1 and piece['color'] != king['color']:
                        print("King in check")
                        return True
                    # Pawns are weird again; if there's a pawn diagonally one space away from the king, need to check what color it is and if it's north or south of the king
                    elif piece['type'] == 'pawn' and distance == 1 and piece['color'] != king['color']:
                        if piece['color'] == 'light' and piece['file'] == king['file'] + 1:
                            print("King in check")
                            return True
                        elif piece['color'] == 'dark' and piece['file'] == king['file'] - 1:
                            print("King in check")
                            return True
                
                # If a piece is found that doesn't place the king in check, break out of both inner loops and search in a new direction
                if pieceFound:
                    print("No check found; changing directions")
                    break

            if pieceFound:
                    break


    # Check the surrounding spaces for a knight. If a knight is found, return True.
    print("Checking for Knights:")
    for direction in knightSpaces:
        checkX = king['rank'] + direction[0]
        checkY = king['file'] + direction[1]
        print(f"Checking space ({checkX,checkY})")

        # If the space to check is out of bounds, skip it and check a different space
        if checkX > 7 or checkX < 0 or checkY > 7 or checkY < 0:
            continue

        for piece in boardPieces:
            if piece['captured'] == False and piece['rank'] == checkX and piece['file'] == checkY:
                print(f"Piece found: {piece['color']} {piece['type']} at ({piece['rank']}, {piece['file']})")
                if piece['type'] == 'knight' and piece['color'] != king['color']:
                    print("King in check")
                    return True
                print("No check found; changing directions")
                break


    # If all of the checks above fail, return false
    print("No check found")
    return False


# Attempts to move a piece on the board. returns True if successful or False otherwise
def move(gameID, piece, position):

    # Current state of the board
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
        piece['hasMoved'] = True
        boardState['turnNumber'] += 1

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


# returns a list of tuples, each describing which directions a piece is allowed to move
def getMovementPattern(piece):
    if piece['type'] == 'pawn':
        if piece['color'] == 'light':
            return [(0,-1)]
        elif piece['color'] == 'dark':
            return [(0,1)]
            
    elif piece['type'] == 'rook':
        return [(0,1),(1,0),(0,-1),(-1,0)]
    elif piece['type'] == 'bishop':
        return [(1,1),(1,-1),(-1,1),(-1,-1)]
    elif piece['type'] == 'knight':
        return [(1,2),(2,1),(1,-2),(2,-1),(-1,-2),(-2,-1),(-1,2),(-2,1)]
    elif piece['type'] == 'queen' or piece['type'] == 'king':
        return [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]


# returns an integer, which represents the number of spaces a piece is allowed to move per turn
def getMovementDistance(piece):
    if piece['type'] == 'bishop' or piece['type'] == 'rook' or piece['type'] == 'queen':
        return 8
    elif piece['type'] == 'knight' or piece['type'] == 'king':
        return 1
    elif piece['type'] == 'pawn':
        if piece['hasMoved']:
            return 1
        else:
            return 2
