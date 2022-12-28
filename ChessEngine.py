import Classes.Piece as Piece

"""
Defines the current game state (piece placement, current turn, and move log)
"""

class GameState():
    START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self) -> None: 
        self.board = [[Piece.EMPTY]  for i in range(64)]
        self.whiteToMove = True
        self.moveLog = []
        self.selected = None
        self.setState(self.START_POSITION)
    
    def setState(self, record: str) -> None:
        
        pieceDict = dict(zip(Piece.pieceNames, Piece.pieces))
        fields = record.split(' ')
        
        # Piece placement
        placement = ''.join(fields[0].split('/'))
        square = 0
        for i in range(len(placement)):
            if placement[i] in pieceDict:
                self.board[square] = pieceDict[placement[i]]
                square += 1
            if placement[i].isnumeric():
                for k in range(int(placement[i])):
                    self.board[square] = Piece.EMPTY
                    square+= 1 
        
        # Side to move
        self.whiteToMove = fields[1] == "w"
        
        # Castling ability
        # En passant target square
        # Halfmove clock
        # Fullmove clock

