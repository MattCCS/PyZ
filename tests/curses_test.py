import curses

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()

    for bg in range(256):
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, bg)
        try:
            for i in range(256):
                # c = str(i)
                c = curses.ACS_ULCORNER
                c = ord('a')
                c = u'\u239e'
                c = u'\u2588'
                # c = 9608
                # c = u'\u239e'.encode("utf-8")
                # c = u'\u0438'.encode('utf-8')
                stdscr.addstr(c, curses.color_pair(i))
                # stdscr.addch(9118)
                # stdscr.addstr('\\u239e')
                # stdscr.addch(c)
                if i < 16:
                    stdscr.addstr(' ', curses.color_pair(i))
                if i in (16,52,88,124,160,196,232,):
                    stdscr.addstr('\n', curses.color_pair(i))
            stdscr.addstr('\n', curses.color_pair(i))
        except curses.error:
            # End of screen reached
            pass
        if stdscr.getch() == ord('q'):
            break
        stdscr.clear()

curses.wrapper(main)
