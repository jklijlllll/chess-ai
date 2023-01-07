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
            if e.type == p.MOUSEBUTTONDOWN:
                square = int((HEIGHT - p.mouse.get_pos()[1] )/ SQ_SIZE) * DIMENSION + int(p.mouse.get_pos()[0] /SQ_SIZE)
                piece = game_state.board[square]
                if game_state.selected is not None:
                    move = next((m for m in game_state.possibleMoves if m.endSquare is square), None)

                    if move is not None:
                        game_state.board[game_state.selected.square] = Piece.EMPTY
                        game_state.board[square] = game_state.selected.piece
                        if move.flag is Move.Flag.EN_PASSANT:
                            game_state.board[game_state.enPassantSquare] = Piece.EMPTY
                            game_state.enPassantSquare = None
                        game_state.moveLog.append(move)
                        game_state.whiteToMove = not game_state.whiteToMove
             
                    game_state.selected = None
                    game_state.possibleMoves = []
                    
                else:
                    if piece is not Piece.EMPTY and game_state.whiteToMove is Piece.is_white(piece):
                        game_state.selected = Selected(square, piece)
                        game_state.generate_move(square, piece)
                    else:
                        game_state.selected = None
                        
        drawGameState(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
Draws all the graphics within the current game state
"""
def drawGameState(screen, game_state):
    drawBoard(screen, game_state.board, game_state.selected, game_state.possibleMoves ,game_state.moveLog)

"""
Draws the chess board
"""
def drawBoard(screen, board, selected, possibleMoves, moveLog):

    for i in range(DIMENSION * DIMENSION):
        rank = int(i / DIMENSION)
        file = i % DIMENSION
        p.draw.rect(screen, p.Color(238,238,210) if (rank + file) % 2 == 0 else p.Color(118,150,86), p.Rect(file * SQ_SIZE, (DIMENSION - rank - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        piece = board[i]
        if piece != Piece.EMPTY:
            screen.blit(IMAGES[piece], p.Rect(file * SQ_SIZE, (DIMENSION - rank - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if selected is not None:
        p.draw.rect(screen, p.Color(186,202,68), p.Rect(selected.square % DIMENSION * SQ_SIZE, (DIMENSION - int(selected.square / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        screen.blit(IMAGES[selected.piece], p.Rect(selected.square % DIMENSION * SQ_SIZE, (DIMENSION - int(selected.square / DIMENSION) - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if possibleMoves is not None:
            for i in range(len(possibleMoves)):
                square = possibleMoves[i].endSquare     
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

        

