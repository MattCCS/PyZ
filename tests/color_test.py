import curses

def main():
    stdscr = curses.initscr()   # MANDATORY!
    curses.start_color()        # MANDATORY!
    curses.use_default_colors() # optional.

    stdscr.addstr("can_change_color(): " + str(curses.can_change_color()) + '\n')
    stdscr.addstr("COLOR_PAIRS: " + str(curses.COLOR_PAIRS) + '\n\n')

    ####################################

    stdscr.addstr("color 67 before:\n")
    curses.init_pair(20, 67, 0)
    stdscr.addstr(str(curses.color_content(67)) + '\n', curses.color_pair(20))

    stdscr.addstr("color 67 after:\n")
    curses.init_color(67, 0, 255, 0)
    curses.init_pair(21, 67, 0)
    stdscr.addstr(str(curses.color_content(67)) + '\n\n', curses.color_pair(21))

    ####################################

    stdscr.addstr("color 101 before:\n")
    curses.init_pair(22, 101, 0)
    stdscr.addstr(str(curses.color_content(101)) + '\n', curses.color_pair(22))

    stdscr.addstr("color 101 after:\n")
    curses.init_color(101, 128, 128, 128)
    curses.init_pair(23, 101, 0)
    stdscr.addstr(str(curses.color_content(101)) + '\n\n', curses.color_pair(23))

    ####################################

    stdscr.addstr("pair 40 before:\n")
    stdscr.addstr(str(curses.pair_content(40)) + '\n', curses.color_pair(40))

    stdscr.addstr("pair 40 after:\n")
    curses.init_pair(40, 101, 67)
    stdscr.addstr(str(curses.pair_content(40)) + '\n\n', curses.color_pair(40))

    stdscr.getch()

    curses.endwin()     # optional, but recommended.

main()
