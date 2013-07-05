# 2013

import sys


class Cell():

    INVALID_VALUE = -1  # per http://stackoverflow.com/a/2682752

    def __init__(self, value):
        if value != '-':
            self._value = int(value)
        else:
            self._value = self.INVALID_VALUE

        self._possibilities = [num for num in range(1, 10)]


    def __str__(self):
        if self._value != self.INVALID_VALUE:
            return str(self.val())
        else:
            return ' '


    def val(self, new_value=None):
        if new_value is None:  # get
            return self._value
        else:  # set
            self._value = new_value
            return self  # enable method chaining    

    def possibilities(self):
        return self._possibilities

    
    def remove_possibility(self, possibility):
        assert possibility in self.possibilities(), ('Cannot remove %s from %s for cell %s' %
            (possibility, self.possibilities(), self))

        # print 'removing possibility %s...' % possibility
        self._possibilities.remove(possibility)

        if len(self.possibilities()) == 0:
            if self.val() == self.INVALID_VALUE:
                raise Exception('The last possibility %s was just removed from cell %s' % (possibility, self))

        if len(self.possibilities()) == 1:
            last_man_standing = self.possibilities()[0]
            if self.val() == self.INVALID_VALUE:
                print 'Was able to fill in a %s!' % last_man_standing
                self._possibilities.remove(last_man_standing)
                self.val(last_man_standing)
            else:
                pass # it's okay the first time around
                # raise Exception('Cannot overwrite cell of value %s with new value %s for cell %s' %
                #     (self.val(), last_man_standing, self))

        return self  # enable method chaining


class Puzzle():

    def __init__(self, filename):
        self.filename = filename
        self.puzzle = []
        self.load()


    def load(self):
        for line in open(self.filename).read().splitlines():  # per http://stackoverflow.com/a/544932
            self.puzzle.append([Cell(value) for value in line.split(' ')])


    def print_puzzle(self):
        self._print_array(self.puzzle)


    def _print_array(self, array):
        for i in range(len(array)):
            print ' '.join([str(cell) for cell in array[i]])


    def _subarray(self, array, i=None, j=None):
        assert 0 <= i <= 8 or i is None, 'i must be None or between 0 and 8 (i: %s; j: %s)' % (i, j)
        assert 0 <= j <= 8 or j is None, 'j must be None or between 0 and 8 (i: %s; j: %s)' % (i, j)

        if i is not None and j is not None:
            return array[i][j]
        elif i is not None:
            return array[i]
        elif j is not None:
            raise Exception('i must be passed in if j is passed in (i: %s; j: %s)' % (i, j))
        else:
            return array


    def rows(self, row_index=None, col_index=None):
        """
            row_index corresponds to:
            0
            --------------
            1
            --------------
            2
            --------------
            ...
        """

        rows = self.puzzle  # already in the correct form
        return self._subarray(rows, row_index, col_index)


    def cols(self, col_index=None, row_index=None):
        """
            col_index corresponds to:
            0  |  1  |  2  |  ...
               |     |     |
               |     |     |
               |     |     |
               |     |     |
        """

        cols = zip(*self.puzzle)  # transpose, per http://stackoverflow.com/a/4937526
        return self._subarray(cols, col_index, row_index)


    def boxes(self, box_index=None, box_item_index=None):
        """
            box_index corresponds to:
            0  |  1  |  2
            ---+-----+----
            3  |  4  |  5
            ---+-----+----
            6  |  7  |  8
        """

        row_ranges = [range(0, 3), range(3, 6), range(6, 9)]
        col_ranges = row_ranges
        boxes = []
        x = 0
        for row_range in row_ranges:
            for col_range in col_ranges:
                boxes.append([])
                for r in row_range:
                    for c in col_range:
                        boxes[x].append(self.puzzle[r][c])
                x += 1
        return self._subarray(boxes, box_index, box_item_index)


    def box_index(self, row_index, col_index):
        return (row_index // 3) * 3 + (col_index // 3) # integer (floor) division


    def prune_possibilities(self):
        for r in range(len(self.puzzle)):
            for c in range(len(self.puzzle[r])):
                b = self.box_index(r, c)
                cell = self.puzzle[r][c]

                for possibility in cell.possibilities():
                    if (possibility in [row_cell.val() for row_cell in self.rows(r)] or
                        possibility in [col_cell.val() for col_cell in self.cols(c)] or
                        possibility in [box_cell.val() for box_cell in self.boxes(b)]
                        ):
                        cell.remove_possibility(possibility)
                        return True

        return False # can prune no more


    def is_solved(self):
        return self.filled_in() and self.valid_vals()


    def filled_in(self):
        for i in range(len(self.rows())):
            for j in range(len(self.cols())):
                if self.puzzle[i][j].val() == Cell.INVALID_VALUE:
                    return False
        return True


    def valid_vals(self):
        for row in self.rows():
            if not self._one_through_nine(row):
                return False
                # raise Exception('Solution contains number other than 1-9! Row:\n%s\n' % row)
            dupes = self._num_duplicates(row)
            if dupes > 0:
                raise Exception('Solution contains %s duplicates in row!\n%s\n!' +
                    'Either the solver has a bug orow the puzzle cannot be solved.' % (dupes, row))
        for col in self.cols():
            if not self._one_through_nine(col):
                return False
                # raise Exception('Solution contains number other than 1-9! Column:\n%s\n' % col)
            dupes = self._num_duplicates(col)
            if dupes > 0:
                raise Exception('Solution contains %s duplicates in column\n%s\n' +
                    'Either the solver has a bug or the puzzle cannot be solved.' % (dupes, col))
        for box in self.boxes():
            if not self._one_through_nine(box):
                return False
                # raise Exception('Solution contains number other than 1-9! Box:\n%s\n' % box)
            dupes = self._num_duplicates(box)
            if dupes > 0:
                raise Exception('Solution contains %s duplicates in box\n%s\n' +
                    'Either the solver has a bug or the puzzle cannot be solved.' % (dupes, box))
        return True


    def _num_duplicates(self, array):
        # per http://stackoverflow.com/a/1541827
        return len(array) - len(set(array))


    def _one_through_nine(self, array):
        ideal_array = [i for i in range(1, 10)]
        array_as_vals = [cell.val() for cell in array]
        return set(array_as_vals) == set(ideal_array)


class Solver():

    def __init__(self, filename):
        pass


    def run(self):
        self.solve()


    def solve(self):
        print 'Loading puzzle...'
        self.puzzle = Puzzle(filename)
        self.puzzle.print_puzzle()

        print 'Solving...'
        while True:
            prunable = self.puzzle.prune_possibilities()
            solved = self.puzzle.is_solved()
            if solved or not prunable:
                break
        
        print '----'
        self.puzzle.is_solved()

        if solved:
            print 'Solved puzzle!'
        else: # not prunable
            print 'This puzzle is too difficult!'

        self.puzzle.print_puzzle()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: ' + __file__ + ' [puzzle file path]'
        sys.exit(0)

    filename = sys.argv[1]

    Solver(filename).run()
