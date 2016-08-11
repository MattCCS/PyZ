"""
"""

# custom
from pyz import layers
from pyz import colors
from pyz import control
from pyz.terminal_size import true_terminal_size

####################################

class QuitWindow(control.Controller):

    def __init__(self, controlmanager):
        control.Controller.__init__(self, controlmanager)

        self.layer = layers.LayerManager("quit_window", (13, 3))
    
    def interact(self, key):
        if key in map(ord, 'yY'):
            raise KeyboardInterrupt()
        elif key == 27 or key in map(ord, 'nN'): # ESC or n/N
            layers.delete("quit_window")
            return True # we die.
        else:
            return False # ignore everything else.

    def render(self, stdscr):
        WHITE = colors.get("white")
        RED   = colors.get("red")

        (X,Y) = true_terminal_size() # <---- TODO:  ok?

        layers.add_border(self.layer, color=WHITE)
        self.layer.setrange(0, 0, "<quit_main>", color=WHITE)
        self.layer.setrange(1, 1, "Quit? (Y/N)", color=RED)
        layers.render_to(self.layer, stdscr, int(X//2.7), int(Y//2.7))
