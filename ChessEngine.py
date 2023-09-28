import Classes.Piece as Piece
from Classes.Move import Move

"""
Defines the current game state (piece placement, current turn, and move log)
"""

# TODO: refactor current color

DEBUG = True


class GameState():
    START_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    directions = [8, -8, -1, 1, 7, -7, 9, -9]
    knightDirections = [15, 17, -17, -15, 10, -6, 6, -10]

    wQCastleMask = (1 << 2) | (1 << 3)
    wKCastleMask = (1 << 5) | (1 << 6)

    bQCastleMask = (1 << 58) | (1 << 59)
    bKCastleMask = (1 << 61) | (1 << 62)

    def __init__(self) -> None:
        self.board = [[Piece.EMPTY] for i in range(64)]
        self.whiteToMove = True
        self.currentColor = Piece.WHITE
        self.moveLog = []
        self.selected = None

        initPieceLists = [None if Piece.is_same_type(
            p, Piece.KING) else [] for p in Piece.pieces]
        self.pieceLists = dict(zip(Piece.pieces, initPieceLists))

        numSquaresToEdge = [[0] * 8 for i in range(64)]
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
            numSquaresToEdge[i] = [
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
                    y = int(endSquare / 8)
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
                    y = int(endSquare / 8)
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

        self.numSquaresToEdge = numSquaresToEdge
        self.knightMoves = knightMoves
        self.kingMoves = kingMoves
        self.knightAttackMaps = knightAttackMaps
        self.kingAttackMaps = kingAttackMaps
        self.pawnWhiteAttacks = pawnWhiteAttacks
        self.pawnBlackAttacks = pawnBlackAttacks
        self.pawnWhiteAttackMaps = pawnWhiteAttackMaps
        self.pawnBlackAttackMaps = pawnBlackAttackMaps

        self.wKSideCastle = True
        self.wQSideCastle = True
        self.bKSideCastle = True
        self.bQSideCastle = True

        self.enPassantSquare = None
        self.possibleMoves = []
        self.selectedMoves = []
        self.pinned = False
        self.inCheck = False
        self.inDoubleCheck = False

        self.promoteSquare = None

        # TODO: add fen position input with default start position
        self.set_state(self.START_POSITION)
        self.opponentAttackMap = 0
        self.pinnedMap = 0
        self.checkMap = 0
        self.generate_moves()

    # def perft(self, depth: int):
    #     nodes = 0
    #     moveList = []

    #     if depth == 0:
    #         return 1

    #     nMoves = self.generate_moves()

    #     return

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
                        square -= 1

        # Side to move
        self.whiteToMove = fields[1] == "w"
        self.currentColor = Piece.WHITE if self.whiteToMove else Piece.BLACK

        # Castling ability
        self.wKSideCastle = self.wQSideCastle = self.bKSideCastle = self.bQSideCastle = False

        if "K" in fields[2]:
            self.wKSideCastle = True
        if "Q" in fields[2]:
            self.wQSideCastle = True
        if "k" in fields[2]:
            self.bKSideCastle = True
        if "q" in fields[2]:
            self.bQSideCastle = True

        # En passant target square
        # Halfmove clock
        # Fullmove clock

    def is_diagonal(self, dir):
        return dir in {-9, -7, 7, 9}

    def get_rank(self, square: int):
        return int(square / 8)

    def within_board(self, square: int):
        return 0 <= square < 64

    # returns pinned piece movable squares for a sliding piece
    def pin_movable_squares_sliding(self, pieceSquare: int, startIndex: int, endIndex: int):

        squares = []
        for i in range(startIndex, endIndex):
            dir = self.directions[i]
            for j in range(self.numSquaresToEdge[pieceSquare][i]):
                square = pieceSquare + dir * (j + 1)
                if not self.pinnedMap & (1 << square):
                    break
                squares.append(square)

                # capture square of pinning piece
                if self.board[square] != Piece.EMPTY:
                    break

        return squares

    # returns movable squares to get out a check for a sliding piece
    def check_movable_squares_sliding(self, pieceSquare: int, startIndex: int, endIndex: int):

        squares = []
        for i in range(startIndex, endIndex):
            dir = self.directions[i]
            for j in range(self.numSquaresToEdge[pieceSquare][i]):
                square = pieceSquare + dir * (j + 1)
                if self.inCheck and self.checkMap & (1 << square):
                    squares.append(square)
                if self.board[square] != Piece.EMPTY:
                    break

        return squares

    # returns true if valid square is movable for a pawn piece
    def movable_pawn_square(self, endSquare: int):
        return (not self.pinned or (self.pinnedMap & 1 << endSquare)) and (not self.inCheck or (self.checkMap & 1 << endSquare))

    # TODO: check for pins and checkmate
    def generate_attack_map(self):

        self.opponentAttackMap = 0
        opponentColor = Piece.get_opposite_color(self.currentColor)

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

    def generate_attack_data(self):

        opponentColor = Piece.get_opposite_color(self.currentColor)
        kingSquare = self.pieceLists[self.currentColor | Piece.KING]
        self.pinned = False
        self.inCheck = False
        self.inDoubleCheck = False
        self.pinnedMap = 0
        self.checkMap = 0

        # sliding pieces pin/check
        for i in range(len(self.directions)):
            dir = self.directions[i]
            rayMask = 0
            friendlyBlock = False

            for j in range(self.numSquaresToEdge[kingSquare][i]):
                square = kingSquare + dir * (j + 1)
                piece = self.board[square]
                rayMask |= 1 << square

                if piece == Piece.EMPTY:
                    continue

                if Piece.is_same_color(self.currentColor, piece):
                    if not friendlyBlock:
                        friendlyBlock = True
                    # Two friendly pieces along ray, no check or pin
                    else:
                        break

                else:

                    if ((Piece.is_same_type(piece, Piece.QUEEN) or Piece.is_same_type(piece, Piece.ROOK)) and not self.is_diagonal(dir)) or (Piece.is_same_type(piece, Piece.BISHOP) and self.is_diagonal(dir)):
                        # Pin
                        if friendlyBlock:
                            self.pinnedMap |= rayMask
                            self.pinned = True
                        # Check
                        else:
                            self.checkMap |= rayMask
                            self.inDoubleCheck = self.inCheck
                            self.inCheck = True

            # king moves are possible only, stop searching for pins/checks
            if self.inDoubleCheck:
                return

        # knights check
        for knight in self.pieceLists[opponentColor | Piece.KNIGHT]:
            knightAttacks = self.knightAttackMaps[knight]
            if knightAttacks & (1 << kingSquare):
                self.checkMap |= knight
                self.inDoubleCheck = self.inCheck
                self.inCheck = True
                break

        # pawns check
        pawnAttackMap = self.pawnWhiteAttackMaps if opponentColor == Piece.WHITE else self.pawnBlackAttackMaps
        for pawn in self.pieceLists[opponentColor | Piece.PAWN]:
            pawnAttacks = pawnAttackMap[pawn]
            if pawnAttacks & (1 << kingSquare):
                self.checkMap |= pawn
                self.inDoubleCheck = self.inCheck
                self.inCheck = True
                break

    def generate_sliding_attacks(self, startSquare: int, startIndex: int, endIndex: int):

        for index in range(startIndex, endIndex):
            for num in range(self.numSquaresToEdge[startSquare][index]):
                endSquare = startSquare + (num + 1) * self.directions[index]
                self.opponentAttackMap |= 1 << endSquare
                if self.board[endSquare] is not Piece.EMPTY:
                    break

    def generate_moves(self):

        self.generate_attack_map()
        self.generate_attack_data()
        self.generate_king_moves(
            self.pieceLists[self.currentColor | Piece.KING], self.currentColor | Piece.KING)

        if self.inDoubleCheck:
            if DEBUG:
                print(len(self.possibleMoves))
            return

        for pawn in self.pieceLists[self.currentColor | Piece.PAWN]:
            self.generate_pawn_moves(pawn, self.currentColor | Piece.PAWN)

        for knight in self.pieceLists[self.currentColor | Piece.KNIGHT]:
            self.generate_knight_moves(
                knight, self.currentColor | Piece.KNIGHT)

        for bishop in self.pieceLists[self.currentColor | Piece.BISHOP]:
            self.generate_sliding_moves(
                bishop, self.currentColor | Piece.BISHOP)

        for rook in self.pieceLists[self.currentColor | Piece.ROOK]:
            self.generate_sliding_moves(rook, self.currentColor | Piece.ROOK)

        for queen in self.pieceLists[self.currentColor | Piece.QUEEN]:
            self.generate_sliding_moves(queen, self.currentColor | Piece.QUEEN)

        if DEBUG:
            print(len(self.possibleMoves))

    def generate_sliding_moves(self, startSquare: int, piece: int):

        # index in direction array
        startIndex = 4 if Piece.is_same_type(piece, Piece.BISHOP) else 0
        endIndex = 4 if Piece.is_same_type(piece, Piece.ROOK) else 8

        if self.pinned and self.pinnedMap & (1 << startSquare):
            if not self.inCheck:
                for square in self.pin_movable_squares_sliding(startSquare, startIndex, endIndex):
                    self.possibleMoves.append(
                        Move(startSquare, square, piece, self.board[square], Move.Flag.NONE))
            return

        if self.inCheck:
            for square in self.check_movable_squares_sliding(startSquare, startIndex, endIndex):
                self.possibleMoves.append(
                    Move(startSquare, square, piece, self.board[square], Move.Flag.NONE))
            return

        for index in range(startIndex, endIndex):
            for num in range(self.numSquaresToEdge[startSquare][index]):
                endSquare = startSquare + (num + 1) * self.directions[index]
                if self.board[endSquare] is Piece.EMPTY:
                    self.possibleMoves.append(
                        Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
                else:
                    if not Piece.is_same_color(piece, self.board[endSquare]):
                        self.possibleMoves.append(
                            Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
                    break

    def generate_pawn_moves(self, startSquare: int, piece: int):

        if Piece.is_white(piece):
            dir = self.directions[0]
            pawnStartRank = 1
            pawnAttacks = self.pawnWhiteAttacks
            promoteRank = 7
        else:
            dir = self.directions[1]
            pawnStartRank = 6
            pawnAttacks = self.pawnBlackAttacks
            promoteRank = 0

        # if self.pinned and self.pinnedMap & (1 << startSquare):
        #     if not self.inCheck:
        #         self.pinned = True
        #     else:
        #         return
        # else:
        #     self.pinned = False

        # check if pawn is pushable
        endSquare = startSquare + dir

        if self.within_board(endSquare) and self.board[endSquare] is Piece.EMPTY and self.movable_pawn_square(endSquare):

            if self.get_rank(endSquare) == promoteRank:
                self.add_pawn_promotion_moves(startSquare, endSquare, piece)
            else:
                self.possibleMoves.append(
                    Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))
                if self.get_rank(startSquare) == pawnStartRank and self.board[endSquare + dir] is Piece.EMPTY:
                    self.possibleMoves.append(Move(
                        startSquare, endSquare + dir, piece, self.board[endSquare + dir], Move.Flag.PAWN_TWO_FORWARD))

        # check for pawn captures
        for i in range(len(pawnAttacks[startSquare])):
            endSquare = pawnAttacks[startSquare][i]
            if self.board[endSquare] is not Piece.EMPTY and not Piece.is_same_color(piece, self.board[endSquare]) and self.movable_pawn_square(endSquare):
                if self.get_rank(endSquare) == promoteRank:
                    self.add_pawn_promotion_moves(
                        startSquare, endSquare, piece)
                else:
                    self.possibleMoves.append(
                        Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.NONE))

        # check for en passant
        if self.moveLog:
            lastMove = self.moveLog[-1]
            if lastMove.flag is Move.Flag.PAWN_TWO_FORWARD and not Piece.is_same_color(piece, lastMove.startPiece):
                direction = -dir

                if lastMove.endSquare is startSquare + 1 or lastMove.endSquare is startSquare - 1:
                    endSquare = lastMove.endSquare + direction
                    if self.movable_pawn_square(endSquare):
                        self.possibleMoves.append(
                            Move(startSquare, endSquare, piece, self.board[endSquare], Move.Flag.EN_PASSANT))
                        self.enPassantSquare = lastMove.endSquare

    def add_pawn_promotion_moves(self, startSquare: int, endSquare: int, piece: int):
        self.possibleMoves.append(Move(
            startSquare, endSquare, piece, self.board[endSquare], Move.Flag.PROMOTE_KNIGHT))
        self.possibleMoves.append(Move(
            startSquare, endSquare, piece, self.board[endSquare], Move.Flag.PROMOTE_BISHOP))
        self.possibleMoves.append(Move(
            startSquare, endSquare, piece, self.board[endSquare], Move.Flag.PROMOTE_ROOK))
        self.possibleMoves.append(Move(
            startSquare, endSquare, piece, self.board[endSquare], Move.Flag.PROMOTE_QUEEN))

    def generate_knight_moves(self, startSquare: int, piece: int):

        for i in range(len(self.knightMoves[startSquare])):
            endSquare = startSquare + self.knightMoves[startSquare][i]
            target = self.board[endSquare]
            if target is Piece.EMPTY:
                self.possibleMoves.append(
                    Move(startSquare, endSquare, piece, target, Move.Flag.NONE))
            elif not Piece.is_same_color(piece, target):
                self.possibleMoves.append(
                    Move(startSquare, endSquare, piece, target, Move.Flag.NONE))

    def generate_king_moves(self, startSquare: int, piece: int):

        for i in range(len(self.kingMoves[startSquare])):
            endSquare = startSquare + self.kingMoves[startSquare][i]
            target = self.board[endSquare]
            if (target is Piece.EMPTY or not Piece.is_same_color(piece, target)) and not self.opponentAttackMap & (1 << endSquare):
                self.possibleMoves.append(
                    Move(startSquare, endSquare, piece, target, Move.Flag.NONE))

        # check for castle
        if not self.inCheck:
            if self.whiteToMove:

                if self.wQSideCastle and not self.opponentAttackMap & self.wQCastleMask:
                    isEmpty = True
                    for i in range(1, 4):
                        if self.board[i] is not Piece.EMPTY:
                            isEmpty = False
                            break
                    if isEmpty:
                        self.possibleMoves.append(
                            Move(4, 2, piece, Piece.EMPTY, Move.Flag.CASTLE))

                if self.wKSideCastle and not self.opponentAttackMap & self.wKCastleMask:
                    for i in range(5, 7):
                        if self.board[i] is not Piece.EMPTY:
                            return
                    self.possibleMoves.append(
                        Move(4, 6, piece, Piece.EMPTY, Move.Flag.CASTLE))

            else:

                if self.bQSideCastle and not self.opponentAttackMap & self.bQCastleMask:
                    isEmpty = True
                    for i in range(57, 60):
                        if self.board[i] is not Piece.EMPTY:
                            isEmpty = False
                            break
                    if isEmpty:
                        self.possibleMoves.append(
                            Move(60, 58, piece, Piece.EMPTY, Move.Flag.CASTLE))

                if self.bKSideCastle and not self.opponentAttackMap & self.bKCastleMask:
                    for i in range(61, 63):
                        if self.board[i] is not Piece.EMPTY:
                            return
                    self.possibleMoves.append(
                        Move(60, 62, piece, Piece.EMPTY, Move.Flag.CASTLE))

    def make_move(self, move: Move):
        pieceList = self.pieceLists[move.startPiece]
        if Piece.is_same_type(Piece.KING, move.startPiece):
            self.pieceLists[move.startPiece] = move.endSquare
        else:
            pieceList[pieceList.index(move.startSquare)] = move.endSquare

        if move.endPiece is not Piece.EMPTY:
            self.pieceLists[move.endPiece].remove(move.endSquare)

        self.board[move.startSquare] = Piece.EMPTY
        self.board[move.endSquare] = move.startPiece

        # En passant
        if move.flag == Move.Flag.EN_PASSANT:
            self.pieceLists[self.board[self.enPassantSquare]].remove(
                self.enPassantSquare)

            self.board[self.enPassantSquare] = Piece.EMPTY
            self.enPassantSquare = None

        # Castling rights

        if self.bQSideCastle | self.bKSideCastle:

            if move.startPiece is Piece.BLACK_KING:
                self.bQSideCastle = self.bKSideCastle = False

            elif move.startPiece is Piece.BLACK_ROOK:
                if move.startSquare == 56:
                    self.bQSideCastle = False
                if move.startSquare == 63:
                    self.bKSideCastle = False

            elif move.endPiece is Piece.BLACK_ROOK:
                if move.endSquare == 56:
                    self.bQSideCastle = False
                if move.endSquare == 63:
                    self.bKSideCastle = False

        if self.wQSideCastle | self.wKSideCastle:

            if move.startPiece is Piece.WHITE_KING:
                self.wQSideCastle = self.wKSideCastle = False

            elif move.startPiece is Piece.WHITE_ROOK:
                if move.startSquare == 0:
                    self.wQSideCastle = False
                if move.startSquare == 7:
                    self.wKSideCastle = False

            elif move.endPiece is Piece.WHITE_ROOK:
                if move.endSquare == 0:
                    self.wQSideCastle = False
                if move.endSquare == 7:
                    self.wKSideCastle = False

        # Castling
        if move.flag is Move.Flag.CASTLE:
            if move.startSquare == 4:
                rooksList = self.pieceLists[Piece.WHITE_ROOK]
                self.wKSideCastle = False
                self.wQSideCastle = False

                if move.startSquare < move.endSquare:
                    rooksList[rooksList.index(7)] = 5
                    self.board[7] = Piece.EMPTY
                    self.board[5] = Piece.WHITE_ROOK
                else:
                    rooksList[rooksList.index(0)] = 3
                    self.board[0] = Piece.EMPTY
                    self.board[3] = Piece.WHITE_ROOK

            else:
                rooksList = self.pieceLists[Piece.BLACK_ROOK]
                self.bKSideCastle = False
                self.bQSideCastle = False

                if move.startSquare < move.endSquare:
                    rooksList[rooksList.index(63)] = 61
                    self.board[63] = Piece.EMPTY
                    self.board[61] = Piece.BLACK_ROOK
                else:
                    rooksList[rooksList.index(56)] = 59
                    self.board[56] = Piece.EMPTY
                    self.board[59] = Piece.BLACK_ROOK

        # Promotion
        if move.flag in {Move.Flag.PROMOTE_KNIGHT, Move.Flag.PROMOTE_BISHOP, Move.Flag.PROMOTE_ROOK, Move.Flag.PROMOTE_QUEEN}:

            self.pieceLists[move.startPiece].remove(move.endSquare)
            color = Piece.WHITE if Piece.is_white(
                move.startPiece) else Piece.BLACK

            promotePiece = int(move.flag)
            self.pieceLists[color | promotePiece].append(move.endSquare)
            self.board[move.endSquare] = color | promotePiece

        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        self.currentColor = Piece.get_opposite_color(self.currentColor)

    # TODO: unmake move function
    def unmake_move(self):

        if len(self.moveLog) == 0:
            return

        lastMove = self.moveLog[-1]

        match lastMove.flag:
            case Move.Flag.NONE | Move.Flag.PAWN_TWO_FORWARD:
                pass
            case Move.Flag.CASTLE:
                pass
            case Move.Flag.EN_PASSANT:
                pass
            # Promotion Moves
            case _:
                pass

        return
