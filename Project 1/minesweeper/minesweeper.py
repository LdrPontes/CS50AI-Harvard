import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()

        if(len(self.cells) == self.count):
            mines = self.cells.copy()

        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()

        if(self.count == 0):
            safes = self.cells.copy()

        return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if(cell not in self.cells):
            return

        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if(cell not in self.cells):
            return

        self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1
        self.moves_made.add(cell)

        # 2
        self.mark_safe(cell)

        # 3
        cell_neighbors = self.neighbors(cell)

        cell_neighbors -= self.safes
        cell_neighbors -= self.mines
        cell_neighbors -= self.moves_made


        new_sentence = Sentence(cell_neighbors, count)
        self.knowledge.append(new_sentence)

        # 4
        tmp_mines = set()
        tmp_safes = set()

        for sentence in self.knowledge:
            if(len(sentence.cells) == 0):
                self.knowledge.remove(sentence)
            else:
                new_safes = sentence.known_safes()
                new_mines = sentence.known_mines()
                
                if(len(new_safes) != 0):
                    tmp_safes.update(new_safes)

                if(len(new_mines) != 0):
                    tmp_mines.update(new_mines)
      
        for safe in tmp_safes:
            if(safe not in self.safes and safe not in self.mines and safe not in self.moves_made):
                self.mark_safe(safe)

        for mine in tmp_mines:
            if(mine not in self.mines and mine not in self.moves_made and mine not in self.safes):
                self.mark_mine(mine)

        # 5
        inferences = []

        for set1 in self.knowledge:
            if(len(set1.cells) == 0):
                self.knowledge.remove(set1)
            elif(set1 == new_sentence):
                break;
            elif(new_sentence.cells <= set1.cells):
                new_set = set1.cells - new_sentence.cells
                inferences.append(Sentence(new_set, set1.count - new_sentence.count))

                
        self.knowledge += inferences

    def neighbors(self, cell):
        """
        Returns the set (i, j) of neighbors from a cell
        """
        neighbors_cells = set()

        for i in range(cell[0] - 1, cell[0] + 2):

            for j in range(cell[1] - 1, cell[1] + 2):

                if(self.in_bounds(i, j) and (i, j) != cell):
                    neighbors_cell = (i, j)
                    if(neighbors_cell not in self.moves_made):
                        neighbors_cells.add(neighbors_cell)

        return neighbors_cells

    def in_bounds(self, row, column):
        """
        Returns True if (row, column) is in bounds of board. Returns False instead of.
        """
        if row < 0 or column < 0:
            return False

        if row > self.height - 1 or column > self.width - 1:
            return False

        return True

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe_move in self.safes:
            if(safe_move not in self.moves_made):
                print('Safe Move:', safe_move)
                return safe_move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        random_move = self.generate_random_position()

        if(random_move not in self.mines):
            print('Random Move:', random_move)
            return random_move
        
        return None

    def generate_random_position(self):
        """
        Returns a generated random position in the board 
        """

        row = random.randint(0, self.height - 1)
        column = random.randint(0, self.width - 1)

        move = (row, column)

        return move
