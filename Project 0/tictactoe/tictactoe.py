"""
Tic Tac Toe Player
"""

import math
import copy 

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if(terminal(board)):
        return None

    contTurns = 0

    for i in range(3):
        for j in range(3):
            if(board[i][j] == X or board[i][j] == O):
                contTurns += 1

    if(contTurns % 2 == 0):
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if(terminal(board)):
        return None

    actions = set()

    for i in range(3):
        for j in range(3):
            if(board[i][j] == EMPTY):
                actions.add(tuple([i, j]))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    aux = copy.deepcopy(board)
    
    if(aux[action[0]][action[1]] != EMPTY):
        raise Exception('ActionNotValid')

    turnPlayer = player(aux)
    
    aux[action[0]][action[1]] = turnPlayer

    return aux


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Row's
    for i in range(3):
        if(board[i][0] == board[i][1] == board[i][2] != EMPTY):
            return X if board[i][0] == X else O

    # Columns
    for j in range(3):
        if(board[0][j] == board[1][j] == board[2][j] != EMPTY):
            return X if board[0][j] == X else O

    # Diagonal`s
    if(board[0][0] == board[1][1] == board[2][2] != EMPTY):
        return X if board[0][0] == X else O

    if(board[0][2] == board[1][1] == board[2][0] != EMPTY):
        return X if board[0][2] == X else O

    # If is a tie or there is no winner
    return None
  


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    aux = winner(board)

    if(aux != None):
        return True

     # Check if is not a tie
    for i in range(3):
        for j in range(3):
            if(board[i][j] == EMPTY):
                return False

    # If is a tie
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    aux = winner(board)

    return 1 if aux == X else -1 if aux == O else 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if(terminal(board)):
        return None


    optimal = None
    
    if(player(board) == X):
        aux = -9999
        
        for action in actions(board):
            minValue = _min(result(board, action))
            if(aux <= minValue):
                aux = minValue
                optimal = action

    else:
        aux = 9999

        for action in actions(board):
            maxValue = _max(result(board, action))
            if(aux >= maxValue):
                aux = maxValue
                optimal = action

    return optimal



def _min(board):

    if(terminal(board)):
        return utility(board)

    aux = 99999

    for action in actions(board):
        aux = min(aux, _max(result(board, action)))

    return aux


def _max(board):

    if(terminal(board)):
        return utility(board)

    aux = -99999

    for action in actions(board):
        aux = max(aux, _min(result(board, action)))

    return aux
