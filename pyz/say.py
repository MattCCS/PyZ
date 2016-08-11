
import subprocess

def say(s, r=200):
    subprocess.check_output(['say', s, '-r', str(r)])

