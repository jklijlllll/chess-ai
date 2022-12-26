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
    pieces = [Piece.WHITE | Piece.PAWN,  Piece.WHITE | Piece.KNIGHT,   Piece.WHITE | Piece.BISHOP,   
    Piece.WHITE | Piece.ROOK,   Piece.WHITE | Piece.QUEEN, Piece.WHITE | Piece.KING, 
    Piece.BLACK | Piece.PAWN,  Piece.BLACK | Piece.KNIGHT,   Piece.BLACK | Piece.BISHOP,   
    Piece.BLACK | Piece.ROOK,   Piece.BLACK | Piece.QUEEN,  Piece.BLACK | Piece.KING]
    pieceImageNames = ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
    pieceDict = dict(zip(pieces, pieceImageNames))

    for piece in pieces:
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

        

