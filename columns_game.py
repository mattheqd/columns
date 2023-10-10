import pygame
import game_mechanics
import random

_INITIAL_WIDTH = 360
_INITIAL_HEIGHT = 780
_FRAME_RATE = 30
_BACKGROUND_COLOR = pygame.Color(000, 000, 000)

class ColumnsGame:
    def __init__(self):
        self._game_state = game_mechanics.GameState(create_empty_board(13,6))
        self._game_active = True
        self._display_game = True
        self._in_matching = False
        self._frame_timer = _FRAME_RATE
        self._color_dictionary = {'R': pygame.Color(255,0,0), 'O': pygame.Color(255,165,0), 'Y': pygame.Color(255,255,0), 'G': pygame.Color(0,128,0),
        'B': pygame.Color(0,0,255), 'I': pygame.Color(75,0,130), 'V': pygame.Color(238,130,238), ' ': pygame.Color(0,0,0,0), '|': pygame.Color(192,192,192)}

    def run(self) -> None:
        pygame.init()

        try:
            clock = pygame.time.Clock()
            self._create_surface((_INITIAL_WIDTH, _INITIAL_HEIGHT))
            while self._game_active:
                clock.tick(_FRAME_RATE)
                if self._game_state.faller_in_frozen() and not self._in_matching:
                    faller = self._create_faller()
                    self._game_state.put_faller_in_board(faller)
                    column = faller[0]
                    index_to_be_removed = 3
                # Creates a faller and inserts it into the board when appropiate (not in matching and board is in frozen)
                if not self._in_matching:
                    column = self._handle_events(column, index_to_be_removed)
                index_to_be_removed = self._pass_time(column, index_to_be_removed)
                self._determine_if_should_match()
                self._draw_frame()
                self._end_game_on_death()
            if self._display_game:
                self._show_board_until_exit()
        finally:
            pygame.quit()

    def _game_board(self) -> list[list[str]]:
        'Returns the game board of a GameState object'
        return self._game_state.return_board()

    def _show_board_until_exit(self) -> None:
        '''
        Shows the board after the game has ended to allow users to 
        figure out how they lost until they manually exit the pygame window
        '''
        self._generate_game_over_image()
        while True:
            should_break = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    should_break = True
                elif event.type == pygame.VIDEORESIZE:
                    self._create_surface(event.size)
                    self._draw_board()
                    self._generate_game_over_image()
            if should_break:
                break

    def _generate_game_over_image(self) -> None:
        'Adds a "GAME OVER" text image to the board'
        font_size = int(self._surface.get_width()/6)
        font = pygame.font.SysFont(None, font_size)
        text_image = font.render('GAME OVER', True, pygame.Color(255, 255, 255))
        self._surface.blit(text_image, (0, 0))
        pygame.display.flip()
            
    def _pass_time(self, column, index_to_be_removed) -> int:
        '''
        Handles how a faller should act with the passage of time, which occurs after 1 second.
        Passage of time actions include matching, falling, landing, and freezing.
        '''
        self._frame_timer -= 1
        if self._frame_timer == 0:
            if self._in_matching:
                positions = self._game_state.single_match()
                if self._game_state.faller_in_matching():
                    self._game_state.remove_match(positions)
                else:
                    self._game_state.add_signal(positions)
            else:
                self._game_state.faller_pass_time(column, index_to_be_removed)
                index_to_be_removed += 1
            self._frame_timer = _FRAME_RATE
        return index_to_be_removed


    def _determine_if_should_match(self) -> None:
        'Sets the in_matching state of the game board based on if matching should begin'
        if (self._game_state.faller_in_frozen() or self._game_state.faller_in_matching()):
            self._in_matching = True
        if not self._game_state._still_matches():
            self._in_matching = False

    def _end_game_on_death(self) -> None:
        'Ends the program when the a column is frozen and full with no matches'
        if self._game_state.check_if_dead() and self._game_state.faller_in_frozen() and not self._in_matching:
            self._stop_game()

    def _create_faller(self) -> tuple[int, list[str]]:
        'Randomly creates a faller in a non-full column, unless all columns are full, which causes the game to end'
        if self._check_if_all_full_columns():
            self._stop_game()
        while True:
            colors = ['[R]', '[O]', '[Y]', '[G]', '[B]', '[I]', '[V]']
            contents = []
            for i in range(3):
                contents.append(random.choice(colors))
            column = random.randrange(1, 6, 1)
            faller = (column, contents)
            if not self._game_state.column_is_full(faller[0]):
                break
        return faller

    def _check_if_all_full_columns(self) -> bool:
        'checks if all columns are full of landed pieces'
        for column in range(6):
            if not self._game_state.column_is_full(column):
                return False
        return True

    def _handle_events(self, column, left_off) -> None:
        'Handles all valid pygame events and key presses. Then relays the information from handle keys regarding column'
        for event in pygame.event.get():
            column = self._handle_event(event, column, left_off)

        return column

    def _handle_event(self, event, column, left_off) -> None:
        'Handles manual exit of the programm resizing of the pygame window, and faller commands'
        if event.type == pygame.QUIT:
            self._stop_game()
            self._display_game = False
        elif event.type == pygame.VIDEORESIZE:
            self._create_surface(event.size)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                return self._game_state.faller_move_delta(column, -1)
            elif event.key == pygame.K_RIGHT:
                return self._game_state.faller_move_delta(column, 1)
            elif event.key == pygame.K_SPACE:
                self._game_state.faller_reverse(column, left_off)
        return column

    def _stop_game(self) -> None:
        'Changes the game active flag to false, ending the overarching pygame while game active loop'
        self._game_active = False

    def _create_surface(self, size: tuple[int, int]) -> None:
        'Creates a resizable pygame surface'
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)

    def _draw_frame(self) -> None:
        'Draws the game board at a given frame'
        self._surface.fill(_BACKGROUND_COLOR)
        self._draw_board()
        pygame.display.flip()

    def _draw_board(self) -> None:
        'Draws all indexes of the board onto a pygame surface'
        x_fract = 0
        y_fract = 0
        for col in range(2, len(self._game_board()[0])):
            for row in range(len(self._game_board())):
                symbol = self._game_board()[row][col]
                color = symbol[1]
                self._draw_jewel(x_fract, y_fract, color,symbol)
                x_fract += 1/6
            x_fract = 0
            y_fract += 1/13

    def _draw_jewel(self, x_fract, y_fract, color,symbol) -> None:
        'Draws a jewel onto the pygame surface, with a border signaling the current state of it'
        width_pixel = self._frac_x_to_pixel_x(1/6)
        height_pixel = self._frac_y_to_pixel_y(1/13)
        top_left_pixel_x = self._frac_x_to_pixel_x(x_fract)
        top_left_pixel_y = self._frac_y_to_pixel_y(y_fract)
        border_color = self._determine_border_color(symbol)
        border_width = self._determine_border_width(width_pixel, height_pixel)
        pygame.draw.rect(self._surface, pygame.Color(border_color), (top_left_pixel_x, top_left_pixel_y, width_pixel, height_pixel))
        pygame.draw.rect(self._surface, pygame.Color(self._color_dictionary[color]), (top_left_pixel_x + 
            border_width, top_left_pixel_y + border_width, width_pixel - border_width*2, height_pixel - border_width*2))

    def _determine_border_color(self, symbol) -> pygame.Color:
        'Determines the color of the border of a jewel based on if it is in a landed, falling, matching, or frozen state'
        if symbol.startswith('|'):
            border_color = pygame.Color(128,128,128)
        elif symbol.startswith('['):
            border_color = pygame.Color(255,255,255)
        elif symbol.startswith('*'):
            border_color = pygame.Color(255,215,0)
        else:
            border_color = pygame.Color(0,0,0)
        return border_color

    def _determine_border_width(self, width_pixel, height_pixel) -> int:
        'Determines the width of the jewel border'
        if width_pixel < height_pixel:
            border_width = int(width_pixel/10)
        else:
            border_width = int(height_pixel/10)
        return border_width

    
    def _frac_x_to_pixel_x(self, frac_x: float) -> int:
        'Converts a fraction format pygame x coordinate to a definitive pixel coordinate'
        return self._frac_to_pixel(frac_x, self._surface.get_width())


    def _frac_y_to_pixel_y(self, frac_y: float) -> int:
        'Converts a fraction format pygame x coordinate to a definitive pixel coordinate'
        return self._frac_to_pixel(frac_y, self._surface.get_height())


    def _frac_to_pixel(self, frac: float, max_pixel: int) -> int:
        'Converts a fraction format pygame value to a definitive pixel value'
        return int(frac * max_pixel)


def create_empty_board(rows: int, columns: int) -> list[list[str]]:
    '''
    Returns a columns game board based on a specified number of rows and columns. 
    Invisible rows are added to take into account the faller that will be later added
    '''
    board = []
    for col in range(columns):
        board.append([])
        for row in range(rows):
            board[-1].append('   ')
    _add_invisible_rows(board)
    return board


def _add_invisible_rows(two_dimensional_list: list[list[str]]) -> None:
    'Adds two invisible rows to two-dimensional array.'
    for col in two_dimensional_list:
        col.insert(0, '   ')
        col.insert(0, '   ')

if __name__ == '__main__':
    ColumnsGame().run()
