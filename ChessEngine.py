import Piece

"""
Defines the current game state (piece placement, current turn, and move log)
"""
class GameState():
    def __init__(self) -> None: 
        self.board = [[Piece.WHITE | Piece.QUEEN] * 8 for i in range(8)]
        self.whiteToMove = True
        self.moveLog = []