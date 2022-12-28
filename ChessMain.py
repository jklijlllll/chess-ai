import pygame as p
import ChessEngine
import Piece

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
                rank = int(p.mouse.get_pos()[1] / SQ_SIZE)
                file = int(p.mouse.get_pos()[0] / SQ_SIZE)
                square = game_state.board[rank][file]
                if game_state.selected is not None and square is Piece.EMPTY:
                    game_state.board[game_state.selected[1]][game_state.selected[2]] = Piece.EMPTY
                    game_state.board[rank][file] = game_state.selected[0]
                    game_state.selected = None
                if square is not Piece.EMPTY:
                    game_state.selected = [square, rank, file]    
            
        drawGameState(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
Draws all the graphics within the current game state
"""
def drawGameState(screen, game_state):
    drawBoard(screen)
    drawPieces(screen, game_state.board)

"""
Draws the chess board
"""
def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            p.draw.rect(screen, p.Color(238,238,210) if (r + c) % 2 == 0 else p.Color(118,150,86), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draws the pieces based on the current game state
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != Piece.EMPTY:
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()

        

