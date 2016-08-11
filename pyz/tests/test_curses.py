
####################################

DIRECTIONAL_MAP_WSAD = {
    ord('w'): ( 0, -1),
    ord('s'): ( 0,  1),
    ord('a'): (-1,  0),
    ord('d'): ( 1,  0),
}

DIRECTIONAL_MAP_ARROW = {
    curses.KEY_UP    : ( 0, -1),
    curses.KEY_DOWN  : ( 0,  1),
    curses.KEY_LEFT  : (-1,  0),
    curses.KEY_RIGHT : ( 1,  0),
}

####################################

def layer_test():

    # cursor
    A = LayerManager("a", (1,1))
    A.set(0,0,'X', mode=curses.A_STANDOUT)

    # container for cursor
    SM = LayerManager("container", (8,8), restrict=True, sublayers=[
            (0, 0, A),
        ])

    # test 1
    L1 = LayerManager("base", (3,8), wrap=True)
    L1.setrange(2, 0, "Here is a long string that i made for you")

    # test 2
    # L2 = LayerManager("top", (5,5))
    # L2.setrange(0,1, "AAAAAAAAAAAAAAAAA")

    # sub-window with border
    LM = LayerManager("subwin", (10,10), sublayers=[
            (1, 1, L1),
            # (1, 4, L2),
            (0, 0, gen_border("border1", 10,10)),
            (1, 1, SM),
        ])

    # main screen
    MAIN = LayerManager("main", (40,24), sublayers=[(30, 6, LM)])

    return MAIN


def curses_test_wrapped(stdscr):
    curses_prep.setup(stdscr)

    MAIN = layer_test()
    SM = LayerManager.get("container")
    L1 = LayerManager.get("base")

    code = (0,0)
    sub_code = (0,0)
    size_code = (0,0)
    main_code = (0,0)

    while True:

        if any(sub_code):
            (dx, dy) = sub_code
            SM.move_layer_inc(dx, dy, "a")
            sub_code = (0,0)
        if any(code):
            (dx, dy) = code
            MAIN.move_layer_inc(dx, dy, "subwin")
            code = (0,0)
        if any(size_code):
            (dx, dy) = size_code
            L1.resize_diff(dx, dy)
            size_code = (0,0)
        if any(main_code):
            (dx, dy) = main_code
            MAIN.resize_diff(dx, dy)
            main_code = (0,0)

        for (x, y, (c, color, mode)) in list(MAIN.items()):
            try:
                stdscr.addstr(y, x*2, c, mode)
                pass
            except curses.error:
                break
        (x, y, _) = SM.get_layer("a")
        stdscr.addstr(20,0, "x/y: {}/{}".format(x, y), 1)
        (x, y, _) = MAIN.get_layer("subwin")
        stdscr.addstr(21,0, "wx/wy: {}/{}".format(x, y), 1)
        (w, h) = L1.size()
        stdscr.addstr(22,0, "w/h: {}/{}".format(w, h), 1)

        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            break

        if key in DIRECTIONAL_MAP_ARROW:
            sub_code = DIRECTIONAL_MAP_ARROW[key]

        elif key in DIRECTIONAL_MAP_WSAD:
            code = DIRECTIONAL_MAP_WSAD[key]

        elif key == ord('u'):
            size_code = (0, -1)
        elif key == ord('j'):
            size_code = (0, 1)
        elif key == ord('h'):
            size_code = (-1, 0)
        elif key == ord('k'):
            size_code = (1, 0)

        elif key == ord('['):
            main_code = (0, -1)
        elif key == ord(']'):
            main_code = (0, 1)
        elif key == ord('-'):
            main_code = (-1, 0)
        elif key == ord('='):
            main_code = (1, 0)

        stdscr.clear()


def curses_test():
    curses.wrapper(curses_test_wrapped)
    # curses_test_wrapped(None)


BODY = """\
 /-\\ 
 \\_/ 
 -o-
/ | \\
  o
 / \\
 | |""".split('\n')


if __name__ == '__main__':
    # speedtest()
    # LM = layer_test()

    curses_test()
