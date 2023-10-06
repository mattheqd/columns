class GameState:
    def __init__(self, board: list[list[str]]):
        self._board = board

    def return_board(self) -> list[list[str]]:
        'Returns the current game board'
        return self._board

    def create_faller(self, specifications: str) -> tuple[int, list[str]]:
        'Creates a faller based on a string of text as a tuple containing the column as an int and contents of the faller as a list'
        column = int(specifications[2]) - 1
        faller = specifications[4:].split()
        for i in range(len(faller)):
            faller[i] = '[' + faller[i] + ']'
        return (column, faller)

    def put_faller_in_board(self, faller: tuple[int, list[str]]):
        'Places a faller into the game board. If the faller should immediately land, it does'
        column = faller[0]
        content = faller[1]
        for i in range(len(content)):
            self.return_board()[column][i] = content[i]
        if self._should_land(self.return_board()[column]):
            self._land()

    def faller_pass_time(self, column: int, left_off: int):
        'Handles the passage of time of a faller as it drops into the game board until freezing. If the faller should land, it does'
        if self.faller_in_landed():
            self._freeze()
            return
        self._board[column] = self._shift_column_down_from_index(self.return_board()[column], left_off)
        if self._should_land(self.return_board()[column]):
            self._land()

    def faller_move_delta(self, column: int, delta: int) -> int:
        '''
        Moves a faller in delta direction, with +1 representing right and -1 representing to left.
        If the faller should land , it lands. If movement causes the faller to unland, it unlands
        Returns the column that the faller is in after movement
        '''
        if self._can_move_faller_delta(delta):
            column += delta
        self._move_faller_delta(delta)
        if self._should_land(self.return_board()[column]):
            self._land()
        else:
            self._unland()
        return column

    def faller_reverse(self, column: int, left_off: int):
        'Reverses a faller'
        temp = self.return_board()[column][left_off-1]
        self.return_board()[column][left_off-1] = self.return_board()[column][left_off-2]
        self.return_board()[column][left_off-2] = self.return_board()[column][left_off-3]
        self.return_board()[column][left_off-3] = temp

    def check_if_dead(self) -> bool:
        'Checks if it should be GAME OVER at a frozen state'
        for col in self.return_board():
            if col[0] == '   ' and col[1] == '   ':
                pass
            else:
                return True
        return False


    def faller_in_landed(self) -> bool:
        'Determines if a faller is in landed position'
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith('|'):
                    return True
        return False

    def faller_in_frozen(self) -> bool:
        'Determines if a faller is in frozen position'
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith(' '):
                    pass
                else:
                    return False
        return True

    def faller_in_matching(self) -> bool:
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith('*'):
                    return True
        return False

    def single_match(self) -> list[tuple[int,int]]:
        'Determines the index positions of all jewels matching sequence'
        positions = []
        for col in range(self._board_columns()):
            for row in range(self._board_rows()):
                if self._matching_sequence_begins_at(col, row) and (col,row) not in positions:
                    coldelta = self._matching_sequence_begins_at(col, row)[1]
                    rowdelta = self._matching_sequence_begins_at(col, row)[2]
                    temp_positions = self._get_positions_to_be_removed(col, row, coldelta, rowdelta)
                    temp_positions.insert(0,(col,row))
                    positions.extend(temp_positions)
        positions = self._remove_duplciates_in_positions(positions)
        positions.sort(key = lambda x: x[1])
        return positions

    def remove_match(self, positions) -> None:
        'Removes index positions in a list from the game board'
        for position in positions:
            self._board[position[0]] = self._shift_column_down_from_index(self._board[position[0]], position[1])

    def add_signal(self, positions) -> None:
        'Adds the matching to signal to specified positions contained within a list'
        for position in positions:
            self.return_board()[position[0]][position[1]] = '*' + self.return_board()[position[0]][position[1]][1] + '*'

    def _still_matches(self) -> bool:
        'Determines if there are still possible matches left on the board'
        for col in range(self._board_columns()):
            for row in range(self._board_rows()):
                if self._matching_sequence_begins_at(col, row):
                    return True
        return False

    def shift_down_all_empties(self):
        'Shifts down all empty positions in the game board'
        for col in range(self._board_columns()):
            self._board[col] = self._shift_down_empties(self._board[col])   

    def column_is_full(self, column: int) -> bool:
        'Determines if a column is full of frozen pieces'
        for i in range(2, len(self._board[column])):
            if self._board[column][i] == '   ':
                return False
        return True

    def _shift_column_down_from_index(self, col: list[str], index: int) -> list[str]:
        'shifts down a column based on a particular index.'
        shifted = []
        for i in range(len(col)):
            if i != index:
                shifted.append(col[i])
        while len(shifted) != len(col):
            shifted.insert(0,'   ')
        return shifted    

    def _should_land(self, column: list[str]) -> bool:
        'Determines if a faller should land'
        if '   ' not in column:
            return True
        for i in range(1, len(column)):
            if column[i] == '   ':
                for j in range(i, -1, -1):
                    if column[j] != '   ':
                        return False
        return True

    def _can_move_faller_delta(self, delta: int) -> bool:
        'Determines if a faller can move in a direction indicated by delta, with 1 representing right and -1 representing left'
        can_move_delta = True
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith('[') or self._board[col][row].startswith('|'):
                    if self._is_valid_column_number(col+delta) and self._board[col+delta][row] == '   ':
                        pass
                    else:
                        can_move_delta = False
                        break
        return can_move_delta

    def _move_faller_delta(self, delta: int) -> list[list[str]]:
        'Moves a faller in delta direction, with 1 representing right and -1 representing left'
        moved = False
        if self._can_move_faller_delta(delta):
            for col in range(len(self._board)):
                for row in range(len(self._board[col])):
                    if self._board[col][row].startswith('[') or self._board[col][row].startswith('|'):
                        self._board[col+delta][row] = self._board[col][row]
                        self._board[col][row] = '   '
                        moved = True
                if moved == True:
                    break
                    
    def _land(self):
        'lands a faller'
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith('['):
                    self._board[col][row] = '|' + self._board[col][row][1] + '|'
    
    def _unland(self):
        'unlands a faller'
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith('|'):
                    self._board[col][row] = '[' + self._board[col][row][1] + ']'

    def _freeze(self):
        'freezes a faller'
        for col in range(len(self._board)):
            for row in range(len(self._board[col])):
                if self._board[col][row].startswith('|'):
                    self._board[col][row] = ' ' + self._board[col][row][1] + ' '

    def _create_duplicate_board(self) -> list[list[str]]:
        'returns a duplicate of the current game board'
        duplicate_board = []
        for col in range(len(self._board)):
            duplicate_board.append([])
            for row in range(len(self._board[col])):
                duplicate_board[col].append(self._board[col][row])
        return duplicate_board

    def _get_positions_to_be_removed(self, col: int, row: int, coldelta: int, rowdelta: int) -> list[tuple[int, int]]:
        'Determines what positions should be removed in a game board after matching occurs'
        positions = []
        for i in range(1, max(self._board_columns(), self._board_rows())):
            if not self._is_valid_column_number(col + coldelta * i) \
                    or not self._is_valid_row_number(row + rowdelta * i) \
                    or self._board[col + coldelta *i][row + rowdelta * i] != self._board[col][row]:
                break
            else:
                positions.append((col + coldelta * i, row + rowdelta * i))
        return positions

    def _shift_down_empties(self, col: list[str]) -> list[str]:
        'shifts down the empty spaces in a column'
        shifted = []
        for char in col:
            if char != '   ':
                shifted.append(char)
        while len(shifted) != len(col):
            shifted.insert(0,'   ')
        return shifted

    def _matching_sequence_begins_at(self, col: int, row: int) -> tuple[bool, int, int]:
        'Returns the result of possible matches in all directions'
        return self._three_or_more_in_a_row(col, row, 0, 1) \
                or self._three_or_more_in_a_row(col, row, 1, 1) \
                or self._three_or_more_in_a_row(col, row, 1, 0) \
                or self._three_or_more_in_a_row(col, row, 1, -1) \
                or self._three_or_more_in_a_row(col, row, 0, -1) \
                or self._three_or_more_in_a_row(col, row, -1, -1) \
                or self._three_or_more_in_a_row(col, row, -1, 0) \
                or self._three_or_more_in_a_row(col, row, -1, 1)

    def _three_or_more_in_a_row(self, col: int, row: int, coldelta: int, rowdelta: int) -> tuple[bool, int, int]:
        'Determines if there is a matching sequence in the current game board, and returns the direction in which the match occurs'
        start_cell = self._board[col][row]

        if start_cell == '   ':
            return False
        else:
            for i in range(1, 3):
                if not self._is_valid_column_number(col + coldelta * i) \
                        or not self._is_valid_row_number(row + rowdelta * i) \
                        or self._board[col + coldelta *i][row + rowdelta * i] != start_cell:
                    return False
            return (True, coldelta, rowdelta)

    def _remove_duplciates_in_positions(self, positions: list) -> list:
        'Removes all duplicates in a list'
        duplicates_removed = []
        for position in positions:
            if position not in duplicates_removed:
                duplicates_removed.append(position)
        return duplicates_removed

    def _board_columns(self) -> int:
        'Returns the number of columns on the given game board'
        return len(self._board)

    def _board_rows(self) -> int:
        'Returns the number of rows on the given game board'
        return len(self._board[0])

    def _is_valid_column_number(self, column_number: int) -> bool:
        'Returns True if the given column number is valid; returns False otherwise'
        return 0 <= column_number < self._board_columns()

    def _is_valid_row_number(self, row_number: int) -> bool:
        'Returns True if the given row number is valid; returns False otherwise'
        return 0 <= row_number < self._board_rows()

