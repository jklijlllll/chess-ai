import Classes.Piece as Piece

"""
Defines the current game state (piece placement, current turn, and move log)
"""

class GameState():
    START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    directions = [-8 , 8 , -1, 1, -9, 9, -7, 7]

    def __init__(self) -> None: 
        self.board = [[Piece.EMPTY] for i in range(64)]
        self.whiteToMove = True
        self.moveLog = []
        self.selected = None
        self.set_state(self.START_POSITION)
        self.numSquaresToEdge = self.__init_numSquaresToEdge()
        self.possibleMoves = []
    
    def set_state(self, record: str) -> None:
        
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

    def __init_numSquaresToEdge(self):

        numsSquaresToEdge = [[0] * 8 for i in range(64)]
        for rank in range(8):
            for file in range(8):
                numNorth = rank
                numSouth = 7 - rank
                numWest = file
                numEast = 7 - file
                numsSquaresToEdge[rank * 8 + file] = [
                    numNorth,
                    numSouth,
                    numWest,
                    numEast,
                    min(numNorth, numWest),
                    min(numSouth, numEast),
                    min(numNorth, numEast),
                    min(numSouth, numWest)
                    ]

        return numsSquaresToEdge

    def generate_sliding_moves(self, startSquare: int, piece: int):

        startIndex = 4 if Piece.is_same_type(piece, Piece.BISHOP) else 0
        endIndex = 4 if Piece.is_same_type(piece, Piece.ROOK) else 8 
        
        for dir in range(startIndex, endIndex):
            for num in range(self.numSquaresToEdge[startSquare][dir]):
                endPosition = startSquare + (num + 1) * self.directions[dir]
                if self.board[endPosition] is Piece.EMPTY:
                    self.possibleMoves.append(endPosition)
                else:
                    if not Piece.is_same_color(piece, self.board[endPosition]):
                        self.possibleMoves.append(endPosition)
                    break
                

