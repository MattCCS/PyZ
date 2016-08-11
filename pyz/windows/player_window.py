# encoding: utf-8
# Author: Matthew Cotton

"""
This file contains code for displaying the bodily health/status
of the player so the player has some context about their injuries.
"""

import sys

####################################

PYTHON2 = sys.version_info[0] == 2

if PYTHON2:
    BODY = u"""\
 /-\\ 
 \\_/ 
 -o-
/ | \\
  o
 / \\
 | |""".split('\n')
else:
    BODY = u"""\
 /⎺\\ 
 \\_/ 
 -o- 
⎛ | ⎞
  o  
 ⎛ ⎞ 
 ⎜ ⎟ """.split('\n')

####################################

