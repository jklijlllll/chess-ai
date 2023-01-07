from enum import Enum

class Move:
    def __init__(self, startSquare: int, endSquare: int, startPiece: int, endPiece: int, flag: int):
        self.startSquare = startSquare
        self.endSquare = endSquare
        self.startPiece = startPiece
        self.endPiece = endPiece
        self.flag = flag
    
    class Flag(Enum):
        NONE = 0
        PAWN_TWO_FORWARD = 1
        EN_PASSANT = 2
        