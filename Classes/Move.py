from enum import IntEnum
import chess


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

    def pyChessPromotePiece(self) -> chess.Piece | None:
        match self.flag:
            case Move.Flag.PROMOTE_KNIGHT:
                return chess.KNIGHT
            case Move.Flag.PROMOTE_BISHOP:
                return chess.BISHOP
            case Move.Flag.PROMOTE_ROOK:
                return chess.ROOK
            case Move.Flag.PROMOTE_QUEEN:
                return chess.QUEEN
            case _:
                return None

    def uci(self) -> str:
        move = chess.Move(self.startSquare, self.endSquare,
                          self.pyChessPromotePiece(), None)
        return move.uci()
