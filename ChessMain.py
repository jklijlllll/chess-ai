import pygame as p
import pygame_menu as pm
import ChessEngine
import Classes.Piece as Piece
from Classes.Selected import Selected
from Classes.Move import Move
import random

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

PROMOTE_MOVE_FLAG = Move.Flag.NONE
PROMOTE_SELECT = False
PROMOTE_MOUSE_OVER = False

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
# TODO: refactor whiteToMove to piece color
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    menuTheme = pm.Theme(background_color=p.Color(255, 255, 255), title=False, selection_color=p.Color(0, 0, 0))
    whitePromoteMenu = pm.Menu("", width= SQ_SIZE, height= SQ_SIZE * 4, theme=menuTheme, overflow=(False, False), keyboard_enabled=False, enabled=False)
    
    game_state = ChessEngine.GameState()
    loadImages()
    initPromoteMenu(whitePromoteMenu, "w")
    promoteMove = None
    global PROMOTE_MOUSE_OVER
    
    running = True

    while running:
        
        events = p.event.get()
        for e in events:
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                square = int((HEIGHT - p.mouse.get_pos()[1] )/ SQ_SIZE) * DIMENSION + int(p.mouse.get_pos()[0] /SQ_SIZE)
                piece = game_state.board[square]
                
                if game_state.selected is not None:
                    
                    move = next((m for m in game_state.selectedMoves if m.endSquare is square), None)

                    if move is not None:
                        if move.flag not in {Move.Flag.PROMOTE_KNIGHT, Move.Flag.PROMOTE_BISHOP, Move.Flag.PROMOTE_ROOK, Move.Flag.PROMOTE_QUEEN}:
                            game_state.make_move(move)
                        else:
                            promoteMove = move
                            game_state.promoteSquare = promoteMove.endSquare
                    
                    if game_state.promoteSquare is None:
                        game_state.selected = None
                        game_state.possibleMoves = []
                        game_state.generate_moves()
                    else:
                        x = game_state.promoteSquare % 8 * SQ_SIZE
                        y = (63 - game_state.promoteSquare) / 8 * SQ_SIZE
                        if game_state.whiteToMove:
                            whitePromoteMenu.set_absolute_position(x, y)
                            whitePromoteMenu.enable()
                            PROMOTE_MOUSE_OVER = True if whitePromoteMenu.get_mouseover_widget() is not None else False
                        
                    # if game_state.opponentAttackMap & (1 << game_state.pieceLists[(Piece.WHITE if game_state.whiteToMove else Piece.BLACK) | Piece.KING]):
                    #     print("check")
                else:
                    if piece is not Piece.EMPTY and game_state.whiteToMove is Piece.is_white(piece):
                        game_state.selected = Selected(square, piece)
                        game_state.selectedMoves = [m for m in game_state.possibleMoves if m.startSquare == square]
                    else:
                        game_state.selected = None
                        game_state.selectedMoves = []
        
        # if not game_state.whiteToMove:
        #     game_state.make_move(random.choice(game_state.possibleMoves))
        #     game_state.generate_moves()
            
        drawGameState(screen, game_state)

        # Select promote piece
        if game_state.promoteSquare is not None:
            if whitePromoteMenu.is_enabled():
                whitePromoteMenu.update(events)
                whitePromoteMenu.draw(screen)
            
            global PROMOTE_SELECT
            if PROMOTE_SELECT:
                global PROMOTE_MOVE_FLAG

                whitePromoteMenu.disable()
               
                promoteMove.flag = PROMOTE_MOVE_FLAG

                PROMOTE_SELECT = False
                PROMOTE_MOVE_FLAG = Move.Flag.NONE

                game_state.make_move(promoteMove)
                promoteMove = None
                game_state.promoteSquare = None

                game_state.selected = None
                game_state.possibleMoves = []
                game_state.generate_moves()
            
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

def initPromoteMenu(menu: pm.Menu, color: str):

    queenPromote = menu.add.image("ChessAI/Images/" + color + "Q.png", selectable=True, onselect=selectQueen)
    queenPromote.resize(width= SQ_SIZE, height= SQ_SIZE)
    queenPromote.set_padding(0)
    queenPromote.set_selection_effect(None)
   
    rookPromote = menu.add.image("ChessAI/Images/" + color + "R.png", selectable=True, onselect=selectRook)
    rookPromote.resize(width= SQ_SIZE, height= SQ_SIZE)
    rookPromote.set_padding(0)
    rookPromote.set_selection_effect(None)

    bishopPromote = menu.add.image("ChessAI/Images/" + color + "B.png", selectable=True, onselect=selectBishop)
    bishopPromote.resize(width= SQ_SIZE, height= SQ_SIZE)
    bishopPromote.set_padding(0)
    bishopPromote.set_selection_effect(None)

    knightPromote = menu.add.image("ChessAI/Images/" + color + "N.png", selectable=True, onselect=selectKnight)
    knightPromote.resize(width= SQ_SIZE, height= SQ_SIZE)
    knightPromote.set_padding(0)
    knightPromote.set_selection_effect(None)

    menu.set_onupdate(onMenuUpdate)
    menu.set_onmouseleave(onMenuMouseLeave)
    menu.set_onmouseover(onMenuMouseOver)


def selectQueen(selected: bool, widget, menu: pm.Menu):
    if selected:
        global PROMOTE_MOVE_FLAG
        PROMOTE_MOVE_FLAG = Move.Flag.PROMOTE_QUEEN
        
       
def selectRook(selected: bool, widget, menu: pm.Menu):
    if selected:
        global PROMOTE_MOVE_FLAG
        PROMOTE_MOVE_FLAG = Move.Flag.PROMOTE_ROOK
        

def selectBishop(selected: bool, widget, menu: pm.Menu):
    if selected:
        global PROMOTE_MOVE_FLAG
        PROMOTE_MOVE_FLAG = Move.Flag.PROMOTE_BISHOP
        

def selectKnight(selected: bool, widget, menu: pm.Menu):
    if selected:
        global PROMOTE_MOVE_FLAG
        PROMOTE_MOVE_FLAG = Move.Flag.PROMOTE_KNIGHT

def onMenuUpdate(event_list, menu: pm.Menu):
 
    if PROMOTE_MOUSE_OVER and next((e for e in event_list if e.type == p.MOUSEBUTTONDOWN), None):
        global PROMOTE_SELECT
        PROMOTE_SELECT = True

def onMenuMouseLeave():
    global PROMOTE_MOUSE_OVER
    PROMOTE_MOUSE_OVER = False

def onMenuMouseOver():
    global PROMOTE_MOUSE_OVER
    PROMOTE_MOUSE_OVER = True

if __name__ == "__main__":
    main()

