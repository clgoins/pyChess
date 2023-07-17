
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

def checkMoves(pieceID, pieceInfo):

    # generate current board state
    # create list of every valid space the given piece can move to

    # TODO: should generate absolute coordinates instead of relative coordinates
    if pieceID[1] == 'p':
        return {'validMoves': [[0,1],[0,-1]]}
    else:
        return {'validMoves':[]}

def move():
    # generate current board state
    # double check that the provided move is valid (should be in the list returned by checkMoves())
    # update the 'move' db with the pieces new position, and with any captures made
    pass

def generateBoardState():
    # generate a fresh board state
    # gather every move from the db with the associated gameID attached
    # create a new board state based on the previous moves that have been made
    pass