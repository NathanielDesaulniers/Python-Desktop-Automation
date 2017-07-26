#!/usr/local/bin/python2.7
import os
import time

# https://code.google.com/p/screenshot-cmd/


def take_screenshot(filename):

    folder = 'screens'
    if not os.path.isdir(folder):
        os.makedirs(folder)

    """
    folder = os.path.join(folder, time.strftime("%Y%m%d"))
    if not os.path.isdir(folder):
        os.makedirs(folder)
    """

    # folder = os.path.join(folder, time.strftime("%H.%M.%S"))
    folder = os.path.join(folder, str(filename))
    os.system("screenshot-cmd.exe -o {}{}".format(folder, ".png"))

