import Classes.Piece as Piece
from Classes.Move import Move

"""
Defines the current game state (piece placement, current turn, and move log)
"""

class GameState():
    START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    directions = [8, -8, -1, 1, 7, -7, 9, -9 ]
    pawnDirections = [[8, 7, 9],[-8, -7, -9]]
    knightDirections = [15, 17, -17, -15, 10, -6, 6, -10]

    def __init__(self) -> None: 
        self.board = [[Piece.EMPTY] for i in range(64)]
        self.whiteToMove = True
        self.moveLog = []
        self.selected = None
        self.set_state(self.START_POSITION)

        numsSquaresToEdge = [[0] * 8 for i in range(64)]
        knightMoves = [[0] * 8 for i in range(64)]
        kingMoves = [[0] * 8 for i in range(64)]
        for i in range(len(self.board)):
            rank = int(i / 8)
            file = i % 8

            numNorth = 7 - rank
            numSouth = rank
            numWest = file
            numEast = 7 - file
            numsSquaresToEdge[i] = [
                numNorth,
                numSouth,
                numWest,
                numEast,
                min(numNorth, numWest),
                min(numSouth, numEast),
                min(numNorth, numEast),
                min(numSouth, numWest)
                ]

            knightSquares = []
            for j in range(len(self.knightDirections)):
                endSquare = i + self.knightDirections[j]
                if self.within_board(endSquare):
                    y = int (endSquare / 8)
                    x = endSquare % 8

                    # Prevent moves from wrapping around board
                    maxDistance = max(abs(rank - y), abs(file - x))
                
                    if maxDistance == 2:
                        knightSquares.append(self.knightDirections[j])
            knightMoves[i] = knightSquares

            kingSquares = []
            for k in range(len(self.directions)):
                endSquare = i + self.directions[k]
                if self.within_board(endSquare):
                    y = int (endSquare / 8)
                    x = endSquare % 8

                    # Prevent moves from wrapping around board
                    maxDistance = max(abs(rank - y), abs(file - x))
                
                    if maxDistance == 1:
                        kingSquares.append(self.directions[k])
            kingMoves[i] = kingSquares

        self.numSquaresToEdge = numsSquaresToEdge
        self.knightMoves = knightMoves
        self.kingMoves = kingMoves

        self.enPassantSquare = None
        self.possibleMoves = []
    
    def set_state(self, record: str) -> None:
        
        pieceDict = dict(zip(Piece.pieceNames, Piece.pieces))
        fields = record.split(' ')
        
        # Piece placement
        placement = fields[0].split('/')
        square = 63

        for i in range(len(placement)):
            for piece in reversed(placement[i]):
                if piece in pieceDict:
                    self.board[square] = pieceDict[piece]
                    square -= 1
                if piece.isnumeric():
                    for k in range(int(piece)):
                        self.board[square] = Piece.EMPTY
                        square-= 1 
       
        # Side to move
        self.whiteToMove = fields[1] == "w"
        
        # Castling ability
        # En passant target square
        # Halfmove clock
        # Fullmove clock

    def get_rank(self, square: int):
        return int(square / 8) 

    def within_board(self, square: int):
        return 0 <= square < 64

    def generate_move(self, startSquare: int, piece: int):

        if Piece.is_same_type(piece, Piece.BISHOP) or Piece.is_same_type(piece, Piece.ROOK) or Piece.is_same_type(piece, Piece.QUEEN):
            self.generate_sliding_moves(startSquare, piece)
        
        elif Piece.is_same_type(piece, Piece.PAWN):
            self.generate_pawn_moves(startSquare, piece)

        elif Piece.is_same_type(piece, Piece.KING):
            self.generate_king_moves(startSquare, piece)
        
        elif Piece.is_same_type(piece, Piece.KNIGHT):
            self.generate_knight_moves(startSquare, piece)


    # TODO: add castling
    def generate_sliding_moves(self, startSquare: int, piece: int):

        startIndex = 4 if Piece.is_same_type(piece, Piece.BISHOP) else 0
        endIndex = 4 if Piece.is_same_type(piece, Piece.ROOK) else 8 
        
        for dir in range(startIndex, endIndex):
            for num in range(self.numSquaresToEdge[startSquare][dir]):
                endSquare = startSquare + (num + 1) * self.directions[dir]
                if self.board[endSquare] is Piece.EMPTY:
                    self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
                elif not Piece.is_same_color(piece, self.board[endSquare]):
                    self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
                    break

    def generate_pawn_moves(self, startSquare: int, piece: int):
        # TODO: add en passant moves
        # TODO: add promotion
        dir = self.pawnDirections[0] if Piece.is_white(piece) else self.pawnDirections[1]
        pawnStartRank = 1 if Piece.is_white(piece) else 6
       
        endSquare = startSquare + dir[0]
        if self.within_board(endSquare) and self.board[endSquare] is Piece.EMPTY:
            self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
            if self.get_rank(startSquare) == pawnStartRank and self.within_board(endSquare + dir[0])  and self.board[endSquare] is Piece.EMPTY:
                self.possibleMoves.append(Move(startSquare, endSquare + dir[0], piece, self.board[endSquare + dir[0]], Move.Flag.PAWN_TWO_FORWARD))

        for i in range(1, len(dir)):
            endSquare = startSquare + dir[i]
            if self.within_board(endSquare) and self.board[endSquare] is not Piece.EMPTY and not Piece.is_same_color(piece, self.board[endSquare]):
                self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))

        if self.moveLog:
            lastMove = self.moveLog[-1]
            if lastMove.flag is Move.Flag.PAWN_TWO_FORWARD and not Piece.is_same_color(piece, lastMove.startPiece):
                direction = -8 if Piece.is_white(lastMove.startPiece) else 8
               
                if lastMove.endSquare is startSquare + 1 or lastMove.endSquare is startSquare - 1:
                    self.possibleMoves.append(Move(startSquare, lastMove.endSquare + direction, piece, self.board[lastMove.endSquare + direction], Move.Flag.EN_PASSANT))
                    self.enPassantSquare = lastMove.endSquare

    def generate_knight_moves(self, startSquare: int, piece: int):

        for i in range(len(self.knightMoves[startSquare])):
            endSquare = startSquare + self.knightMoves[startSquare][i]
            target = self.board[endSquare]
            if target is Piece.EMPTY:
                self.possibleMoves.append(Move(startSquare, endSquare, piece, target, Move.Flag.NONE))
            elif not Piece.is_same_color(piece, target):
                self.possibleMoves.append(Move(startSquare, endSquare, piece, target, Move.Flag.NONE))

    def generate_king_moves(self, startSquare: int, piece: int):

        for i in range(len(self.kingMoves[startSquare])):
            endSquare = startSquare + self.kingMoves[startSquare][i]
            target = self.board[endSquare]
            if target is Piece.EMPTY:
                self.possibleMoves.append(Move(startSquare, endSquare, piece, target, Move.Flag.NONE))
            elif not Piece.is_same_color(piece, target):
                self.possibleMoves.append(Move(startSquare, endSquare, piece, target, Move.Flag.NONE))

        