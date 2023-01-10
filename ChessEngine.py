import Classes.Piece as Piece
from Classes.Move import Move
from bitmap import BitMap

"""
Defines the current game state (piece placement, current turn, and move log)
"""
# TODO: add attack bitboard to determine check/checkmate

class GameState():
    START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    directions = [8, -8, -1, 1, 7, -7, 9, -9 ]
    knightDirections = [15, 17, -17, -15, 10, -6, 6, -10]

    def __init__(self) -> None: 
        self.board = [[Piece.EMPTY] for i in range(64)]
        self.whiteToMove = True
        self.moveLog = []
        self.selected = None
        
        initPieceLists = [None if Piece.is_same_type(p, Piece.KING) else [] for p in Piece.pieces]
        self.pieceLists = dict(zip(Piece.pieces, initPieceLists))

        numsSquaresToEdge = [[0] * 8 for i in range(64)]
        knightMoves = [[0] * 8 for i in range(64)]
        kingMoves = [[0] * 8 for i in range(64)]
        pawnWhiteAttacks = [[0] * 8 for i in range(64)]
        pawnBlackAttacks = [[0] * 8 for i in range(64)]

        knightAttackMaps = [0 for i in range(64)]
        kingAttackMaps = [0 for i in range(64)]
        pawnWhiteAttackMaps = [0 for i in range(64)] 
        pawnBlackAttackMaps = [0 for i in range(64)]

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
            knightAttacks = 0
            for j in range(len(self.knightDirections)):
                endSquare = i + self.knightDirections[j]
                if self.within_board(endSquare):
                    y = int (endSquare / 8)
                    x = endSquare % 8

                    # Prevent moves from wrapping around board
                    maxDistance = max(abs(rank - y), abs(file - x))
                
                    if maxDistance == 2:
                        knightSquares.append(self.knightDirections[j])
                        knightAttacks |= 1 << endSquare

            knightMoves[i] = knightSquares
            knightAttackMaps[i] = knightAttacks

            kingSquares = []
            kingAttacks = 0
            for k in range(len(self.directions)):
                endSquare = i + self.directions[k]
                if self.within_board(endSquare):
                    y = int (endSquare / 8)
                    x = endSquare % 8

                    # Prevent moves from wrapping around board
                    maxDistance = max(abs(rank - y), abs(file - x))
                
                    if maxDistance == 1:
                        kingSquares.append(self.directions[k])
                        kingAttacks |= 1 << endSquare

            kingMoves[i] = kingSquares
            kingAttackMaps[i] = kingAttacks

            whitePawnAttacks = 0
            whitePawnSquares = []
            blackPawnAttacks = 0
            blackPawnSquares = []

            if rank > 0:
                if file > 0:
                    blackPawnAttacks |= 1 << i - 9
                    blackPawnSquares.append(i - 9)
                if file < 7:
                    blackPawnAttacks |= 1 << i - 7
                    blackPawnSquares.append(i - 7)
            if rank < 7:
                if file > 0:
                    whitePawnAttacks |= 1 << i + 7
                    whitePawnSquares.append(i + 7)
                if file < 7:
                    whitePawnAttacks |= 1 << i + 9
                    whitePawnSquares.append(i + 9)
            
            pawnWhiteAttacks[i] = whitePawnSquares
            pawnWhiteAttackMaps[i] = whitePawnAttacks
            pawnBlackAttacks[i] = blackPawnSquares
            pawnBlackAttackMaps[i] = blackPawnAttacks

        self.numSquaresToEdge = numsSquaresToEdge
        self.knightMoves = knightMoves
        self.kingMoves = kingMoves
        self.knightAttackMaps = knightAttackMaps
        self.kingAttackMaps = kingAttackMaps
        self.pawnWhiteAttacks = pawnWhiteAttacks
        self.pawnBlackAttacks = pawnBlackAttacks
        self.pawnWhiteAttackMaps = pawnWhiteAttackMaps
        self.pawnBlackAttackMaps = pawnBlackAttackMaps

        self.enPassantSquare = None
        self.possibleMoves = []

        # TODO: add fen position input with default start position
        self.set_state(self.START_POSITION)
        self.opponentAttackMap = 0
        self.generate_attack_map()
    
    def set_state(self, record: str) -> None:
        
        pieceDict = dict(zip(Piece.pieceNames, Piece.pieces))
        fields = record.split(' ')
        
        # Piece placement
        placement = fields[0].split('/')
        square = 63

        for i in range(len(placement)):
            for piece in reversed(placement[i]):
                if piece in pieceDict:
                    pieceType = pieceDict[piece]
                    self.board[square] = pieceType

                    if pieceType is Piece.WHITE_KING or pieceType is Piece.BLACK_KING:
                        self.pieceLists[pieceType] = square
                    else:
                        self.pieceLists[pieceType].append(square)
                        
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

    def generate_attack_map(self):
        
        self.opponentAttackMap = 0
        opponentColor = Piece.BLACK if self.whiteToMove else Piece.WHITE
        
        for rook in self.pieceLists[opponentColor | Piece.ROOK]:
            self.generate_sliding_attacks(rook, 0, 4)

        for bishop in self.pieceLists[opponentColor | Piece.BISHOP]:
            self.generate_sliding_attacks(bishop, 4, 8)
        
        for queen in self.pieceLists[opponentColor | Piece.QUEEN]:
            self.generate_sliding_attacks(queen, 0, 8)

        for knight in self.pieceLists[opponentColor | Piece.KNIGHT]:
            self.opponentAttackMap |= self.knightAttackMaps[knight]

        pawnAttackMap = self.pawnBlackAttackMaps if self.whiteToMove else self.pawnWhiteAttackMaps
        for pawn in self.pieceLists[opponentColor | Piece.PAWN]:
            self.opponentAttackMap |= pawnAttackMap[pawn]

        self.opponentAttackMap |= self.kingAttackMaps[self.pieceLists[opponentColor | Piece.KING]]

    def generate_sliding_attacks(self, startSquare: int, startIndex: int, endIndex: int):
        
        for dir in range(startIndex, endIndex):
             for num in range(self.numSquaresToEdge[startSquare][dir]):
                endSquare = startSquare + (num + 1) * self.directions[dir]
                self.opponentAttackMap |= 1 << endSquare
                if self.board[endSquare] is not Piece.EMPTY:
                    break

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
                else:
                    if not Piece.is_same_color(piece, self.board[endSquare]):
                        self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
                    break
                

    def generate_pawn_moves(self, startSquare: int, piece: int):
        # TODO: add promotion

        if Piece.is_white(piece):
            dir = self.directions[0] 
            pawnStartRank = 1 
            pawnAttacks = self.pawnWhiteAttacks
        else:
            dir = self.directions[1]
            pawnStartRank = 6
            pawnAttacks = self.pawnBlackAttacks

        # check if pawn is pushable
        endSquare = startSquare + dir
        if self.within_board(endSquare) and self.board[endSquare] is Piece.EMPTY:
            self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
            if self.get_rank(startSquare) == pawnStartRank and self.board[endSquare] is Piece.EMPTY:
                self.possibleMoves.append(Move(startSquare, endSquare + dir, piece, self.board[endSquare + dir], Move.Flag.PAWN_TWO_FORWARD))

        # check for pawn captures
        for i in range(len(pawnAttacks[startSquare])):
            endSquare = pawnAttacks[startSquare][i]
            if self.board[endSquare] is not Piece.EMPTY and not Piece.is_same_color(piece, self.board[endSquare]):
                self.possibleMoves.append(Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))

        # check for en passant
        if self.moveLog:
            lastMove = self.moveLog[-1]
            if lastMove.flag is Move.Flag.PAWN_TWO_FORWARD and not Piece.is_same_color(piece, lastMove.startPiece):
                direction = -dir
               
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

        