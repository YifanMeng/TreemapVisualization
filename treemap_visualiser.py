"""Assignment 2: Treemap Visualiser

=== CSC148 Fall 2016 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the code to run the treemap visualisation program.
It is responsible for initializing an instance of AbstractTree (using a
concrete subclass, of course), rendering it to the user using pygame,
and detecting user events like mouse clicks and key presses and responding
to them.
"""
import pygame
from tree_data import FileSystemTree
from population import PopulationTree


# Screen dimensions and coordinates
ORIGIN = (0, 0)
WIDTH = 1024
HEIGHT = 768
FONT_HEIGHT = 30                       # The height of the text display.
TREEMAP_HEIGHT = HEIGHT - FONT_HEIGHT  # The height of the treemap display.

# Font to use for the treemap program.
FONT_FAMILY = 'Consolas'


def run_visualisation(tree):
    """Display an interactive graphical display of the given tree's treemap.

    @type tree: AbstractTree
    @rtype: None
    """
    # Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render the initial display of the static treemap.
    render_display(screen, tree, '')

    # Start an event loop to respond to events.
    event_loop(screen, tree)


def render_display(screen, tree, text):
    """Render a treemap and text display to the given screen.

    Use the constants TREEMAP_HEIGHT and FONT_HEIGHT to divide the
    screen vertically into the treemap and text comments.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @type text: str
        The text to render.
    @rtype: None
    """
    # First, clear the screen
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, 0, WIDTH, HEIGHT))

    # The treemap display
    treemap = tree.generate_treemap((0, 0, WIDTH, TREEMAP_HEIGHT))
    if len(treemap) == 0:  # B.C: if the tree is empty
        pygame.draw.rect(screen, pygame.color.THECOLORS['black'], (0, 0, WIDTH, TREEMAP_HEIGHT))
    else:
        for t in treemap:
            rec, col = t  # extract coordinates of a rectangle and its color
            pygame.draw.rect(screen, col, rec)

    # The text display
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'], (0, TREEMAP_HEIGHT, WIDTH, FONT_HEIGHT))
    _render_text(screen, text)

    # This must be called *after* all other pygame functions have run.
    pygame.display.flip()


def _render_text(screen, text):
    """Render text at the bottom of the display.

    @type screen: pygame.Surface
    @type text: str
    @rtype: None
    """
    # The font we want to use
    font = pygame.font.SysFont(FONT_FAMILY, FONT_HEIGHT - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])

    # Where to render the text_surface
    text_pos = (0, HEIGHT - FONT_HEIGHT + 4)
    screen.blit(text_surface, text_pos)


def event_loop(screen, tree):
    """Respond to events (mouse clicks, key presses) and update the display.

    Note that the event loop is an *infinite loop*: it continually waits for
    the next event, determines the event's type, and then updates the state
    of the visualisation or the tree itself, updating the display if necessary.
    This loop ends when the user closes the window.

    @type screen: pygame.Surface
    @type tree: AbstractTree
    @rtype: None
    """
    clicked = False  # to store the clicked times
    selected = None  # to store the selected leaf
    text = ''  # to initiate the text
    while True:
        # Wait for an event
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            return
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos
            txt = tree.treename()
            selected_leaf, text = selected_leaf_and_its_path(tree, x, y, txt)
            if event.button == 1:
                if selected_leaf is None:
                    pass
                elif clicked is False:
                    selected = selected_leaf
                    clicked = True
                    textline = text + " ({})".format(selected_leaf.data_size)
                    render_display(screen, tree, textline)
                elif clicked is True:
                    if selected == selected_leaf:
                        clicked = False
                        textline = ''
                    else:
                        selected = selected_leaf
                        textline = text + " ({})".format(selected_leaf.data_size)
                    render_display(screen, tree, textline)
            elif event.button == 3:
                selected_leaf.update_datasize(selected_leaf.data_size, 1)
                selected_leaf.data_size = 0
                selected_leaf.get_parent().subtrees().remove(selected_leaf)
                render_display(screen, tree, '')
        elif event.type == pygame.KEYUP:
            if clicked is True:
                n = 0.01 * selected.data_size
                round_n = selected.round_up(n)
                if event.key == pygame.K_UP:
                    selected.data_size += round_n
                    selected.update_datasize(round_n, 0)
                elif event.key == pygame.K_DOWN:
                    selected.data_size -= round_n
                    if selected.data_size <= 1:
                        selected.data_size = 1
                    selected.update_datasize(round_n, 1)
                textline = text + " ({})".format(selected.data_size)
                render_display(screen, tree, textline)


def selected_leaf_and_its_path(tree, x, y, txt):
    """Return the selected leaf and its path string according to different tree attributes.

    @type tree: AbstractTree
    @type x: int
    @type y: int
    @type txt: object
    @rtype: (AbstractTree, str)
    """
    selected = None
    text = txt
    if tree.data_size == 0:  # if the tree has 0 data size, do nothing
        pass
    elif 0 <= x <= WIDTH and TREEMAP_HEIGHT < y <= HEIGHT:  # if the text display is selected
        text = ''
    elif len(tree.subtrees()) == 0:
        selected = tree
    elif len(tree.subtrees()) != 0:  # if the tree has subtrees, call the helper function
        treemap = (0, 0, WIDTH, TREEMAP_HEIGHT)
        selected, text = rect_to_leaf(tree, treemap, x, y, txt)
    return selected, text


def rect_to_leaf(tree, treemap, x, y, txt):
    """Return the selected leaf and its path string accoding to the mouse cursor coordinate (x, y).

    @type tree: AbstractTree
    @type treemap: (int, int, int, int)
    @type x: int
    @type y: int
    @type txt: object
    @rtype: (AbstractTree, str)
    """
    text = txt
    ori_x, ori_y, width, height = treemap
    curr_w = ori_x
    curr_h = ori_y
    sub_curr = 0  # set to use for the last rectangle
    for i in range(0, len(tree.subtrees())):  # recomputing the rectangles
        proportion = tree.subtrees()[i].data_size / tree.data_size
        if width > height:
            if i != len(tree.subtrees()) - 1:  # if it is not the last rectangle
                subwidth = int(proportion * width)
                sub_curr += subwidth
            else:  # if it is the last rectangle
                subwidth = int(width - sub_curr)
            subtreemap = (curr_w, ori_y, subwidth, height)
            rect_x, rect_y = tree.get_coordinates(subtreemap)
            if (rect_x[0] <= x < rect_x[1]) and (rect_y[0] <= y < rect_y[1]):  # locate the mouse cursor
                selected_leaf = tree.subtrees()[i]
                text += selected_leaf.get_separator() + selected_leaf.treename()
                if len(selected_leaf.subtrees()) != 0:
                    return rect_to_leaf(selected_leaf, subtreemap, x, y, text)
                else:  # if it is a leaf
                    return selected_leaf, text
            curr_w += subwidth
        elif width <= height:
            if i != len(tree.subtrees()) - 1:  # if it is not the last rectangle
                subheight = int(proportion * height)
                sub_curr += subheight
            else:  # if it is the last rectangle
                subheight = int(height - sub_curr)
            subtreemap = (ori_x, curr_h, width, subheight)
            rect_x, rect_y = tree.get_coordinates(subtreemap)
            if (rect_x[0] <= x < rect_x[1]) and (rect_y[0] <= y < rect_y[1]):  # locate the mouse cursor
                selected_leaf = tree.subtrees()[i]
                text += selected_leaf.get_separator() + selected_leaf.treename()
                if len(selected_leaf.subtrees()) != 0:
                    return rect_to_leaf(selected_leaf, subtreemap, x, y, text)
                else:  # if it is a leaf
                    return selected_leaf, text
            curr_h += subheight


def run_treemap_file_system(path):
    """Run a treemap visualisation for the given path's file structure.

    Precondition: <path> is a valid path to a file or folder.

    @type path: str
    @rtype: None
    """
    file_tree = FileSystemTree(path)
    run_visualisation(file_tree)


def run_treemap_population():
    """Run a treemap visualisation for World Bank population data.

    @rtype: None
    """
    pop_tree = PopulationTree(True)
    run_visualisation(pop_tree)


if __name__ == '__main__':
    import python_ta
    # Remember to change this to check_all when cleaning up your code.
    python_ta.check_errors(config='pylintrc.txt')

    # To check your work for Tasks 1-4, try uncommenting the following function
    # call, with the '' replaced by a path like
    # 'C:\\Users\\David\\Documents\\csc148\\assignments' (Windows) or
    # '/Users/dianeh/Documents/courses/csc148/assignments' (OSX)
    run_treemap_file_system('/Users/mengmeng/Dropbox/course/csc148/assignments/a2/example/B')

    # To check your work for Task 5, uncomment the following function call.
    # run_treemap_population()
