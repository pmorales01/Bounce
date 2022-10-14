#!/usr/bin/env python3
# Pedro Morales
# CPSC 386-03
# 2022-04-23
# pedrom2@csu.fullerton.edu
# @pedromorales451
#
# Lab 05-00
#
# This file creates and runs a Bouncing Balls game object.
#

"""
Imports the Bounce demo and executes the main function.
"""

import sys
from game import game

if __name__ == "__main__":
    NUM_BALLS = 5
    if len(sys.argv) > 1:
        NUM_BALLS = int(sys.argv[1])
    if NUM_BALLS >= 50:
        NUM_BALLS = 49
    if NUM_BALLS < 3:
        NUM_BALLS = 3
    VIDEO_GAME = game.BounceDemo(NUM_BALLS)
    VIDEO_GAME.build_scene_graph()
    VIDEO_GAME.run()
