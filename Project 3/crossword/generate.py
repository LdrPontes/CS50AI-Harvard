import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for v in self.crossword.variables:
            copy = self.domains[v].copy()

            for i in copy:
                if(v.length != len(i)):
                    self.domains[v].remove(i)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        copy = self.domains[x].copy()
 
        for word in copy:
            overlap = self.crossword.overlaps[x, y]
            must_remove = True

            if(overlap != None):
                for s in self.domains[y]:
                    if(word[overlap[0]] == s[overlap[1]]):
                        must_remove = False

                if(must_remove):
                    self.domains[x].remove(word)
                    revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if(arcs == None):
            queue = []
            for i in self.crossword.overlaps:
                queue.append(i)
        else:
            queue = arcs

        while len(queue) > 0:
            (x, y) = queue.pop(0)
            if(self.revise(x, y)):
                if(len(self.domains[x]) == 0):
                    return False
                for z in self.crossword.neighbors(x):
                    if(x != y):
                        queue.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        #All values are distinct
        if(len(assignment.values()) != len(set(assignment.values()))):
            return False

        #Every value is the correct length
        for variable in assignment.keys():
            if(variable.length != len(assignment[variable])):
                return False

        #there are no conflicts between neighboring variables.
        for variable in assignment.keys():
            neighbors = self.crossword.neighbors(variable)
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[variable, neighbor]

                if(neighbor in assignment.keys() and assignment[variable][overlap[0]] != assignment[neighbor][overlap[1]]):
                    return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = list()

        for word in self.domains[var]:
            count = 0

            for neighbor in (self.crossword.neighbors(var) - set(assignment.keys())):
                overlap = self.crossword.overlaps[var, neighbor]
                count += len(set(filter(lambda x:x[overlap[1]] != word[overlap[0]], self.domains[neighbor])))

            values.append((word, count))

        values.sort(key=lambda value: value[1])

        domain_values = list()

        for value in values:
            domain_values.append(value[0])

        return domain_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        assigned_variables = set(assignment.keys())
        all_variables = self.crossword.variables.copy()
        unassigned_variables = all_variables.difference(assigned_variables)

        variable = list(unassigned_variables)[0]

        for i in unassigned_variables:
            if(len(self.domains[variable]) < len(self.domains[i])):
                variable = i

            if(len(self.domains[variable]) == len(self.domains[i]) and len(self.crossword.neighbors(variable)) <= len(self.crossword.neighbors(i))):
                variable = i

        return variable


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if(self.assignment_complete(assignment)):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if(self.consistent(new_assignment)):  
                
                self.inference(var, new_assignment)

                result = self.backtrack(new_assignment)

                if(result != None):
                    return result

        return None

    def inference(self, var, assignment):
        arcs = list()
        
        domain_backup = dict()

        for neighbor in self.crossword.neighbors(var):
            if(neighbor not in assignment.keys()):
                domain_backup[neighbor] = self.domains[neighbor].copy()
                arcs.append((neighbor, var))

        result = self.ac3(arcs=arcs)

        if(not result):
            for neighbor in domain_backup.keys():
                self.domains[neighbor] = domain_backup[neighbor]


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
