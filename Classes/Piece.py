EMPTY = 0
KING = 1
PAWN = 2
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN  = 6

WHITE = 8
BLACK = 16
pieces = [WHITE | PAWN,  WHITE | KNIGHT,   WHITE | BISHOP,   
    WHITE | ROOK,   WHITE | QUEEN, WHITE | KING, 
    BLACK | PAWN,  BLACK | KNIGHT,   BLACK | BISHOP,   
    BLACK | ROOK,   BLACK | QUEEN,  BLACK | KING]
pieceImageNames = ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
pieceNames = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]

typeMask = 0b00111

def is_same_color(p1, p2):
    return p1 >> 3 == p2 >> 3

def is_same_type(p1, p2):
    return (p1 & typeMask) == (p2 & typeMask)
