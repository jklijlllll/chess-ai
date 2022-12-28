import Piece

"""
Defines the current game state (piece placement, current turn, and move log)
"""

class GameState():
    START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self) -> None: 
        self.board = [[Piece.EMPTY] * 8 for i in range(8)]
        self.whiteToMove = True
        self.moveLog = []
        self.selected = None
        self.setState(self.START_POSITION)
    
    def setState(self, record: str) -> None:
        
        pieceDict = dict(zip(Piece.pieceNames, Piece.pieces))
        fields = record.split(' ')
        
        # Piece placement
        ranks = fields[0].split('/')
        for i in range(len(ranks)):
            rank = ranks[i]
            col = 0
            for j in range(len(rank)):
                if rank[j] in pieceDict:
                    self.board[i][col] = pieceDict[rank[j]]
                    col += 1
                if rank[j].isnumeric():
                    for k in range(int(rank[j])):
                        self.board[i][col] = Piece.EMPTY
                        col+= 1 
        
        # Side to move
        self.whiteToMove = fields[1] == "w"
        
        # Castling ability
        # En passant target square
        # Halfmove clock
        # Fullmove clock

