import pytest
from random import Random
from random import randint
from random import sample
from itertools import product
from copy import deepcopy
from hiveminder.game import make_flowers, make_hives
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from hiveminder.board import Board
from hiveminder.hive import Hive
from hiveminder.flower import Flower
from hiveminder.volant import Volant
from hiveminder.bee import Bee
from hiveminder.bee import QueenBee
from hiveminder.seed import Seed

from algos.MitMinder import *
from algosref import MitMinderRef as mr


# CONSTANTS
# ===========================================================

G_max_ind = 383
G_dim     = G_max_ind + 1
is_neighbour = \
((False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,True,False,True,False,False,False,False,False,False,True,True),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,True,False,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True,False),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False,True),(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,True,False))


mpaths_base = MPaths()


# MISC. FUNCTIONS
# ===========================================================

class _OtherBoard(object):
    def __init__(self):
        self._incoming = {}

def make_inflight(nbees, nqueens, nseeds, board_width, board_height, rng):
    all_possible_sites = list(product(range(1, board_width - 1), range(1, board_height - 1)))
    s = list(rng.sample(all_possible_sites,nbees+nqueens+nseeds))

    inflight  = [Bee(*tuple(list(site) + [0] + [25] + [DEFAULT_GAME_PARAMETERS])) for site in s[0:nbees]]
    inflight += [QueenBee(*tuple(list(site) + [0] + [25] + [DEFAULT_GAME_PARAMETERS])) for site in s[nbees:nbees+nqueens]]
    inflight += [Seed(*tuple(list(site) + [0])) for site in s[nbees+nqueens:nbees+nqueens+nseeds]]

    keys = [next(rand_id()) for _ in range(len(inflight))]
    return dict(zip(keys,inflight))


def get_random_boards(nhives,nflowers,nbees,nqueens,nseeds):
    #assert(0<= nhives + nbees + nqueens <= 64)
    #assert(0<= nseeds <= 64)
    #assert(0<= nhives + nflowers <= 64)
    #assert(0<= nseeds <= 64)
    assert(0<= nhives + nflowers + nbees + nqueens + nseeds <= 64)
    assert(0<= nhives <= 64)
    assert(0<= nflowers <= 64)
    assert(0<= nbees <= 64)
    assert(0<= nqueens <= 64)
    assert(0<= nseeds <= 64)

    rng = Random()
    board_width  = 8
    board_height = 8
    game_params  = DEFAULT_GAME_PARAMETERS

    hives = make_hives(nhives,
                       board_width,
                       board_height,
                       rng)

    flowers = make_flowers(nflowers,
                           hives,
                           board_width,
                           board_height,
                           rng, game_params)

    assert(len(flowers) == nflowers)

    inflight = make_inflight(nbees, nqueens, nseeds,
                             board_width,
                             board_height,
                             rng)

    turn_num = 2

    bboard = Board(game_params=DEFAULT_GAME_PARAMETERS,
                  board_width=board_width,
                  board_height=board_height,
                  hives=hives,
                  flowers=flowers,
                  neighbours={'N':1, 'S':1, 'E':1, 'W':1, 'NW':1, 'SE':1, },
                  inflight=inflight,
                  dead_bees=0)
    bboard._connect_to_neighbours([bboard, _OtherBoard()])

    mboard = MBoard()
    mboard.game_init(turn_num,[h.to_json() for h in bboard.hives],  \
                              [f.to_json() for f in bboard.flowers],\
                              {i: v.to_json() for i,v in bboard.inflight.items()})

    mrboard = mr.MBoard()
    mrboard.game_init(turn_num,[h.to_json() for h in bboard.hives],  \
                               [f.to_json() for f in bboard.flowers],\
                               {i: v.to_json() for i,v in bboard.inflight.items()})

    return mboard, mrboard, bboard


def board_compare(mboard,mrboard):

    assert(sorted(tuple(f.to_tuple() for f in mrboard.flowers.values()))== sorted(tuple(f.to_tuple() for f in mboard.flowers.values())))
    assert(sorted(tuple(b.to_tuple() for b in mrboard.bees.values()))   == sorted(tuple(b.to_tuple() for b in mboard.bees.values())))
    assert(sorted(tuple(q.to_tuple() for q in mrboard.qbees.values()))  == sorted(tuple(q.to_tuple() for q in mboard.qbees.values())))
    assert(sorted(tuple(s.to_tuple() for s in mrboard.seeds.values()))  == sorted(tuple(s.to_tuple() for s in mboard.seeds.values())))
    assert(sorted(tuple(h.to_tuple() for h in mrboard.hives.values()))  == sorted(tuple(h.to_tuple() for h in mboard.hives.values())))


# TEST FUNCTIONS
# ===========================================================

def test_get_random_boards(capsys):
    with capsys.disabled():
        print('')
        print('.[0] test_get_random_boards')

        nhives   = 5
        nflowers = 4
        nbees    = 8
        nqueens  = 4
        nseeds   = 3

        for test in range(40):
            mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
            board_compare(mboard,mrboard)

    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')


def test_list_of_commands(capsys):
    with capsys.disabled():
        print('')
        print('[1] test_list_of_commands')

        for test in range(1000):
            nhives   = 1
            nflowers = 1
            nbees    = 1
            nqueens  = 0
            nseeds   = 0
            mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
            cmds = mboard.commands()
            assert(len(cmds) == 1 + nbees*2 + nqueens*3 + nseeds*3)
            assert(len([cmd for cmd in cmds if cmd is not None and cmd.cmd=='create_hive']) == nqueens)
            assert(len([cmd for cmd in cmds if cmd is not None and cmd.cmd=='flower'])      == nseeds)

        for test in range(40):
            for nhives in range(1):
                for nflowers in range(1):
                    for nbees in range(3):
                        for nqueens in range(4):
                            for nseeds in range(2):
                                mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
                                cmds = mboard.commands()
                                assert(len(cmds) == 1 + nbees*2 + nqueens*3 + nseeds*3)
                                assert(len([cmd for cmd in cmds if cmd is not None and cmd.cmd=='create_hive']) == nqueens)
                                assert(len([cmd for cmd in cmds if cmd is not None and cmd.cmd=='flower'])      == nseeds)
    
    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')

def test_list_of_commands_ref(capsys):
    """
    Test that the next state commands do not change with respect to the reference.
    """
    with capsys.disabled():
        print('')
        print('.[2] test_list_of_commands_ref')

    ntests   = 1000
    nhives   = 5
    nflowers = 3
    nbees    = 3
    nqueens  = 3
    nseeds   = 2
    for i in range(ntests):
        mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
        assert( tuple(() if x is None else (x.key,x.volant,x.cmd) \
                         for x in sorted(mboard.commands(), key=lambda x: "" if x is None else x.key)) == \
                tuple(() if x is None else (x.key,x.volant,x.cmd) \
                         for x in sorted(mrboard.commands(),key=lambda x: "" if x is None else x.key)) )

    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')


def test_valid_next_move(capsys):
    """
    Test that a valid next move is returned.
    """
    with capsys.disabled():
        print('')
        print('.[3] test_valid_next_move')

    # test without qbees
    ntests   = 50
    nhives   = 5
    nflowers = 3
    nbees    = 3
    nqueens  = 0
    nseeds   = 2
    for i in range(ntests):
        mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
        out_cmds = (mboard.output_command(x) for x in mboard.commands())
        assert mboard.next_move() in out_cmds

    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')

def test_valid_next_move_with_queen(capsys):
    """
    Test that a valid next move is returned, when there are queens.
    """
    with capsys.disabled():
        print('')
        print('.[4] test_valid_next_move_with_queen')

    # test without qbees
    ntests   = 5
    nhives   = 5
    nflowers = 3
    nbees    = 3
    nseeds   = 2
    for i in range(ntests):
        nqueens  = randint(1,5)
        mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
        mpaths = deepcopy(mpaths_base)
        for i,hive in enumerate(mboard.hives.values()):
            if i == 0:
                mpaths.game = game_pos[hive.pos]
            mpaths.hives_pos.append(hive.pos)
            mpaths.graph_update(hive.pos)
        mpaths.short_paths_generate()
        mboard.mpaths = mpaths

        out_cmds = (mboard.output_command(x) for x in mboard.commands())
        assert mboard.next_move() in out_cmds

    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')

def test_turn(capsys):
    """
    Test that next state calculation is the same.
    """
    with capsys.disabled():
        print('')
        print('.[5] test_turn')

    # test without qbees
    ntests   = 100
    nhives   = 5
    nflowers = 3
    nbees    = 3
    nqueens  = 0
    nseeds   = 2
    for i in range(ntests):
        mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)

        # depth 1
        cmd = sample(mboard.commands(),1)[0]
        mboard.turn(cmd)
        mrboard.turn(cmd)
        board_compare(mboard,mrboard)
        
        # depth 2
        cmd = sample(mboard.commands(),1)[0]
        mboard.turn(cmd)
        mrboard.turn(cmd)
        board_compare(mboard,mrboard)

        # depth 3
        cmd = sample(mboard.commands(),1)[0]
        mboard.turn(cmd)
        mrboard.turn(cmd)
        
        
    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')


def test_evaluate(capsys):
    with capsys.disabled():
        print('')
        print('.[6] test_evaluate')

    # test without qbees
    ntests   = 100
    nhives   = 5
    nflowers = 3
    nbees    = 3
    nqueens  = 2
    nseeds   = 2
    for i in range(ntests):
        mboard, mrboard, bboard = get_random_boards(nhives,nflowers,nbees,nqueens,nseeds)
        assert isinstance(mboard.evaluate() , int)
        assert not isinstance(mboard.evaluate(), bool)
    
    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')



def test_id_pos_heading_conversions(capsys):
    with capsys.disabled():
        print('')
        print('[7] test_id_pos_heading_conversion')
 
    global G_max_ind

    for pos in range(64):
        all_h_ids = MPaths.get_idns_from_p(pos)

        all_h_ids_single_get = []
        for h in valid_headings:
            id_node = MPaths.get_idn_from_ph(pos,h)
            assert(0 <= id_node <= G_max_ind)
            assert((pos,h) == MPaths.get_ph_from_idn(id_node))
            assert(pos == MPaths.get_p_from_idn(id_node))
            assert(h == MPaths.get_h_from_idn(id_node))
            all_h_ids_single_get.append(id_node)
        assert(tuple(all_h_ids_single_get) == tuple(all_h_ids))
            
    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')
    pass


def test_G_generate(capsys):
    with capsys.disabled():
        print('')
        print('[8] test_G_generate')

    mpaths = MPaths()
    # test for node connectivity
    for pos in range(64):
        for heading in valid_headings:
            graph_new_pos = [MPaths.get_p_from_idn(idn) for idn in range(len(mpaths.graph[ MPaths.get_idn_from_ph(pos,heading) ])) if \
                                                                   mpaths.graph[ MPaths.get_idn_from_ph(pos,heading) ][idn] == 1]
            if not (len(graph_new_pos) == 1 or len(graph_new_pos) == 0):
                print(pos)
                print(heading)
                print(MPaths.get_idn_from_ph(pos,heading))
                print(MPaths.get_p_from_idn(MPaths.get_idn_from_ph(pos,heading)))
                print(mpaths.graph[MPaths.get_idn_from_ph(pos,heading)])
                raise AssertionError
            if len(graph_new_pos) == 0:
                assert new_pos[heading][pos] < 0 or new_pos[heading][pos] >= 64
            if len(graph_new_pos) == 1:
                assert graph_new_pos[0] == new_pos[heading][pos]

    # test conectivity with neighbours
    for pos in range(64):
        for heading in valid_headings:
            graph_new_pos = [MPaths.get_p_from_idn(idn) for idn in range(len(mpaths.graph[ MPaths.get_idn_from_ph(pos,heading) ])) if \
                                                                   mpaths.graph[ MPaths.get_idn_from_ph(pos,heading) ][idn] == 1 or \
                                                                   mpaths.graph[ MPaths.get_idn_from_ph(pos,heading) ][idn] == 2]
            if not 0<= len(graph_new_pos) <= 6:
                print(pos)
                print(heading)
                print(graph_new_pos)
                print(mpaths.graph[ MPaths.get_idn_from_ph(pos,heading) ])
                raise AssertionError
            for connected_pos in graph_new_pos:
                assert is_neighbour[connected_pos][pos]


    with capsys.disabled():
        print(' --> DONE')
        print('-----------------')

def main():
    return pytest.main([__file__])

if __name__ == '__main__':
    main()
