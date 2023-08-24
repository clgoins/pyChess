from .models import *
import json


def createNewBoard(game):
    
    # Dictionary describing a bunch of info about the game
    boardState = {}
    boardState['id'] = game.id
    boardState['roomCode'] = game.roomCode
    boardState['player1'] = game.player1.username

    if game.player2 == None:
        boardState['player2'] = ""
    else:
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
        
        # *****Regular pawn capturing*******************************************
        checkLeft = piece['rank'] - 1
        checkRight = piece['rank'] + 1
        if piece['color'] == 'light':
            opposingColor = 'dark'
            checkVert = piece['file'] - 1
        elif piece['color'] == 'dark':
            opposingColor = 'light'
            checkVert = piece['file'] + 1

        if (checkRight,checkVert, opposingColor) in piecePositionList:
            virtualGameState = simulateMove(gameState, piece['id'], (checkRight,checkVert))
            if not isInCheck(virtualGameState, piece['color']):
                validMoves.append((checkRight,checkVert))

        if (checkLeft,checkVert, opposingColor) in piecePositionList:
            virtualGameState = simulateMove(gameState, piece['id'], (checkLeft,checkVert))
            if not isInCheck(virtualGameState, piece['color']):
                validMoves.append((checkLeft,checkVert))


        # *****En Passant*******************************************************
        ''' From Google: In chess, en passant (French: lit. "in passing") describes 
        the capture by a pawn of an enemy pawn on the same rank and an adjacent file that has 
        just made an initial two-square advance. The capturing pawn moves to the square that 
        the enemy pawn passed over, as if the enemy pawn had advanced only one square.'''
        
        # The attacking pawn must be on File 3 for light pieces, or File 4 for dark pieces
        if (piece['file'] == 3 and piece['color'] == 'light') or (piece['file'] == 4 and piece['color'] == 'dark'):
            # Checks the board state to see if an opposite colored pawn is adjacent left or right to the attacking pawn. The defending Pawn also must have moved at some point.
            for boardPiece in gameState['pieces']:
                if boardPiece['file'] == piece['file'] and (boardPiece['rank'] == checkLeft or boardPiece['rank'] == checkRight) and boardPiece['captured'] == False and boardPiece['type'] == 'pawn' and boardPiece['color'] != piece['color'] and boardPiece['hasMoved'] == True:
                    # Checks if the defending pawn moved two spaces on the previous turn.
                    currentGame = Game.objects.get(id=gameState['id'])
                    previousMove = Move.objects.filter(gameID=currentGame).get(moveNumber=gameState['turnNumber'] - 1)
                    defenderMoveCount = Move.objects.filter(gameID=currentGame).filter(pieceID=boardPiece['id']).count()
                    if previousMove.pieceID == boardPiece['id'] and defenderMoveCount == 1:
                        # All conditions are correct for en passant
                        if piece['color'] == 'light':
                            virtualGameState = simulateMove(gameState, piece['id'], (boardPiece['rank'], boardPiece['file'] - 1))
                            if not isInCheck(virtualGameState, piece['color']):
                                validMoves.append((boardPiece['rank'], boardPiece['file'] - 1))
                        elif piece['color'] == 'dark':
                            virtualGameState = simulateMove(gameState, piece['id'], (boardPiece['rank'], boardPiece['file'] + 1))
                            if not isInCheck(virtualGameState, piece['color']):
                                validMoves.append((boardPiece['rank'], boardPiece['file'] + 1))
                    

    # *****Light Castling******************************************************
    # Piece 28 is the light king. Cannot be in check to perform a castle.
    # TODO: This section is a ton of text, and a lot of it is basically the same with just some ID numbers swapped out depending on whether the piece is light or dark. See if there's a shorter way to write this.
    if piece['id'] == 28 and not isInCheck(gameState, piece['color']):

        # Left castle. Piece 24 is light Rook on left side. Neither piece can have moved at any point.
        if piece['hasMoved'] == False and gameState['pieces'][24]['hasMoved'] == False:
            canCastle = True
            
            # All three spaces between the rook and king must be empty.
            for boardPiece in gameState['pieces']:
                if (boardPiece['rank'] == 3 or boardPiece['rank'] == 2 or boardPiece['rank'] == 1) and boardPiece['file'] == 7:
                    canCastle = False
                    break
            
            # The King cannot move into check or through check
            virtualGameState = simulateMove(gameState, piece['id'], (3,7))
            if isInCheck(virtualGameState, piece['color']):
                canCastle = False
            else:
                virtualGameState = simulateMove(gameState, piece['id'], (2,7))
                if isInCheck(virtualGameState, piece['color']):
                    canCastle = False

            if canCastle:
                validMoves.append((2,7))

        # Right castle. Piece 31 is light Rook on right side. Neither piece can have moved at any point.
        if piece['hasMoved'] == False and gameState['pieces'][31]['hasMoved'] == False:
            canCastle = True
            
            # Both spaces between the rook and king must be empty.
            for boardPiece in gameState['pieces']:
                if (boardPiece['rank'] == 5 or boardPiece['rank'] == 6) and boardPiece['file'] == 7:
                    canCastle = False
                    break
            
            # The King cannot move into check or through check
            virtualGameState = simulateMove(gameState, piece['id'], (5,7))
            if isInCheck(virtualGameState, piece['color']):
                canCastle = False
            else:
                virtualGameState = simulateMove(gameState, piece['id'], (6,7))
                if isInCheck(virtualGameState, piece['color']):
                    canCastle = False

            if canCastle:
                validMoves.append((6,7))


    # *****Dark Castling*******************************************************
    # Piece 4 is the dark king. Cannot be in check to perform a castle.
    if piece['id'] == 4 and not isInCheck(gameState, piece['color']):

        # Left castle. Piece 0 is dark rook on the left
        if piece['hasMoved'] == False and gameState['pieces'][0]['hasMoved'] == False:
            canCastle = True
            
            for boardPiece in gameState['pieces']:
                if (boardPiece['rank'] == 3 or boardPiece['rank'] == 2 or boardPiece['rank'] == 1) and boardPiece['file'] == 0:
                    canCastle = False
                    break
            
            virtualGameState = simulateMove(gameState, piece['id'], (3,0))
            if isInCheck(virtualGameState, piece['color']):
                canCastle = False
            else:
                virtualGameState = simulateMove(gameState, piece['id'], (2,0))
                if isInCheck(virtualGameState, piece['color']):
                    canCastle = False

            if canCastle:
                validMoves.append((2,0))

        # Right castle. Piece 7 is right dark rook
        if piece['hasMoved'] == False and gameState['pieces'][7]['hasMoved'] == False:
            canCastle = True
            
            for boardPiece in gameState['pieces']:
                if (boardPiece['rank'] == 5 or boardPiece['rank'] == 6) and boardPiece['file'] == 0:
                    canCastle = False
                    break
            
            virtualGameState = simulateMove(gameState, piece['id'], (5,0))
            if isInCheck(virtualGameState, piece['color']):
                canCastle = False
            else:
                virtualGameState = simulateMove(gameState, piece['id'], (6,0))
                if isInCheck(virtualGameState, piece['color']):
                    canCastle = False

            if canCastle:
                validMoves.append((6,0))


    # *****Standard moves******************************************************
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


# Counts the number of legal moves a player has. If the count is 0; the player has no legal moves and the game is over.
def countValidMoves(gameState, color):
    pieces = gameState['pieces']
    moveCount = 0

    for piece in pieces:
        if piece['captured'] == False and piece['color'] == color and piece['type'] != 'king':
            moveList = checkPieceMoves(gameState, piece['id'])
            moveCount += len(moveList['validMoves'])

    # If the King can move, and it's the ONLY piece that can move, return -1 to signify that the opponents moves need to be counted.
    # If both players moves are counted and return -1; the game ends in a stalemate.
    if moveCount == 0:
        if color == 'light':
            moveList = checkPieceMoves(gameState, pieces[28])
        elif color == 'dark':
            moveList = checkPieceMoves(gameState, pieces[4])

        if len(moveList['validMoves'] > 0):
            return -1

    return moveCount


# Checks both players remaining pieces to check for a draw by insufficient material (i.e. not possible to perform a checkmate with the remaining pieces on the board)
# Insufficient material is defined as (per Chess.com): King vs King; King & Bishop vs King; King & Kight vs King; King & Bishop vs King & Bishop, where both bishops occupy the same colored square.
# Returns True in the case of a draw; or False otherwise
def checkForInsufficientMaterial(gameState):
    lightPieces = []
    darkPieces  = []
    
    for piece in gameState['pieces']:
        if piece['captured'] == False:
            if piece['color'] == 'light':
                lightPieces.append(piece)
            elif piece['color'] == 'dark':
                darkPieces.append(piece)

    # If each player has only 1 piece, that piece must be a King, and the game is a draw.
    if len(darkPieces) == 1 and len(lightPieces) == 1:
        return True
    
    # King vs King & Bishop or King vs King & Knight
    elif len(darkPieces) == 2 and len(lightPieces) == 1:
        for piece in darkPieces:
            if piece['type'] == 'bishop' or piece['type'] == 'knight':
                return True
            
    # King vs King & Bishop or King vs King & Knight            
    elif len(darkPieces) == 1 and len(lightPieces) == 2:
        for piece in lightPieces:
            if piece['type'] == 'bishop' or piece['type'] == 'knight':
                return True
            
    # King & Bishop vs King & Bishop
    elif len(darkPieces) == 2 and len(lightPieces) == 2:
        darkBishop = None
        lightBishop = None

        for piece in darkPieces:
            if piece['type'] == 'bishop':
                darkBishop = piece
                break

        if darkBishop:
            for piece in lightPieces:
                if piece['type'] == 'bishop':
                    lightBishop = piece
                    break

        # Add the rank and file together; if the number is even the piece occupies a light square, otherwise it's a dark square.
        # If both bishops occupy the same color spaces, there is insufficient material for a checkmate.
        if darkBishop and lightBishop:
            if (lightBishop['rank'] + lightBishop['file']) % 2 == (darkBishop['rank'] + darkBishop['file']) % 2:
                return True

    else:
        return False
        

# Checks if a player is in check. Returns True if so, or False otherwise.
def isInCheck(gameState, color):
# Starts from the position of the king of the given color.
# Picks one of the 8 directions around the king, and begins stepping in that direction until a piece or the edge of the board is reached.
# Depening on the movement rules and the color of the piece that is encountered, determines if the king is in danger and returns true if so.
# Then checks each of the 8 spaces surrounding the king where a knight may attack from, and checks if a knight of the opposite color exists, returning true if so.
# If all the above checks fail, the player is not in check, and the function will return false.


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
    for direction in cardinalDirections:
        pieceFound = False
        for distance in range(8):
            checkX = king['rank'] + (direction[0] * (distance + 1))
            checkY = king['file'] + (direction[1] * (distance + 1))
            # If the check space is out of bounds, break and start searching in a new direction
            if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                break

            # Begin checking the positions of the pieces on the board against the new checkX and checkY
            for piece in boardPieces:
                
                # If a piece is found, check its type and distance.
                if piece['captured'] == False and piece['rank'] == checkX and piece['file'] == checkY:
                    pieceFound = True
                    if piece['color'] != king['color'] and (piece['type'] == 'rook' or piece['type'] == 'queen'):
                        return True
                    
                    if piece['color'] != king['color'] and piece['type'] == 'king' and distance == 0:
                        return True
                
                # If a piece is found that doesn't place the king in check, break out of both inner loops and search in a new direction
                if pieceFound:
                    break

            if pieceFound:
                    break    


    # Check diagonally in all four directions until a piece is hit. If the piece is a bishop or queen, return True
    # If the piece is a Pawn or a King, and it's only one space away, return True.
    # Pawns are weird because they can only capture NE/NW or SE/SW depending on their color
    for direction in ordinalDirections:
        pieceFound = False
        for distance in range(8):
            checkX = king['rank'] + (direction[0] * (distance + 1))
            checkY = king['file'] + (direction[1] * (distance + 1))

            # If the check space is out of bounds, break and start searching in a new direction
            if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                break

            # Begin checking the positions of the pieces on the board against the new checkX and checkY
            for piece in boardPieces:
                
                # If a piece is found, check its type and distance.
                if piece['captured'] == False and piece['rank'] == checkX and piece['file'] == checkY:
                    pieceFound = True
                    if piece['color'] != king['color'] and (piece['type'] == 'bishop' or piece['type'] == 'queen'):
                        return True
                    
                    if piece['color'] != king['color'] and piece['type'] == 'king' and distance == 0:
                        return True
        
                    # Pawns are weird again; if there's a pawn diagonally one space away from the king, need to check what color it is and if it's north or south of the king
                    elif piece['type'] == 'pawn' and distance == 0 and piece['color'] != king['color']:
                        if piece['color'] == 'light' and piece['file'] == king['file'] + 1:
                            return True
                        elif piece['color'] == 'dark' and piece['file'] == king['file'] - 1:
                            return True
                
                # If a piece is found that doesn't place the king in check, break out of both inner loops and search in a new direction
                if pieceFound:
                    break

            if pieceFound:
                    break


    # Check the surrounding spaces for a knight. If a knight is found, return True.
    for direction in knightSpaces:
        checkX = king['rank'] + direction[0]
        checkY = king['file'] + direction[1]

        # If the space to check is out of bounds, skip it and check a different space
        if checkX > 7 or checkX < 0 or checkY > 7 or checkY < 0:
            continue

        for piece in boardPieces:
            if piece['captured'] == False and piece['rank'] == checkX and piece['file'] == checkY:
                if piece['type'] == 'knight' and piece['color'] != king['color']:
                    return True
                break


    # If all of the checks above fail, return false
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
def generateBoardState(gameID, moveCount=-1):
    # generate a fresh board state
    # gather every move from the db with the associated gameID attached
    # will limit the list to the first x moves, based on moveCount. If moveCount < 0, it will not limit the list.
    # update and return the board state based on the list of moves that have been made
    # Assumes that if a Move is listed in the DB, it has already been verified to be a valid move

    boardState = createNewBoard(Game.objects.get(id=gameID))

    if moveCount < 0:
        moveList = Move.objects.filter(gameID = Game.objects.get(id=gameID)).order_by('moveNumber')
    
    # If the moveList is empty, go ahead and return the brand new board
    if not moveList:
        return boardState    

    # For every move in the movelist, update the relevant pieces location and increment the turn number
    for move in moveList:
        coords = rankFileToCoord(move.rankFile)
        piece = boardState['pieces'][move.pieceID]
        previousRank = piece['rank']
        previousFile = piece['file']
        capturePerformed = False
        piece['rank'] = coords[0]
        piece['file'] = coords[1]

        # This block performs a castle (moves both King and Rook) if the moving piece is a King that has not yet moved, and is moving two spaces either left or right of the starting position
        # Piece ID's 0, 7, 24, and 31 are the four rooks on the board.
        if piece['type'] == 'king' and piece['hasMoved'] == False:
            if piece['rank'] == 2 and piece['file'] == 7:
                boardState['pieces'][24]['rank'] = 3
            elif piece['rank'] == 6 and piece['file'] == 7:
                boardState['pieces'][31]['rank'] = 5
            elif piece['rank'] == 2 and piece['file'] == 0:
                boardState['pieces'][0]['rank'] = 3
            elif piece['rank'] == 6 and piece['file'] == 0:
                boardState['pieces'][7]['rank'] = 5
 
        piece['hasMoved'] = True
        boardState['turnNumber'] += 1

        # This block promotes a pawn to a queen once it's made it all the way across the board
        if piece['type'] == 'pawn' and piece['color'] == 'dark' and piece['file'] == 7:
            piece['type'] = 'queen'
        
        if piece['type'] == 'pawn' and piece['color'] == 'light' and piece['file'] == 0:
            piece['type'] = 'queen'
        
        # Checks if a piece is moving to an occupied square, and captures that piece if so
        for boardPiece in boardState['pieces']:
            if boardPiece['captured'] == False and boardPiece['rank'] == piece['rank'] and boardPiece['file'] == piece['file'] and boardPiece != piece:
                boardPiece['captured'] = True
                capturePerformed = True
                break

        # This block checks if a pawn moves diagonally without moving into an occupied square. Assumes En Passant if so and captures the defending pawn.
        if piece['type'] == 'pawn' and capturePerformed == False and (piece['rank'] == previousRank - 1 or piece['rank'] == previousRank + 1):
            # Find the defending pawn in the position that's being attacked, and capture it.
            for boardPiece in boardState['pieces']:
                if boardPiece['rank'] == piece['rank'] and boardPiece['file'] == previousFile:
                    boardPiece['captured'] = True
                    break

    return boardState


# Creates a deep copy of the board state and moves the given piece to the given position on that copied state, without committing the move to the DB or altering the main gameState.
# Used for verifying that a player cannot move themselves into check, per Chess rules
# Very similar to generateBoardState, but doesn't touch the database
def simulateMove(gameState, pieceID, position):
    
    # Creates a deep copy of the gameState object; so as not to modify any of the values in the gameState while working
    virtualGameState = json.loads(json.dumps(gameState))
    vPiece = virtualGameState['pieces'][pieceID]

    previousRank = vPiece['rank']
    previousFile = vPiece['file']
    capturePerformed = False
    vPiece['rank'] = position[0]
    vPiece['file'] = position[1]

    # Castling
    if vPiece['type'] == 'king' and vPiece['hasMoved'] == False:
        if vPiece['rank'] == 2 and vPiece['file'] == 7:
            virtualGameState['pieces'][24]['rank'] = 3
        elif vPiece['rank'] == 6 and vPiece['file'] == 7:
            virtualGameState['pieces'][31]['rank'] = 5
        elif vPiece['rank'] == 2 and vPiece['file'] == 0:
            virtualGameState['pieces'][0]['rank'] = 3
        elif vPiece['rank'] == 6 and vPiece['file'] == 0:
            virtualGameState['pieces'][7]['rank'] = 5

    vPiece['hasMoved'] = True
    virtualGameState['turnNumber'] += 1

    # Promotion
    if vPiece['type'] == 'pawn' and vPiece['color'] == 'dark' and vPiece['file'] == 7:
        vPiece['type'] = 'queen'
        
    if vPiece['type'] == 'pawn' and vPiece['color'] == 'light' and vPiece['file'] == 0:
        vPiece['type'] = 'queen'

    # Capturing
    for boardPiece in virtualGameState['pieces']:
            if boardPiece['rank'] == vPiece['rank'] and boardPiece['file'] == vPiece['file'] and boardPiece != vPiece:
                boardPiece['captured'] = True
                capturePerformed = True
                break

    # En Passant
    if vPiece['type'] == 'pawn' and capturePerformed == False and (vPiece['rank'] == previousRank - 1 or vPiece['rank'] == previousRank + 1):
        # Find the defending pawn in the position that's being attacked, and capture it.
        for boardPiece in virtualGameState['pieces']:
            if boardPiece['rank'] == vPiece['rank'] and boardPiece['file'] == previousFile:
                boardPiece['captured'] = True
                break

    return virtualGameState


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
