"""
"""

# standard
import traceback

# custom
from pyz import curses_prep
from pyz.gamedata import json_parser
from pyz import controlmanager

####################################

def main():
    try:
        json_parser.load_all()
        curses_prep.curses.wrapper(controlmanager.mainwrapped)
    except Exception as e:
        with open("BAD3.txt", 'w') as f:
            f.write(traceback.format_exc())


if __name__ == '__main__':
    main()
