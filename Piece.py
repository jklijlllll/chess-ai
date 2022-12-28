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