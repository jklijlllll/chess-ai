from enum import IntEnum

class Move:
    def __init__(self, startSquare: int, endSquare: int, startPiece: int, endPiece: int, flag: int):
        self.startSquare = startSquare
        self.endSquare = endSquare
        self.startPiece = startPiece
        self.endPiece = endPiece
        self.flag = flag
    
    class Flag(IntEnum):
        NONE = 0
        PAWN_TWO_FORWARD = 1
        EN_PASSANT = 2
        PROMOTE_KNIGHT = 3
        PROMOTE_BISHOP = 4
        PROMOTE_ROOK = 5
        PROMOTE_QUEEN = 6
        CASTLE = 7
        