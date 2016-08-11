
import os
os.environ['ESCDELAY'] = '25'
import curses
import locale
locale.setlocale(locale.LC_ALL, "")
CODE = locale.getpreferredencoding()

####################################
# setup
def setup(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(1)) # set background color to WHITE ON BLACK
