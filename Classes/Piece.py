EMPTY = 0
KING = 1
PAWN = 2
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN = 6

WHITE = 8
BLACK = 16

WHITE_PAWN = WHITE | PAWN
WHITE_KNIGHT = WHITE | KNIGHT
WHITE_BISHOP = WHITE | BISHOP
WHITE_ROOK = WHITE | ROOK
WHITE_QUEEN = WHITE | QUEEN
WHITE_KING = WHITE | KING
BLACK_PAWN = BLACK | PAWN
BLACK_KNIGHT = BLACK | KNIGHT
BLACK_BISHOP = BLACK | BISHOP
BLACK_ROOK = BLACK | ROOK
BLACK_QUEEN = BLACK | QUEEN
BLACK_KING = BLACK | KING

pieces = [WHITE_PAWN,  WHITE_KNIGHT,   WHITE_BISHOP,
          WHITE_ROOK,   WHITE_QUEEN, WHITE_KING,
          BLACK_PAWN,  BLACK_KNIGHT,   BLACK_BISHOP,
          BLACK_ROOK,   BLACK_QUEEN,  BLACK_KING]
pieceImageNames = ["wP", "wN", "wB", "wR", "wQ",
                   "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
pieceNames = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]

typeMask = 0b00111
colorMask = 0b11000


def is_same_color(p1, p2):
    return p1 >> 3 == p2 >> 3


def is_same_type(p1, p2):
    return (p1 & typeMask) == (p2 & typeMask)


def is_white(p):
    return p & colorMask == WHITE


def get_opposite_color(c):
    return WHITE if c == BLACK else BLACK
