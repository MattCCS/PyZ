"""
"""

# standard
import traceback

# custom
from pyz import audio
from pyz import layers
from pyz import gameworld
from pyz import curses_prep

####################################

class ControlManager(object):

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.pending_controllers = []
        self.dead_controllers = set()
        self.controllers = []

    def add_controller(self, controller):
        self.pending_controllers.append(controller)

    def _interact_with_controller(self, controller, key):
        dead = controller.interact(key)
        if dead:
            self.dead_controllers.add(controller)

    def _loop(self):
        
        while True:
            # update controller stack
            self.controllers += self.pending_controllers
            self.controllers = [c for c in self.controllers if c not in self.dead_controllers]
            self.pending_controllers = []
            self.dead_controllers = set()

            if not self.controllers:
                break

            lower = self.controllers[:-1]
            top   = self.controllers[-1]
            assert top

            ####################################
            # RENDERING
            self.stdscr.erase()

            # render the lower controllers (bottom to top)
            if lower:
                layers.set_dim(True)
                for controller in lower:
                    controller.render(self.stdscr)
                layers.set_dim(False)

            # render the TOPMOST controller
            top.render(self.stdscr)

            # get input safely
            curses_prep.curses.flushinp()
            key = self.stdscr.getch() # don't do anything special for KeyboardInterrupt!

            # resizes are sent to EVERYONE!
            # otherwise, rendering suffers.
            if key == curses_prep.curses.KEY_RESIZE:
                for controller in self.controllers:
                    self._interact_with_controller(controller, key)
            else:
                self._interact_with_controller(top, key)

    def loop(self):
        """
        """

        try:
            self._loop()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            with open("BAD2.txt", 'w') as f:
                f.write(traceback.format_exc())

####################################

def mainwrapped(stdscr):
    curses_prep.setup(stdscr)
    layers.set_curses_border()
    stdscr.timeout(1000)

    stdscr.addstr(0, 0, "Starting...")
    stdscr.refresh()

    stdscr.addstr(1, 0, "Loading viewtree...")
    stdscr.refresh()

    # grid
    # stdscr.addstr(2, 0, "Creating game grid...")
    # stdscr.refresh()
    # GRID = gameworld.GridManager2D(stdscr, X, Y)

    # stdscr.addstr(3, 0, "Playing...")
    # stdscr.refresh()

    manager = ControlManager(stdscr)
    gameworld.GridManager2D(manager)
    manager.loop()

    audio.stop_all_sounds()
    curses_prep.curses.curs_set(1)
