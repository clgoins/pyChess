
def createNewBoard():
    boardState = {}
    boardState['playerToMove'] = 'light'
    boardState['turnNumber'] = 0
    boardState['dp1'] = {'rank':0, 'file':1, 'captured':False}
    boardState['dp2'] = {'rank':1, 'file':1, 'captured':False}
    boardState['dp3'] = {'rank':2, 'file':1, 'captured':False}
    boardState['dp4'] = {'rank':3, 'file':1, 'captured':False}
    boardState['dp5'] = {'rank':4, 'file':1, 'captured':False}
    boardState['dp6'] = {'rank':5, 'file':1, 'captured':False}
    boardState['dp7'] = {'rank':6, 'file':1, 'captured':False}
    boardState['dp8'] = {'rank':7, 'file':1, 'captured':False}

    boardState['lp1'] = {'rank':0, 'file':6, 'captured':False}
    boardState['lp2'] = {'rank':1, 'file':6, 'captured':False}
    boardState['lp3'] = {'rank':2, 'file':6, 'captured':False}
    boardState['lp4'] = {'rank':3, 'file':6, 'captured':False}
    boardState['lp5'] = {'rank':4, 'file':6, 'captured':False}
    boardState['lp6'] = {'rank':5, 'file':6, 'captured':False}
    boardState['lp7'] = {'rank':6, 'file':6, 'captured':False}
    boardState['lp8'] = {'rank':7, 'file':6, 'captured':False}

    boardState['dr1'] = {'rank':0, 'file':0, 'captured':False}
    boardState['dn1'] = {'rank':1, 'file':0, 'captured':False}
    boardState['db1'] = {'rank':2, 'file':0, 'captured':False}
    boardState['dq1'] = {'rank':3, 'file':0, 'captured':False}
    boardState['dk1'] = {'rank':4, 'file':0, 'captured':False}
    boardState['db2'] = {'rank':5, 'file':0, 'captured':False}
    boardState['dn2'] = {'rank':6, 'file':0, 'captured':False}
    boardState['dr2'] = {'rank':7, 'file':0, 'captured':False}

    boardState['lr1'] = {'rank':0, 'file':7, 'captured':False}
    boardState['ln1'] = {'rank':1, 'file':7, 'captured':False}
    boardState['lb1'] = {'rank':2, 'file':7, 'captured':False}
    boardState['lq1'] = {'rank':3, 'file':7, 'captured':False}
    boardState['lk1'] = {'rank':4, 'file':7, 'captured':False}
    boardState['lb2'] = {'rank':5, 'file':7, 'captured':False}
    boardState['ln2'] = {'rank':6, 'file':7, 'captured':False}
    boardState['lr2'] = {'rank':7, 'file':7, 'captured':False}

    return boardState