import pygame as p
import ChessEngine
import Classes.Piece as Piece
from Classes.Move import Move
from Classes.Selected import Selected

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Loads piece images
"""
def loadImages():
    
    pieceDict = dict(zip(Piece.pieces, Piece.pieceImageNames))

    for piece in Piece.pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("ChessAI/Images/" + pieceDict[piece] + ".png"), (SQ_SIZE, SQ_SIZE))

"""
Handles user input and graphics updates
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    loadImages()
    running = True
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if game_state.whiteToMove and e.type == p.MOUSEBUTTONDOWN:
                square = int((HEIGHT - p.mouse.get_pos()[1] )/ SQ_SIZE) * DIMENSION + int(p.mouse.get_pos()[0] /SQ_SIZE)
                piece = game_state.board[square]
                
                if game_state.selected is not None:
                    
                    move = next((m for m in game_state.selectedMoves if m.endSquare is square), None)

                    if move is not None:
 
                        pieceList = game_state.pieceLists[move.startPiece]
                        if Piece.is_same_type(Piece.KING, move.startPiece):
                            pieceList = move.endSquare
                        else:
                            pieceList[pieceList.index(move.startSquare)] = move.endSquare
                        
                        if piece is not Piece.EMPTY:
                            game_state.pieceLists[piece].remove(move.endSquare)

                        game_state.board[game_state.selected.square] = Piece.EMPTY
                        game_state.board[move.endSquare] = game_state.selected.piece

                        if move.flag == Move.Flag.EN_PASSANT:
                            game_state.pieceLists[game_state.board[game_state.enPassantSquare]].remove(game_state.enPassantSquare)

                            game_state.board[game_state.enPassantSquare] = Piece.EMPTY
                            game_state.enPassantSquare = None

                        if move.startPiece is Piece.BLACK_ROOK:
                            if move.startSquare == 56:
                                game_state.blackQueenSideCastle = False
                            if move.startSquare == 63:
                                game_state.blackKingSideCastle = False

                        if move.endPiece is Piece.BLACK_ROOK:
                            if move.endSquare == 56:
                                game_state.blackQueenSideCastle = False
                            if move.endSquare == 63:
                                game_state.blackKingSideCastle = False

                        if move.startPiece is Piece.WHITE_ROOK:
                            if move.startSquare == 0:
                                game_state.whiteQueenSideCastle = False
                            if move.startSquare == 7:
                                game_state.whiteKingSideCastle = False

                        if move.endPiece is Piece.WHITE_ROOK:
                            if move.endSquare == 0:
                                game_state.whiteQueenSideCastle = False
                            if move.endSquare == 7:
                                game_state.whiteKingSideCastle = False

                        if move.flag is Move.Flag.CASTLE:
                            if move.startSquare == 4:
                                rooksList = game_state.pieceLists[Piece.WHITE_ROOK]
                                game_state.whiteKingSideCastle = False
                                game_state.whiteQueenSideCastle = False

                                if move.startSquare < move.endSquare:
                                    rooksList[rooksList.index(7)] = 5
                                    game_state.board[7] = Piece.EMPTY
                                    game_state.board[5] = Piece.WHITE_ROOK
                                else:
                                    rooksList[rooksList.index(0)] = 3
                                    game_state.board[0] = Piece.EMPTY
                                    game_state.board[3] = Piece.WHITE_ROOK

                            else:
                                rooksList = game_state.pieceLists[Piece.BLACK_ROOK]
                                game_state.blackKingSideCastle = False
                                game_state.blackQueenSideCastle = False

                                if move.startSquare < move.endSquare:
                                    rooksList[rooksList.index(63)] = 61
                                    game_state.board[63] = Piece.EMPTY
                                    game_state.board[61] = Piece.BLACK_ROOK
                                else:
                                    rooksList[rooksList.index(56)] = 59
                                    game_state.board[56] = Piece.EMPTY
                                    game_state.board[59] = Piece.BLACK_ROOK

                        if move.flag in {Move.Flag.PROMOTE_KNIGHT, Move.Flag.PROMOTE_BISHOP, Move.Flag.PROMOTE_ROOK, Move.Flag.PROMOTE_QUEEN}:
                            while running:
                                promoteInput = input("Promote pawn (k, b, r, q): ")
                                
                                if promoteInput == "k":
                                    move = next((m for m in game_state.selectedMoves if m.flag is Move.Flag.PROMOTE_KNIGHT and m.endSquare is square), None)
                                    promotePiece = Piece.KNIGHT
                                    promote = True
                                if  promoteInput == "b":
                                    move = next((m for m in game_state.selectedMoves if m.flag is Move.Flag.PROMOTE_BISHOP and m.endSquare is square), None)
                                    promotePiece = Piece.BISHOP
                                    promote = True
                                if  promoteInput == "r":
                                    move = next((m for m in game_state.selectedMoves if m.flag is Move.Flag.PROMOTE_ROOK and m.endSquare is square), None)
                                    promotePiece = Piece.ROOK
                                    promote = True
                                if  promoteInput == "q":
                                    move = next((m for m in game_state.selectedMoves if m.flag is Move.Flag.PROMOTE_QUEEN and m.endSquare is square), None)
                                    promotePiece = Piece.QUEEN
                                    promote = True

                                if promote:
                                    game_state.pieceLists[move.startPiece].remove(move.endSquare)
                                    color = Piece.WHITE if Piece.is_white(move.startPiece) else Piece.BLACK
 
                                    game_state.pieceLists[color | promotePiece].append(move.endSquare)
                                    game_state.board[move.endSquare] = color | promotePiece
                                    break

                        game_state.moveLog.append(move)
                        game_state.whiteToMove = True

                    game_state.selected = None
                    game_state.possibleMoves = []
                    game_state.generate_moves()
                    # if game_state.opponentAttackMap & (1 << game_state.pieceLists[(Piece.WHITE if game_state.whiteToMove else Piece.BLACK) | Piece.KING]):
                    #     print("check")
                else:
                    if piece is not Piece.EMPTY and game_state.whiteToMove is Piece.is_white(piece):
                        game_state.selected = Selected(square, piece)
                        game_state.selectedMoves = [m for m in game_state.possibleMoves if m.startSquare == square]
                    else:
                        game_state.selected = None
                        game_state.selectedMoves = []
        
        if not game_state.whiteToMove:
            game_state.whiteToMove = False
            
        drawGameState(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
Draws all the graphics within the current game state
"""
def drawGameState(screen, game_state):
    drawBoard(screen, game_state.board, game_state.selected, game_state.selectedMoves , game_state.moveLog, game_state.opponentAttackMap)

"""
Draws the chess board
"""
def drawBoard(screen, board, selected, selectedMoves, moveLog, attackMap):

    for i in range(DIMENSION * DIMENSION):
        rank = int(i / DIMENSION)
        file = i % DIMENSION
        # if attackMap is not None and attackMap & (1 << i):
        #      p.draw.rect(screen, p.Color(255,0,0) , p.Rect(file * SQ_SIZE, (DIMENSION - rank - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.draw.rect(screen, p.Color(238,238,210) if (rank + file) % 2 == 0 else p.Color(118,150,86), p.Rect(file * SQ_SIZE, (DIMENSION - rank - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        piece = board[i]
        if piece != Piece.EMPTY:
            screen.blit(IMAGES[piece], p.Rect(file * SQ_SIZE, (DIMENSION - rank - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if selected is not None:
        p.draw.rect(screen, p.Color(186,202,68), p.Rect(selected.square % DIMENSION * SQ_SIZE, (DIMENSION - int(selected.square / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        screen.blit(IMAGES[selected.piece], p.Rect(selected.square % DIMENSION * SQ_SIZE, (DIMENSION - int(selected.square / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        if selectedMoves is not None:
            for i in range(len(selectedMoves)):
                square = selectedMoves[i].endSquare     
                p.draw.rect(screen, p.Color(255,255,255), p.Rect(square % DIMENSION * SQ_SIZE, (DIMENSION - int(square / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                if board[square] is not Piece.EMPTY:
                    screen.blit(IMAGES[board[square]], p.Rect(square % DIMENSION * SQ_SIZE, (DIMENSION - int(square / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    elif moveLog:
        lastMove = moveLog[-1]
        p.draw.rect(screen, p.Color(186,202,68), p.Rect(lastMove.startSquare % DIMENSION * SQ_SIZE,  (DIMENSION - int(lastMove.startSquare / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        # start square will always be empty
        p.draw.rect(screen, p.Color(186,202,68), p.Rect(lastMove.endSquare % DIMENSION * SQ_SIZE, (DIMENSION - int(lastMove.endSquare / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        screen.blit(IMAGES[board[lastMove.endSquare]], p.Rect(lastMove.endSquare % DIMENSION * SQ_SIZE, (DIMENSION - int(lastMove.endSquare / DIMENSION) - 1)* SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()

        

