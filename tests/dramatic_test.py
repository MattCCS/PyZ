
import curses
import time

import subprocess
import os

def start():
    subprocess.Popen(["afplay", "/Users/Matt/Desktop/wciii_sounds/NightElfDefeat.mp3"])

def stop():
    os.system("ps ax | grep afplay | awk '{print $1}' | xargs kill")

Y = 8

L = [
    ("Let me tell you a tale", "of a kingdom long forgotten..."),
    ("Lorem ipsum dolor", "sit amet"),
    ("Here is a bunch of text", "that will be printed line...", "... by line."),
]

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(1)) # set background color to WHITE ON BLACK
    stdscr.refresh()

    time.sleep(0.5)

    for page in L:
        # each page:
        time.sleep(0.5)

        # (fade in)
        for (i,row) in enumerate(page):
            # each row:
            for c in ([16] + range(232, 255+1)):
                # each frame:
                curses.init_pair(c, c, 0) # on black
                stdscr.addstr(Y+i, 20, row, curses.color_pair(c))
                time.sleep(0.2)
                stdscr.refresh()
            time.sleep(0.5)

        # (fade out)
        for c in (range(255, 232-1, -1) + [16]):
            # each frame:
            for (i,row) in enumerate(page):
                curses.init_pair(c, c, 0) # on black
                stdscr.addstr(Y+i, 20, row, curses.color_pair(c))
                stdscr.refresh()
            time.sleep(0.1)

        stdscr.clear()
        stdscr.refresh()

    time.sleep(0.5)

start()
curses.wrapper(main)
stop()
