"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2016 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
import os
from random import randint
import math


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    @type data_size: int
        The total size of all leaves of this tree.
    @type colour: (int, int, int)
        The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    @type _root: obj | None
        The root value of this tree, or None if this tree is empty.
    @type _subtrees: list[AbstractTree]
        The subtrees of this tree.
    @type _parent_tree: AbstractTree | None
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    def __init__(self, root, subtrees, data_size=0):
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this tree's
        data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.

        @type self: AbstractTree
        @type root: object
        @type subtrees: list[AbstractTree]
        @type data_size: int
        @rtype: None

        >>> a1 = AbstractTree('f1', [], 10)
        >>> a2 = AbstractTree('f2', [], 10)
        >>> a3 = AbstractTree('f3', [a1, a2], 0)
        >>> len(a3._subtrees)== 2
        True
        >>> a3.data_size == 20
        True
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        # Initialize self.colour.
        if len(self._subtrees) == 0:
            (c1, c2, c3) = (randint(0, 255), randint(0, 255), randint(0, 255))
            self.color = (c1, c2, c3)

        # Initialize self.data_size and set all _parent_tree attributes in self._subtrees.
        if len(self._subtrees) == 0:
            self.data_size = data_size
        else:  # len(self._subtrees) != 0
            self.data_size = 0
            for subtree in self._subtrees:
                self.data_size += subtree.data_size
                subtree._parent_tree = self

    def is_empty(self):
        """Return True if this tree is empty.

        @type self: AbstractTree
        @rtype: bool
        """
        return self._root is None

    def treename(self):
        """Return the root of the tree.

        @type self: AbstractTree
        @rtype: object
        """
        return self._root

    def subtrees(self):
        """Return the subtrees of the tree.

        @type self: AbstractTree
        @rtype: list[AbstractTree]
        """
        return self._subtrees

    def get_parent(self):
        """Return the parent tree of the tree.

        @type self: AbstractTree
        @rtype: AbstractTree
        """
        return self._parent_tree

    def generate_treemap(self, rect):
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]

        >>> f1 = AbstractTree('f2', [], 0)
        >>> f1.generate_treemap((0, 0, 100, 200))
        []
        """
        if self.data_size == 0:  # if the tree has size 0
            return []
        else:
            x, y, width, height = rect  # extract coordinates of a rectangle
            if len(self._subtrees) == 0:  # if the tree has a single leaf
                return [((x, y, width, height), self.color)]
            else:
                new = []
                curr_w = x
                curr_h = y
                sub_curr = 0  # set to use for the last rectangle
                for i in range(0, len(self._subtrees)):
                    proportion = self._subtrees[i].data_size / self.data_size
                    if width > height:
                        if i != len(self._subtrees) - 1:  # if it is not the last rectangle
                            subwidth = int(proportion * width)
                            sub_curr += subwidth
                        else:  # if it is the last rectangle
                            subwidth = int(width - sub_curr)
                        new_rect = self._subtrees[i].generate_treemap((curr_w, y, subwidth, height))
                        new.extend(new_rect)
                        curr_w += subwidth
                    else:  # width <= height
                        if i != len(self._subtrees) - 1:  # if it is not the last rectangle
                            subheight = int(proportion * height)
                            sub_curr += subheight
                        else:  # if it is the last rectangle
                            subheight = int(height - sub_curr)
                        new_rect = self._subtrees[i].generate_treemap((x, curr_h, width, subheight))
                        new.extend(new_rect)
                        curr_h += subheight
                return new

    def round_up(self, number):
        """Round up the number.

        @type self: AbstractTree
        @type number: int
        @rtype: int
        """
        return math.ceil(number)

    def get_coordinates(self, coor):
        """Return a rectangle range according to the given coordiante.

        @type self: AbstractTree
        @type coor: (int, int, int, int)
        @rtype: ((int, int), (int, int))

        >>> f1 = AbstractTree('f2', [], 0)
        >>> f1.get_coordinates((50, 0, 75, 100))
        ((50, 125), (0, 100))
        """
        x, y, width, height = coor
        new_x = (x, x + width)  # the range of x-axis cordinates of a rectangle
        new_y = (y, y + height)  # the range of y-axis cordinates of a rectangle
        return new_x, new_y

    def update_datasize(self, num, s):
        """Traversing up the tree if its data size adds or reduces a number
        according to the demand s. When s is equal to 0, the number is added,
        and when s is equal to 1, the number is reduced.

        @type self: AbstractTree
        @type num: int
        @type s: int
        @rtype: None

        >>> a1 = AbstractTree('f1', [], 10)
        >>> a2 = AbstractTree('f2', [], 10)
        >>> a3 = AbstractTree('F1', [a1, a2], 0)
        >>> a4 = AbstractTree('F2', [a3], 0)
        >>> a1.update_datasize(5, 0)
        >>> a4.data_size
        25
        >>> a3.data_size
        25
        """
        stored = [self._parent_tree]  # use to store the parent tree
        while stored[0] is not None:
            if s == 0:
                stored[0].data_size += num
                stored[0] = stored[0].get_parent()
            elif s == 1:
                stored[0].data_size -= num
                stored[0] = stored[0].get_parent()

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.

        @type self: AbstractTree
        @rtype: str
        """
        raise NotImplementedError


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """
    def __init__(self, path):
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.

        @type self: FileSystemTree
        @type path: str
        @rtype: None

        >>> path1 = '/h/u10/c5/00/mengyifa/Desktop/csc148/assignments/a2/example/B/A/f1.txt'
        >>> tree1 = FileSystemTree(path1)
        >>> tree1.treename()  == 'f1.txt'
        True
        >>> tree1.data_size  == 15
        True
        >>> len(tree1.subtrees()) == 0
        True
        >>> path2 = '/h/u10/c5/00/mengyifa/Desktop/csc148/assignments/a2/example/B'
        >>> tree2 = FileSystemTree(path2)
        >>> tree2.data_size  == 40
        True
        >>> tree2.treename() == 'B'
        True
        >>> tree2.get_parent() is None
        True
        >>> len(tree2.subtrees()) == 2
        True
        >>> tree2.subtrees()[1].treename()
        'A'
        >>> tree1.generate_treemap((0, 0, 100, 200))
        [(0, 0, 100, 200), ()]
        >>> tree2.generate_treemap((0, 0, 200, 100))
        [((0, 0, 50, 100), ()), ((50, 0, 75, 100), ()), ((125, 0, 25, 100), ()), ((150, 0, 50, 100), ())]
        >>> tree2.generate_treemap((0, 0, 200, 200))
        [((0, 0, 200, 50), ()), ((0, 50, 66, 150), ()), ((66, 50, 100, 150), ()), ((166, 50, 34, 150), ())]
        """
        root = os.path.basename(path)
        subtrees = []
        if not os.path.isdir(path):  # when it is a regular file
            data_size = os.path.getsize(path)
            AbstractTree.__init__(self, root, subtrees, data_size)
        else:  # when it is a folder
            for filename in os.listdir(path):
                subtree_path = os.path.join(path, filename)
                f = FileSystemTree(subtree_path)
                subtrees.append(f)
            AbstractTree.__init__(self, root, subtrees, data_size=0)

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        @type self: FileSystemTree
        @rtype: str
        """
        return "/"

if __name__ == '__main__':
    import python_ta
    # Remember to change this to check_all when cleaning up your code.
    python_ta.check_errors(config='pylintrc.txt')
