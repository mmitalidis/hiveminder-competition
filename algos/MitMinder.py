from copy import deepcopy
from random import randint
from heapq import heappush, heappop
from operator import itemgetter
import signal
import time
from numpy import argmax, argsort
from hiveminder import algo_player

#===================================================================================#
#                                    CONSTANTS                                      #
#===================================================================================#

last_turn  = 9999
best_n     = 3
dlim       = 30

# Maximum number of children on a cache level. Increases per level basis, if necessary.
max_chilen = 40

#===================================================================================#
#                                 GLOBAL DATA (declarations)                        #
#===================================================================================#

cache  = None
mpaths = None

#===================================================================================#
#                                  PRE-COMPUTED (declarations)                      #
#===================================================================================#

valid_headings = None
new_headings   = None
opp_headings   = None
alt_headings   = None
heading_enum   = None
heading_denum  = None
new_pos        = None
onew_pos       = None
reach_pos      = None
priority       = None
game_pos       = None
path_crosses   = None
first_short_paths = None



#===================================================================================#
#                                  SHORTEST PATH                                    #
#===================================================================================#


# MPaths class - for shortest path between two tiles (avoiding hives)
# ----------------------------------------------------------------------------------

class MPaths():
    board_width  = 8
    board_height = 8
    board_pos    = 64

    __slots__ = ('graph','short_paths','hives_pos','game')
    def __init__(self,board_width,board_height,first_hive=None):
        MPaths.board_width  = board_width
        MPaths.board_height = board_height
        MPaths.board_pos    = MPaths.board_width*MPaths.board_height

        self.graph_generate()
        self.hives_pos = []
        self.game      = None

        if first_hive is not None:
            global game_pos
            self.add_hive(first_hive)
            self.game = game_pos[first_hive]
        else:
            self.short_paths_generate()

    # Update the class, after we have added a new hive.
    # ---------------------------------------------------------------------------------------------------------

    def add_hive_from_input(self,hives):
        if len(hives) == len(self.hives_pos):
            return

        in_hives_pos = [ h[0]*MPaths.board_width+h[1] for h in hives ]
        for pos in in_hives_pos:
            if pos not in self.hives_pos:
                self.add_hive(pos)


    def add_hive(self,pos):
        # store current hive pos
        self.hives_pos.append(pos)

        # graph update - other nodes cannot lead to this node from now on
        self.graph_update(pos)
 
        # shortest paths re-calculate
        self.short_paths_generate()


    # Connectivity of board tiles graph. Note, that a graph nodes includes both position and heading info.
    # ---------------------------------------------------------------------------------------------------------

    def graph_generate(self):
        """
        graph[i][j] = {9: node j inaccessible from node i,
                       1: node j accessible   from node i - no need to change heading,
                       2: node j accessible   from node i - need to change heading}
        pos     in [0,64)
        heading in {0,60,120,180,-120,-60}
        """
        global alt_headings
 
        npos = MPaths.board_pos
        nhead = 6
        nnodes = npos*nhead
    
        self.graph = [[9 for i in range(nnodes)] for j in range(nnodes)]
        
        for id_node in range(nnodes):
            pos, heading = MPaths.get_ph_from_idn(id_node)
            
            for new_heading in alt_headings[heading]:
                the_new_pos = new_pos[new_heading][pos]
                if 0<= the_new_pos < MPaths.board_pos:
                    new_id_node = MPaths.get_idn_from_ph(the_new_pos, new_heading)
    
                    if new_heading == heading:
                        self.graph[id_node][new_id_node] = 1
                    else:
                        self.graph[id_node][new_id_node] = 2


    def graph_update(self,pos):
        id_del = MPaths.get_idns_from_p(pos)

        for id_node in id_del:
            for other in range(len(self.graph)):
                self.graph[other][id_node] = 9
    

    # Dijkstra to generate the shortest paths for all pairs of nodes
    # ---------------------------------------------------------------------------------------------------------

    def dijkstra(self, start):
        dist = [None for _ in range(len(self.graph))]
        queue = [(0, start)]
        p = {}
        while queue:
            path_len, v = heappop(queue)
            if dist[v] is None: # v is unvisited
                dist[v] = path_len
                for w in [i for i,d in enumerate(self.graph[v]) if d<9]:
                    if dist[w] is None or path_len < dist[w]:
                        heappush(queue, (path_len + 1, w))
                        p[w] = v
    
        return p
    
    def short_paths_from_start(self,start):
        p = self.dijkstra(start)
        paths = [[] for i in range(len(self.graph[0]))]
    
        for end in range(len(self.graph[0])):
            current = end
            while True:
                paths[end].insert(0,current)
                if current == start:
                    break
                if current not in p:
                    # this end is unreachable
                    paths[end] = []
                    break
                current = p[current]
    
        return paths
    
    
    def short_paths_generate(self):
        self.short_paths = [[[] for i in range(len(self.graph))] for j in range(len(self.graph))]
    
        for start in range(len(self.graph)):
            self.short_paths[start] = self.short_paths_from_start(start)
    

    # Static methods for (pos, id conversions)
    # ---------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_idn_from_ph(pos,heading):
        global heading_enum
        return MPaths.board_pos*heading_enum[heading]+pos
    
    @staticmethod
    def get_p_from_idn(id_node):
        heading_id = id_node // MPaths.board_pos
        pos        = id_node - heading_id * MPaths.board_pos
        return pos
    
    @staticmethod
    def get_h_from_idn(id_node):
        global heading_denum
        heading_id = id_node // MPaths.board_pos
        return heading_denum[heading_id]
    
    @staticmethod
    def get_ph_from_idn(id_node):
        global heading_denum
        heading_id = id_node // MPaths.board_pos
        pos        = id_node - heading_id * MPaths.board_pos
        return pos, heading_denum[heading_id]
    
    @staticmethod
    def get_idns_from_p(pos):
        """
        Get all graph id_nodes belonging to a single position.
        """
        global valid_headings
        return [MPaths.get_idn_from_ph(pos,h) for h in valid_headings]
    
    @staticmethod
    def get_ppath_from_idns(id_path):
        """
        Given a path in graph ids return the equivalent path in pos ids.
        """
        path_pos = []
        for idn in id_path:
            path_pos.append(MPaths.get_p_from_idn(idn))
        return path_pos
    


#===================================================================================#
#                                     MBOARD                                        # 
#===================================================================================#


# Data Containers
# ----------------------------------------------------------------------------------

class Mhive():
    __slots__ = ('pos','nectar')
    def __init__(self, pos, nectar):
        self.pos    = pos
        self.nectar = nectar
    def to_tuple(self):
        return (self.pos,self.nectar)

class Mflower():
    __slots__ = ('pos','potency','visits','ttl')
    def __init__(self, pos, potency, visits, ttl):
        self.pos     = pos
        self.potency = potency
        self.visits  = visits
        self.ttl     = ttl
    def to_tuple(self):
        return (self.pos, self.potency, self.visits, self.ttl)

class Mbee():
    __slots__ = ('pos','heading','energy','nectar')
    def __init__(self, pos, heading, energy, nectar):
        self.pos     = pos
        self.heading = heading
        self.energy  = energy
        self.nectar  = nectar
    def to_tuple(self):
        return (self.pos, self.heading, self.energy, self.nectar)

class Mqbee():
    __slots__ = ('pos','heading','energy','nectar')
    def __init__(self, pos, heading, energy, nectar):
        self.pos     = pos
        self.heading = heading
        self.energy  = energy
        self.nectar  = nectar
    def to_tuple(self):
        return (self.pos, self.heading, self.energy, self.nectar)

class Mseed():
    __slots__ = ('pos','heading')
    def __init__(self, pos, heading):
        self.pos     = pos
        self.heading = heading
    def to_tuple(self):
        return (self.pos, self.heading)

class Vocounter():
    """
    Volant counter. Counts how many volants left or died.
    """
    __slots__ = ('bees','qbees','seeds')
    def __init__(self, bees =0, qbees =0, seeds =0):
        self.bees  = bees
        self.qbees = qbees
        self.seeds = seeds

class Command():
    __slots__ = ('volant','cmd','key')
    def __init__(self,volant,cmd,key):
        self.volant = volant
        self.cmd    = cmd
        self.key    = key


# Misc. functions and definitions.
# ----------------------------------------------------------------------------------

def rand_id():
    yield str(randint(0,9999999999999999999))


class TimeOutException(Exception):
    """
    TimeOutException in order to stop the game tree traversal.
    """
    def __init__(self, message="", errors=""):
        super(TimeOutException, self).__init__(message)
        self.errors = errors

def timeout_handler(signum,frame):
    raise TimeOutException()



# MBoard class
# ----------------------------------------------------------------------------------

class MBoard():
    """
    MBoard is a board class. The aim is to be fast to go to the next state. No neighbours connections.
    """
    board_width  = 8
    board_height = 8
    board_pos    = 64
    __slots__ = ('hives','flowers','bees','qbees','seeds','dead','left','turn_num','mpaths')
    def __init__(self,
                 board_width  = None,\
                 board_height = None,\
                 board_pos    = None,\
                 hives    =None,\
                 flowers  =None,\
                 bees     =None,\
                 qbees    =None,\
                 seeds    =None,\
                 dead     =None,\
                 left     =None,\
                 turn_num =None,\
                 mpaths   =None):
        MBoard.board_width  = board_width
        MBoard.board_height = board_height
        MBoard.board_pos    = board_pos
        self.hives    = deepcopy(hives)
        self.flowers  = deepcopy(flowers)
        self.bees     = deepcopy(bees)
        self.qbees    = deepcopy(qbees)
        self.seeds    = deepcopy(seeds)
        self.dead     = deepcopy(dead)
        self.left     = deepcopy(left)
        self.turn_num = turn_num
        self.mpaths   = mpaths


    # MBoard basics (initialization, board advance i.e turn, available commands, copy and turn, static board evaluation, next move)
    # ---------------------------------------------------------------------------------------------------------

    def game_init(self,turn_num,board_width,board_height,in_hives,in_flowers,in_inflight,mpaths=None):
        """
        Parse inputs (hives, flowers, inflights) - lists of lists
        hives   : [pos,nectar]
        flowers : [pos,potency,visits,ttl]
        bees    : [pos,heading,energy,nectar]
        qbees   : [pos,heading,energy,nectar]
        seeds   : [pos,heading]

        Note that ttl = turn_that_expires - turn_num
        Also, id of inflight can be used to access the key list.
        """
        # clear object data
        MBoard.board_width  = 8
        MBoard.board_height = 8
        MBoard.board_pos    = 64
        self.hives      = dict()
        self.flowers    = dict()
        self.bees       = dict()
        self.qbees      = dict()
        self.seeds      = dict()
        self.dead       = Vocounter()
        self.left       = Vocounter()
        self.turn_num   = turn_num
        self.mpaths     = mpaths

        # set board dimensions
        MBoard.board_width  = board_width
        MBoard.board_height = board_height
        MBoard.board_pos    = board_width*board_height

        # transform input to lists and store keys
        self.hives   = dict((next(rand_id()), Mhive(x[0]*MBoard.board_width +x[1], x[2]))                      for x in in_hives)
        self.flowers = dict((next(rand_id()), Mflower(x[0]*MBoard.board_width +x[1], x[3], x[4], x[5]-turn_num)) for x in in_flowers)

        for key, v in in_inflight.items():
            if v[0] == 'Bee':
                self.bees[key]  = Mbee(v[1]*MBoard.board_width +v[2], v[3], v[4], v[6])
            elif v[0] == 'QueenBee':
                self.qbees[key] = Mqbee(v[1]*MBoard.board_width +v[2], v[3], v[4], v[6])
            elif v[0] == 'Seed':
                self.seeds[key] = Mseed(v[1]*MBoard.board_width +v[2], v[3])



    def commands(self):
        """
        Get all the commands that can be issued from this board.
        [isBug, id, new_heading or 'create_hive' or 'flower']
        @return: A list with all the commands.
        """
        cmds = [None]

        # change heading
        for key,bee in self.bees.items():
            for new_heading in new_headings[bee.heading]:
                cmds.append( Command('Bee',new_heading,key) )

        for key,qbee in self.qbees.items():
            for new_heading in new_headings[qbee.heading]:
                cmds.append( Command('QueenBee',new_heading,key) )

        for key,seed in self.seeds.items():
            for new_heading in new_headings[seed.heading]:
                cmds.append( Command('Seed',new_heading,key) )
            
        # create a hive
        for key,qbee in self.qbees.items():
            cmds.append( Command('QueenBee','create_hive',key) )

        #create a flower
        for key,seed in self.seeds.items():
            cmds.append( Command('Seed','flower',key) )

        return cmds


    def output_command(self,command):
        if command is not None:
            return dict(entity=command.key, command=command.cmd)
        else:
            return None


    def make(self,other_board,command):
        # copy other_board data
        self.hives    = deepcopy(other_board.hives)
        self.flowers  = deepcopy(other_board.flowers)
        self.bees     = deepcopy(other_board.bees)
        self.qbees    = deepcopy(other_board.qbees)
        self.seeds    = deepcopy(other_board.seeds)
        self.dead     = deepcopy(other_board.dead)
        self.left     = deepcopy(other_board.left)
        self.turn_num = deepcopy(other_board.turn_num)
        self.mpaths   = other_board.mpaths

        # advance board
        self.turn(command)

 
    def turn(self,command):

        # 1. apply user command
        if command is not None:
            if command.volant == 'Bee':
                self.bees[ command.key ].heading = command.cmd
            elif command.volant == 'QueenBee':
                if command.cmd == 'create_hive':
                    self.hives   = dict((key,hive) for (key,hive) in self.hives.items()   if hive.pos != self.qbees[ command.key ].pos)
                    self.flowers = dict((key,fl)   for (key,fl)   in self.flowers.items() if fl.pos   != self.qbees[ command.key ].pos)

                    self.hives[ next(rand_id()) ] = Mhive(self.qbees[command.key].pos, self.qbees[command.key].nectar)
                    del self.qbees[ command.key ]
                else:
                    self.qbees[ command.key ].heading = command.cmd
            else:
                if command.cmd == 'flower':
                    self.hives   = dict((key,hive) for (key,hive) in self.hives.items()   if hive.pos != self.seeds[ command.key ].pos)
                    self.flowers = dict((key,fl)   for (key,fl)   in self.flowers.items() if fl.pos   != self.seeds[ command.key ].pos)

                    self.flowers[ next(rand_id()) ] = Mflower(self.seeds[command.key].pos,1,0,300)
                    del self.seeds[ command.key ]
                else:
                    self.seeds[ command.key ].heading = command.cmd
            

        # 2. move and send volants
        for key,bee in self.bees.items():
            self.bees[key].pos = new_pos[bee.heading][bee.pos]
            self.bees[key].energy -= 1

        for key,qbee in self.qbees.items():
            self.qbees[key].pos = new_pos[qbee.heading][qbee.pos]
            self.qbees[key].energy -= 1

        for key,seed in self.seeds.items():
            self.seeds[key].pos = new_pos[seed.heading][seed.pos]


        old_bees_len  = len(self.bees)
        old_qbees_len = len(self.qbees)
        old_seeds_len = len(self.seeds)

        self.bees  = dict((key,bee)  for (key,bee)  in self.bees.items()  if 0<= bee.pos  < MBoard.board_pos)
        self.qbees = dict((key,qbee) for (key,qbee) in self.qbees.items() if 0<= qbee.pos < MBoard.board_pos)
        self.seeds = dict((key,seed) for (key,seed) in self.seeds.items() if 0<= seed.pos < MBoard.board_pos)

        new_bees_len  = len(self.bees)
        new_qbees_len = len(self.qbees)
        new_seeds_len = len(self.seeds)

        self.left.bees  += old_bees_len  - new_bees_len
        self.left.qbees += old_qbees_len - new_qbees_len
        self.left.seeds += old_seeds_len - new_seeds_len

        # 4. send bees to flowers - just add nectar to bees
        fl_pos = (fl.pos for fl in self.flowers.values())
        for bkey,bee in self.bees.items():
            if bee.pos in fl_pos:
                self.bees[bkey].nectar += 3

        # 5. bees that return to hives
        old_qbees_len = len(self.qbees)

        # leave nectar to hives
        for hkey, hive in self.hives.items():
            for bkey, bee in self.bees.items():
                if bee.pos == hive.pos:
                    self.hives[hkey].nectar += bee.nectar

        # delete bees, qbees
        hives_pos  = tuple(hive.pos for hive in self.hives.values())
        self.bees  = dict((key,bee) for (key,bee) in self.bees.items()  if bee.pos not in hives_pos)
        self.qbees = dict((key,qb)  for (key,qb)  in self.qbees.items() if qb.pos  not in hives_pos)

        new_qbees_len = len(self.qbees)
        self.dead.qbees += old_qbees_len - new_qbees_len


        # 6. detect dead bees and seeds (headon crashes)
        old_bees_len  = len(self.bees)
        old_qbees_len = len(self.qbees)

        # crashes
        all_bees_on_tile = dict()
        for bee in self.bees.values():
            if bee.pos not in all_bees_on_tile:
                all_bees_on_tile[bee.pos] = 0
            all_bees_on_tile[bee.pos] += 1

        for qbee in self.qbees.values():
            if qbee.pos not in all_bees_on_tile:
                all_bees_on_tile[qbee.pos] = 0
            all_bees_on_tile[qbee.pos] += 1

        self.bees  = dict((key,bee)  for (key,bee)  in self.bees.items()  if all_bees_on_tile[bee.pos]  == 1)
        self.qbees = dict((key,qbee) for (key,qbee) in self.qbees.items() if all_bees_on_tile[qbee.pos] == 1)
        
        all_seeds_on_tile = dict()
        for seed in self.seeds.values():
            if seed.pos not in all_seeds_on_tile:
                all_seeds_on_tile[seed.pos] = 0
            all_seeds_on_tile[seed.pos] += 1

        self.seeds = dict((key,seed) for (key,seed) in self.seeds.items() if all_seeds_on_tile[seed.pos] == 1)

        # headon crashes
        bees_to_del  = set()
        qbees_to_del = set()
        seeds_to_del = set()

        for key, bee in self.bees.items():
            for other_key, other_bee in self.bees.items():
                if (other_bee.pos == onew_pos[bee.heading][bee.pos]) and (other_bee.heading == opp_headings[bee.heading]):
                    bees_to_del.add(key)
                    bees_to_del.add(other_key)
                    break
            for other_key, other_qbee in self.qbees.items():
                if (other_qbee.pos == onew_pos[bee.heading][bee.pos]) and (other_qbee.heading == opp_headings[bee.heading]):
                    bees_to_del.add(key)
                    qbees_to_del.add(other_key)
                    break

        for key, qbee in self.qbees.items():
            for other_key, other_bee in self.bees.items():
                if (other_bee.pos == onew_pos[qbee.heading][qbee.pos]) and (other_bee.heading == opp_headings[qbee.heading]):
                    qbees_to_del.add(key)
                    bees_to_del.add(other_key)
                    break
            for other_key, other_qbee in self.qbees.items():
                if (other_qbee.pos == onew_pos[qbee.heading][qbee.pos]) and (other_qbee.heading == opp_headings[qbee.heading]):
                    qbees_to_del.add(key)
                    qbees_to_del.add(other_key)
                    break

        for key, seed in self.seeds.items():
            for other_key, other_seed in self.seeds.items():
                if (other_seed.pos == onew_pos[seed.heading][seed.pos]) and (other_seed.heading == opp_headings[seed.heading]):
                    seeds_to_del.add(key)
                    seeds_to_del.add(other_key)
                    break

        for key in bees_to_del:
            del self.bees[key]

        for key in qbees_to_del:
            del self.qbees[key]

        for key in seeds_to_del:
            del self.seeds[key]

        new_bees_len  = len(self.bees)
        new_qbees_len = len(self.qbees)

        self.dead.bees  += old_bees_len  - new_bees_len
        self.dead.qbees += old_qbees_len - new_qbees_len

        # 7. increment turn number
        self.turn_num += 1


    def is_on_course_with_any(self,inflight,targets):
        global reach_pos
        for target in targets.values():
            if target.pos in reach_pos[inflight.heading][inflight.pos]:
                return True
        return False


    def nbees_to_min_nectar_hive(self):
        if len(self.hives) == 0:
            return 0

        nbees = 0
        min_hive_pos = min(self.hives.values(), key=lambda x: x.nectar%100).pos
        for bee in self.bees.values():
            if min_hive_pos in reach_pos[bee.heading][bee.pos] and bee.nectar == 5:
                nbees += 1

        return nbees


    def evaluate(self):
        score = (200*len(self.hives) + 50*len(self.flowers) -3*(self.dead.bees+self.dead.qbees) +\
                   2*sum(x.nectar for x in self.hives.values()))

        nectar_on_bees = sum(bee.nectar  for bee  in self.bees.values())
        bees_peak  = len([bee for bee in self.bees.values() if bee.nectar < 5 and self.is_on_course_with_any(bee,self.flowers)])
        bees_store = len([bee for bee in self.bees.values() if bee.nectar > 0 and self.is_on_course_with_any(bee,self.hives)])
        nbees_to_min_hive = self.nbees_to_min_nectar_hive()

        w = (626, 516, 712, 828, 700)
        evaluate = w[0]*score + w[1]*nectar_on_bees + w[2]*bees_peak + w[3]*bees_store + w[4]*nbees_to_min_hive 
        return evaluate


    def next_move(self):
        global dlim
        if len(self.qbees) != 0:
            return self.output_command( self.qbee_best_cmd() )
        else:
            return self.output_command( self.bee_best_cmd(dlim) )


    # Queen strategy in MBoard (go to tile with highest priority, using the shortest path)
    # ---------------------------------------------------------------------------------------------------------

    def qbee_best_cmd(self):

        # start counting time
        time_start = time.time()
    
        # available tiles to create hive (ignore flowers)
        free_pos = tuple( set(range(MBoard.board_pos)) - set(hive.pos for hive in self.hives.values()) )
    
        # we will only work with one queen bee
        for qkey, qbee in self.qbees.items():

            # get the starting node
            start_idn = MPaths.get_idn_from_ph(qbee.pos, qbee.heading)

            # keep tiles
            tiles = []
            for end_pos in free_pos:
                end_idns = MPaths.get_idns_from_p(end_pos)
                for end_idn in end_idns:

                    path_len = len(self.mpaths.short_paths[start_idn][end_idn])
                    if path_len != 0:
                        tiles.append((end_idn,priority[self.mpaths.game][end_pos],path_len))
    
            # sort based on priority and route length
            tiles.sort(key=itemgetter(1,2))
    
            # search for a viable route and follow the command
            while tiles:
                tile = tiles.pop(0)
                cond, cmd = self.is_viable(qkey,start_idn,tile[0])
                if cond:
                    return cmd
    
    
        # we failed to find a viable route for the queen, return the best the bees can do
        time_stop = time.time()
        time_diff = time_stop - time_start
        time_remain = 0.193 - time_diff
        if time_remain > 0.01:
            global dlim
            return self.bee_best_cmd(dlim, time_remain)
        else:
            return None


    def is_viable(self,qkey,start_idn,end_idn):

        if start_idn == end_idn:
            return True, Command('QueenBee','create_hive',qkey) 

        # get the path we will check (node ids and positions)
        path_idn = self.mpaths.short_paths[start_idn][end_idn]
        path_pos = MPaths.get_ppath_from_idns( path_idn )

        # get the bugs (bees,qbees) that are dangerous
        danger_bugs = self.list_of_danger_bugs(qkey,path_pos)

        # need_command  (list with True/False - a move needs to be played at that step)
        need_command = [False for _ in range(len(path_pos)-1)]

        # first_command (the command we will play if the path is viable)
        first_command = None

        # initialize need_command, first_command
        for step in range(len(path_idn)-1):
            requires_queen_command = self.mpaths.graph[ path_idn[step] ][ path_idn[step+1] ] == 2
            if requires_queen_command:
                need_command[step] = True
                if step == 0:
                    new_heading = MPaths.get_h_from_idn(path_idn[step+1])
                    first_command = Command('QueenBee',new_heading,qkey)

        # stop early if there are too many danger bugs
        number_of_available_moves = len([f for f in need_command if f is False])
        if len(danger_bugs) > number_of_available_moves:
            return False, None


        # try to avoid all danger_bugs
        while danger_bugs:

            # get next danger bug
            dbug = danger_bugs.pop(0)
            dbug_type = dbug[0]
            dbug_key  = dbug[1]

            # too late, we cannot do anything
            if need_command.index(False) > dbug[2]:
                return False, None

            if dbug_type == 'Bee':
                # try to turn the bug left
                crash_if_left,_ =self.is_danger_bee(new_pos[new_headings[self.bees[dbug_key].heading][0]][ self.bees[dbug_key].pos ],\
                                                    new_headings[self.bees[dbug_key].heading][0], \
                                                    dbug_key, 
                                                    path_pos[1:])
                # try to turn the bug right
                crash_if_right,_ =self.is_danger_bee(new_pos[new_headings[self.bees[dbug_key].heading][1]][self.bees[dbug_key].pos],\
                                                     new_headings[self.bees[dbug_key].heading][1], \
                                                     dbug_key, 
                                                     path_pos[1:])
            else:
                # repeat the above for the qbees
                crash_if_left,_ =self.is_danger_qbee(new_pos[new_headings[self.qbees[dbug_key].heading][0]][self.qbees[dbug_key].pos],\
                                                     new_headings[self.qbees[dbug_key].heading][0], \
                                                     dbug_key, 
                                                     path_pos[1:])
                crash_if_right,_=self.is_danger_qbee(new_pos[new_headings[self.qbees[dbug_key].heading][1]][self.qbees[dbug_key].pos],\
                                                     new_headings[self.qbees[dbug_key].heading][1], \
                                                     dbug_key, 
                                                     path_pos[1:])


            # we will avoid the bug if it turns to left
            if not crash_if_left:
                if first_command is None:
                    if dbug_type == 'Bee':
                        first_command = Command('Bee',new_headings[self.bees[dbug_key].heading][0],dbug_key)
                    else:
                        first_command = Command('QueenBee',new_headings[self.qbees[dbug_key].heading][0],dbug_key)
                need_command[ need_command.index(False) ] = True

            # we will avoid the bug if it turns to right
            elif not crash_if_right:
                if first_command is None:
                    if dbug_type == 'Bee':
                        first_command = Command('Bee',new_headings[self.bees[dbug_key].heading][1],dbug_key)
                    else:
                        first_command = Command('QueenBee',new_headings[self.qbees[dbug_key].heading][1],dbug_key)
                need_command[ need_command.index(False) ] = True

            # we cannot avoid the bug
            else:
                return False,None

        # we managed to avoid all danger bugs, the route is viable
        return True, first_command
 

    def is_danger_bee(self,pos,heading,key,path_pos):
        if not 0<= pos < MBoard.board_pos:
            return False,None

        to_cross = path_crosses[heading][pos]

        for ind in range(min(len(path_pos), len(to_cross))):
            if to_cross[ind] == path_pos[ind]:
                return True, ('Bee',key,ind)
        return False, None


    def is_danger_qbee(self,pos,heading,key,path_pos):
        if not 0<= pos < MBoard.board_pos:
            return False,None

        to_cross = path_crosses[heading][pos]

        for ind in range(min(len(path_pos), len(to_cross))):
            if to_cross[ind] == path_pos[ind]:
                return True, ('QueenBee',key,ind)
        return False, None


    def list_of_danger_bugs(self,qkey,path_pos):

        danger_bugs = []
        for key,bee in self.bees.items():
            cond, bug = self.is_danger_bee(bee.pos,bee.heading,key,path_pos)
            if cond:
                danger_bugs.append(bug)

        for key,qbee in self.qbees.items():
            if key != qkey:
                cond, bug = self.is_danger_qbee(qbee.pos,qbee.heading,key,path_pos)
                if cond:
                    danger_bugs.append(bug)

        danger_bugs.sort(key=itemgetter(2))
        return danger_bugs

    # Bee strategy in MBoard (search the game tree. Expand only the "best_n" nodes with the highest static evaluation (most promising)
    # ---------------------------------------------------------------------------------------------------------
             
    def bee_best_cmd(self,depth,time_lim=0.193):
        """
        Iterative deepening dfs. Searches for depths [1,depth]
        """
        best_cmd = None

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, time_lim)

        try:
            for d in range(1,depth+1):
                best_cmd = self.iddfs(d)
        except TimeOutException:
            pass

        signal.alarm(0)
        return best_cmd

    def iddfs(self,fdepth):
        """
        iddfs argument
            fdepth = final_depth
        """
        global best_n
        global cache

        cmds = self.commands()

        # if children are more than cache size, increase cache
        if len(cmds) > len(cache[0]):
            cache[0] += [MBoard() for _ in range(len(cmds))]

        # make the children MBoard
        for x,cmd in enumerate(cmds):
            cache[0][x].make(self,cmd)

        # evaluate children and get the sorted list indices (descending)
        children_eval = [cache[0][x].evaluate() for x in range(len(cmds))]
        sorted_ind = argsort(children_eval)[::-1]

        # how many children nodes will be examined?
        nchildren = min(best_n,len(sorted_ind))

        # return the command that leads to the child with the best score
        ind = argmax([ cache[0][sorted_ind[x]].dls(1,fdepth) for x in range(nchildren) ])
        return cmds[sorted_ind[ind]]

    def dls(self,cdepth,fdepth):
        """
        dls arguments:
            cdepth = current depth
            fdepth = final depth
        """
        ndepth = cdepth + 1
        global best_n
        global cache

        cmds = self.commands()

        # If we reached the final depth (should only happen for fdepth == cdepth == 1)
        # Also, new inflights won't be generated, so if we have no moves, do not search the tree with "None"
        if (cdepth == fdepth) or (len(cmds) == 1) or (self.turn_num == last_turn):
            return self.evaluate()


        # if number of children is more than the cache size, increase its size
        if len(cmds) > len(cache[cdepth]):
            cache[cdepth] += [MBoard() for _ in range(len(cmds))]

        # evaluate the new children nodes
        children_eval = []
        for x,cmd in enumerate(cmds):
            cache[cdepth][x].make(self,cmd)
            children_eval.append(cache[cdepth][x].evaluate())

        # get the sorted indices
        sorted_ind = argsort(children_eval)[::-1]

        nchildren = min(best_n, len(sorted_ind))

        # make the MBoard only for the best children
        for x in range(nchildren):
            cache[cdepth][x].make(self,cmds[sorted_ind[x]])

        # repeat the algorithm for the just-made-children, and return the max leaf evaluation
        return max([cache[cdepth][x].dls(ndepth,fdepth) for x in range(nchildren) ])
                          
                          

#===================================================================================#
#                           ALGORITHM GAME INTERFACE                                #
#===================================================================================#

                          
@algo_player(name="MitMinder",
             description="Most Promising Children - Queen Navigation")
def mitminder(board_width, board_height, hives, flowers, inflight, crashed,
              lost_volants, received_volants, landed, scores, player_id, game_id, turn_num):

    global mpaths

    # store new hives and recalculate shortest paths (if necessary)
    mpaths.add_hive_from_input(hives)

    mboard = MBoard()
    mboard.game_init(turn_num,board_width,board_height,hives,flowers,inflight,mpaths)
    output_command = mboard.next_move()

    return output_command



@mitminder.on_start_game
def start_game(board_width, board_height, hives, flowers, players, player_id, game_id, game_params):
    global mpaths

    if len(hives) > 0:
        first_hive_pos = hives[0][0]*board_width + hives[0][1]
    else:
        first_hive_pos = None

    # we do not use the add_hives_from_input method to avoid calculating the shortest paths the first time
    mpaths = MPaths(board_width,board_height,first_hive_pos)


@mitminder.on_game_over
def game_over(board_width, board_height, hives, flowers, inflight, crashed,
              lost_volants, received_volants, landed, scores, player_id, game_id, turns):
    pass


#===================================================================================#
#                                GLOBAL DATA (definitions)                          # 
#===================================================================================#

cache  = [[MBoard() for _ in range(max_chilen)] for d in range(dlim)]

#===================================================================================#
#                                PRE-COMPUTED (definitions)                         # 
#===================================================================================#

valid_headings = (0,60,120,180,-120,-60)

# new headings dictionary
new_headings = {0   : [60  , -60 ],\
                60  : [120 , 0   ],\
                120 : [180 , 60  ],\
                180 : [-120, 120 ],\
                -120: [-60 , 180 ],\
                -60 : [0   , -120], }


# opposite headings dictionary
opp_headings = { 0   : 180,\
                 180 :   0,\
                 60  :-120,\
                 -120:  60,\
                 120 : -60,\
                 -60 : 120}

# alternatives for heading given a starting heading
alt_headings = {0   : [0   ,60  , -60 ],\
                60  : [60  ,120 , 0   ],\
                120 : [120 ,180 , 60  ],\
                180 : [180 ,-120, 120 ],\
                -120: [-120,-60 , 180 ],\
                -60 : [-60 ,0   , -120], }

# heading to id
heading_enum = {0   : 0,\
                60  : 1,\
                120 : 2,\
                180 : 3,\
                -120: 4,\
                -60 : 5,}

# id to heading
heading_denum = {0 : 0,\
                 1 : 60,\
                 2 : 120,\
                 3 : 180,\
                 4 : -120,\
                 5 : -60,}

# the new position (given heading and pos)
new_pos = \
{0:(1,2,3,4,5,6,7,-100,9,10,11,12,13,14,15,-100,17,18,19,20,21,22,23,-100,25,26,27,28,29,30,31,-100,33,34,35,36,37,38,39,-100,41,42,43,44,45,46,47,-100,49,50,51,52,53,54,55,-100,57,58,59,60,61,62,63,-100),-120:(-100,-100,-100,-100,-100,-100,-100,-100,-100,0,1,2,3,4,5,6,8,9,10,11,12,13,14,15,-100,16,17,18,19,20,21,22,24,25,26,27,28,29,30,31,-100,32,33,34,35,36,37,38,40,41,42,43,44,45,46,47,-100,48,49,50,51,52,53,54),180:(-100,0,1,2,3,4,5,6,-100,8,9,10,11,12,13,14,-100,16,17,18,19,20,21,22,-100,24,25,26,27,28,29,30,-100,32,33,34,35,36,37,38,-100,40,41,42,43,44,45,46,-100,48,49,50,51,52,53,54,-100,56,57,58,59,60,61,62),120:(8,9,10,11,12,13,14,15,-100,16,17,18,19,20,21,22,24,25,26,27,28,29,30,31,-100,32,33,34,35,36,37,38,40,41,42,43,44,45,46,47,-100,48,49,50,51,52,53,54,56,57,58,59,60,61,62,63,-100,-100,-100,-100,-100,-100,-100,-100),-60:(-100,-100,-100,-100,-100,-100,-100,-100,0,1,2,3,4,5,6,7,9,10,11,12,13,14,15,-100,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,-100,32,33,34,35,36,37,38,39,41,42,43,44,45,46,47,-100,48,49,50,51,52,53,54,55),60:(9,10,11,12,13,14,15,-100,16,17,18,19,20,21,22,23,25,26,27,28,29,30,31,-100,32,33,34,35,36,37,38,39,41,42,43,44,45,46,47,-100,48,49,50,51,52,53,54,55,57,58,59,60,61,62,63,-100,-100,-100,-100,-100,-100,-100,-100,-100)}

# the new position in the opposite direction (given heading and pos)
onew_pos = \
{0:(-1,0,1,2,3,4,5,-100,7,8,9,10,11,12,13,-100,15,16,17,18,19,20,21,-100,23,24,25,26,27,28,29,-100,31,32,33,34,35,36,37,-100,39,40,41,42,43,44,45,-100,47,48,49,50,51,52,53,-100,55,56,57,58,59,60,61,-100),-120:(-100,-100,-100,-100,-100,-100,-100,-100,-100,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,-100,33,34,35,36,37,38,39,41,42,43,44,45,46,47,48,-100,49,50,51,52,53,54,55,57,58,59,60,61,62,63,64,-100,65,66,67,68,69,70,71),180:(-100,2,3,4,5,6,7,8,-100,10,11,12,13,14,15,16,-100,18,19,20,21,22,23,24,-100,26,27,28,29,30,31,32,-100,34,35,36,37,38,39,40,-100,42,43,44,45,46,47,48,-100,50,51,52,53,54,55,56,-100,58,59,60,61,62,63,64),120:(-7,-6,-5,-4,-3,-2,-1,0,-100,1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,-100,17,18,19,20,21,22,23,25,26,27,28,29,30,31,32,-100,33,34,35,36,37,38,39,41,42,43,44,45,46,47,48,-100,-100,-100,-100,-100,-100,-100,-100),-60:(-100,-100,-100,-100,-100,-100,-100,-100,15,16,17,18,19,20,21,22,24,25,26,27,28,29,30,-100,31,32,33,34,35,36,37,38,40,41,42,43,44,45,46,-100,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,-100,63,64,65,66,67,68,69,70),60:(-8,-7,-6,-5,-4,-3,-2,-100,-1,0,1,2,3,4,5,6,8,9,10,11,12,13,14,-100,15,16,17,18,19,20,21,22,24,25,26,27,28,29,30,-100,31,32,33,34,35,36,37,38,40,41,42,43,44,45,46,-100,-100,-100,-100,-100,-100,-100,-100,-100)}

# the positions that can be reached from a given position (given heading and pos)
reach_pos = \
{0:((1,2,3,4,5,6,7),(2,3,4,5,6,7),(3,4,5,6,7),(4,5,6,7),(5,6,7),(6,7),(7,),(),(9,10,11,12,13,14,15),(10,11,12,13,14,15),(11,12,13,14,15),(12,13,14,15),(13,14,15),(14,15),(15,),(),(17,18,19,20,21,22,23),(18,19,20,21,22,23),(19,20,21,22,23),(20,21,22,23),(21,22,23),(22,23),(23,),(),(25,26,27,28,29,30,31),(26,27,28,29,30,31),(27,28,29,30,31),(28,29,30,31),(29,30,31),(30,31),(31,),(),(33,34,35,36,37,38,39),(34,35,36,37,38,39),(35,36,37,38,39),(36,37,38,39),(37,38,39),(38,39),(39,),(),(41,42,43,44,45,46,47),(42,43,44,45,46,47),(43,44,45,46,47),(44,45,46,47),(45,46,47),(46,47),(47,),(),(49,50,51,52,53,54,55),(50,51,52,53,54,55),(51,52,53,54,55),(52,53,54,55),(53,54,55),(54,55),(55,),(),(57,58,59,60,61,62,63),(58,59,60,61,62,63),(59,60,61,62,63),(60,61,62,63),(61,62,63),(62,63),(63,),()),-120:((),(),(),(),(),(),(),(),(),(0,),(1,),(2,),(3,),(4,),(5,),(6,),(8,),(9,0),(10,1),(11,2),(12,3),(13,4),(14,5),(15,6),(),(16,8),(17,9,0),(18,10,1),(19,11,2),(20,12,3),(21,13,4),(22,14,5),(24,),(25,16,8),(26,17,9,0),(27,18,10,1),(28,19,11,2),(29,20,12,3),(30,21,13,4),(31,22,14,5),(),(32,24),(33,25,16,8),(34,26,17,9,0),(35,27,18,10,1),(36,28,19,11,2),(37,29,20,12,3),(38,30,21,13,4),(40,),(41,32,24),(42,33,25,16,8),(43,34,26,17,9,0),(44,35,27,18,10,1),(45,36,28,19,11,2),(46,37,29,20,12,3),(47,38,30,21,13,4),(),(48,40),(49,41,32,24),(50,42,33,25,16,8),(51,43,34,26,17,9,0),(52,44,35,27,18,10,1),(53,45,36,28,19,11,2),(54,46,37,29,20,12,3)),180:((),(0,),(1,0),(2,1,0),(3,2,1,0),(4,3,2,1,0),(5,4,3,2,1,0),(6,5,4,3,2,1,0),(),(8,),(9,8),(10,9,8),(11,10,9,8),(12,11,10,9,8),(13,12,11,10,9,8),(14,13,12,11,10,9,8),(),(16,),(17,16),(18,17,16),(19,18,17,16),(20,19,18,17,16),(21,20,19,18,17,16),(22,21,20,19,18,17,16),(),(24,),(25,24),(26,25,24),(27,26,25,24),(28,27,26,25,24),(29,28,27,26,25,24),(30,29,28,27,26,25,24),(),(32,),(33,32),(34,33,32),(35,34,33,32),(36,35,34,33,32),(37,36,35,34,33,32),(38,37,36,35,34,33,32),(),(40,),(41,40),(42,41,40),(43,42,41,40),(44,43,42,41,40),(45,44,43,42,41,40),(46,45,44,43,42,41,40),(),(48,),(49,48),(50,49,48),(51,50,49,48),(52,51,50,49,48),(53,52,51,50,49,48),(54,53,52,51,50,49,48),(),(56,),(57,56),(58,57,56),(59,58,57,56),(60,59,58,57,56),(61,60,59,58,57,56),(62,61,60,59,58,57,56)),120:((8,),(9,16,24),(10,17,25,32,40),(11,18,26,33,41,48,56),(12,19,27,34,42,49,57),(13,20,28,35,43,50,58),(14,21,29,36,44,51,59),(15,22,30,37,45,52,60),(),(16,24),(17,25,32,40),(18,26,33,41,48,56),(19,27,34,42,49,57),(20,28,35,43,50,58),(21,29,36,44,51,59),(22,30,37,45,52,60),(24,),(25,32,40),(26,33,41,48,56),(27,34,42,49,57),(28,35,43,50,58),(29,36,44,51,59),(30,37,45,52,60),(31,38,46,53,61),(),(32,40),(33,41,48,56),(34,42,49,57),(35,43,50,58),(36,44,51,59),(37,45,52,60),(38,46,53,61),(40,),(41,48,56),(42,49,57),(43,50,58),(44,51,59),(45,52,60),(46,53,61),(47,54,62),(),(48,56),(49,57),(50,58),(51,59),(52,60),(53,61),(54,62),(56,),(57,),(58,),(59,),(60,),(61,),(62,),(63,),(),(),(),(),(),(),(),()),-60:((),(),(),(),(),(),(),(),(0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(9,1),(10,2),(11,3),(12,4),(13,5),(14,6),(15,7),(),(16,9,1),(17,10,2),(18,11,3),(19,12,4),(20,13,5),(21,14,6),(22,15,7),(23,),(25,17,10,2),(26,18,11,3),(27,19,12,4),(28,20,13,5),(29,21,14,6),(30,22,15,7),(31,23),(),(32,25,17,10,2),(33,26,18,11,3),(34,27,19,12,4),(35,28,20,13,5),(36,29,21,14,6),(37,30,22,15,7),(38,31,23),(39,),(41,33,26,18,11,3),(42,34,27,19,12,4),(43,35,28,20,13,5),(44,36,29,21,14,6),(45,37,30,22,15,7),(46,38,31,23),(47,39),(),(48,41,33,26,18,11,3),(49,42,34,27,19,12,4),(50,43,35,28,20,13,5),(51,44,36,29,21,14,6),(52,45,37,30,22,15,7),(53,46,38,31,23),(54,47,39),(55,)),60:((9,17,26,34,43,51,60),(10,18,27,35,44,52,61),(11,19,28,36,45,53,62),(12,20,29,37,46,54,63),(13,21,30,38,47,55),(14,22,31,39),(15,23),(),(16,25,33,42,50,59),(17,26,34,43,51,60),(18,27,35,44,52,61),(19,28,36,45,53,62),(20,29,37,46,54,63),(21,30,38,47,55),(22,31,39),(23,),(25,33,42,50,59),(26,34,43,51,60),(27,35,44,52,61),(28,36,45,53,62),(29,37,46,54,63),(30,38,47,55),(31,39),(),(32,41,49,58),(33,42,50,59),(34,43,51,60),(35,44,52,61),(36,45,53,62),(37,46,54,63),(38,47,55),(39,),(41,49,58),(42,50,59),(43,51,60),(44,52,61),(45,53,62),(46,54,63),(47,55),(),(48,57),(49,58),(50,59),(51,60),(52,61),(53,62),(54,63),(55,),(57,),(58,),(59,),(60,),(61,),(62,),(63,),(),(),(),(),(),(),(),(),())}

# priority of each tile for hive creation
# original min hive
priority = \
((64,128,6,64,64,4,64,64,64,0,192,128,13,128,128,3,128,192,13,192,192,13,128,64,64,8,128,192,13,192,128,7,128,192,13,192,192,13,128,64,64,10,128,192,13,192,128,9,128,192,13,128,128,13,128,64,64,2,64,64,5,64,64,1),(7,64,64,5,64,64,10,64,64,128,13,128,128,13,192,128,1,128,192,13,192,128,2,64,64,128,13,192,192,13,192,128,8,128,192,13,192,128,9,64,64,128,13,192,192,13,192,128,3,128,128,13,128,192,0,64,64,64,6,64,64,4,128,64),(64,3,64,64,5,64,64,13,13,64,128,10,128,128,0,64,64,6,192,192,13,192,128,13,13,128,192,13,192,192,7,64,64,8,192,192,13,192,128,13,13,128,192,13,192,192,9,64,64,1,128,128,13,128,128,13,13,64,64,4,64,64,2,64))
#original
#((1,2,0,1,1,0,1,1,1,0,3,2,0,2,2,0,2,3,0,3,3,0,2,1,1,0,2,3,0,3,2,0,2,3,0,3,3,0,2,1,1,0,2,3,0,3,2,0,2,3,0,2,2,0,2,1,1,0,1,1,0,1,1,0),(0,1,1,0,1,1,0,1,1,2,0,2,2,0,3,2,0,2,3,0,3,2,0,1,1,2,0,3,3,0,3,2,0,2,3,0,3,2,0,1,1,2,0,3,3,0,3,2,0,2,2,0,2,3,0,1,1,1,0,1,1,0,2,1),(1,0,1,1,0,1,1,0,0,1,2,0,2,2,0,1,1,0,3,3,0,3,2,0,0,2,3,0,3,3,0,1,1,0,3,3,0,3,2,0,0,2,3,0,3,3,0,1,1,0,2,2,0,2,2,0,0,1,1,0,1,1,0,1))

# the game that we will play based on first hive position
game_pos = \
(1,2,0,1,2,0,1,2,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,2,0,1,2,0,1,2,0)

# path_crosses[heading][pos] returns a tuple of positions that a volant will pass from, if it does not change its direction
# the initial pos is included
path_crosses = \
{0:((0,1,2,3,4,5,6,7),(1,2,3,4,5,6,7),(2,3,4,5,6,7),(3,4,5,6,7),(4,5,6,7),(5,6,7),(6,7),(7,),(8,9,10,11,12,13,14,15),(9,10,11,12,13,14,15),(10,11,12,13,14,15),(11,12,13,14,15),(12,13,14,15),(13,14,15),(14,15),(15,),(16,17,18,19,20,21,22,23),(17,18,19,20,21,22,23),(18,19,20,21,22,23),(19,20,21,22,23),(20,21,22,23),(21,22,23),(22,23),(23,),(24,25,26,27,28,29,30,31),(25,26,27,28,29,30,31),(26,27,28,29,30,31),(27,28,29,30,31),(28,29,30,31),(29,30,31),(30,31),(31,),(32,33,34,35,36,37,38,39),(33,34,35,36,37,38,39),(34,35,36,37,38,39),(35,36,37,38,39),(36,37,38,39),(37,38,39),(38,39),(39,),(40,41,42,43,44,45,46,47),(41,42,43,44,45,46,47),(42,43,44,45,46,47),(43,44,45,46,47),(44,45,46,47),(45,46,47),(46,47),(47,),(48,49,50,51,52,53,54,55),(49,50,51,52,53,54,55),(50,51,52,53,54,55),(51,52,53,54,55),(52,53,54,55),(53,54,55),(54,55),(55,),(56,57,58,59,60,61,62,63),(57,58,59,60,61,62,63),(58,59,60,61,62,63),(59,60,61,62,63),(60,61,62,63),(61,62,63),(62,63),(63,)),-120:((0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(8,),(9,0),(10,1),(11,2),(12,3),(13,4),(14,5),(15,6),(16,8),(17,9,0),(18,10,1),(19,11,2),(20,12,3),(21,13,4),(22,14,5),(23,15,6),(24,),(25,16,8),(26,17,9,0),(27,18,10,1),(28,19,11,2),(29,20,12,3),(30,21,13,4),(31,22,14,5),(32,24),(33,25,16,8),(34,26,17,9,0),(35,27,18,10,1),(36,28,19,11,2),(37,29,20,12,3),(38,30,21,13,4),(39,31,22,14,5),(40,),(41,32,24),(42,33,25,16,8),(43,34,26,17,9,0),(44,35,27,18,10,1),(45,36,28,19,11,2),(46,37,29,20,12,3),(47,38,30,21,13,4),(48,40),(49,41,32,24),(50,42,33,25,16,8),(51,43,34,26,17,9,0),(52,44,35,27,18,10,1),(53,45,36,28,19,11,2),(54,46,37,29,20,12,3),(55,47,38,30,21,13,4),(56,),(57,48,40),(58,49,41,32,24),(59,50,42,33,25,16,8),(60,51,43,34,26,17,9,0),(61,52,44,35,27,18,10,1),(62,53,45,36,28,19,11,2),(63,54,46,37,29,20,12,3)),180:((0,),(1,0),(2,1,0),(3,2,1,0),(4,3,2,1,0),(5,4,3,2,1,0),(6,5,4,3,2,1,0),(7,6,5,4,3,2,1,0),(8,),(9,8),(10,9,8),(11,10,9,8),(12,11,10,9,8),(13,12,11,10,9,8),(14,13,12,11,10,9,8),(15,14,13,12,11,10,9,8),(16,),(17,16),(18,17,16),(19,18,17,16),(20,19,18,17,16),(21,20,19,18,17,16),(22,21,20,19,18,17,16),(23,22,21,20,19,18,17,16),(24,),(25,24),(26,25,24),(27,26,25,24),(28,27,26,25,24),(29,28,27,26,25,24),(30,29,28,27,26,25,24),(31,30,29,28,27,26,25,24),(32,),(33,32),(34,33,32),(35,34,33,32),(36,35,34,33,32),(37,36,35,34,33,32),(38,37,36,35,34,33,32),(39,38,37,36,35,34,33,32),(40,),(41,40),(42,41,40),(43,42,41,40),(44,43,42,41,40),(45,44,43,42,41,40),(46,45,44,43,42,41,40),(47,46,45,44,43,42,41,40),(48,),(49,48),(50,49,48),(51,50,49,48),(52,51,50,49,48),(53,52,51,50,49,48),(54,53,52,51,50,49,48),(55,54,53,52,51,50,49,48),(56,),(57,56),(58,57,56),(59,58,57,56),(60,59,58,57,56),(61,60,59,58,57,56),(62,61,60,59,58,57,56),(63,62,61,60,59,58,57,56)),120:((0,8),(1,9,16,24),(2,10,17,25,32,40),(3,11,18,26,33,41,48,56),(4,12,19,27,34,42,49,57),(5,13,20,28,35,43,50,58),(6,14,21,29,36,44,51,59),(7,15,22,30,37,45,52,60),(8,),(9,16,24),(10,17,25,32,40),(11,18,26,33,41,48,56),(12,19,27,34,42,49,57),(13,20,28,35,43,50,58),(14,21,29,36,44,51,59),(15,22,30,37,45,52,60),(16,24),(17,25,32,40),(18,26,33,41,48,56),(19,27,34,42,49,57),(20,28,35,43,50,58),(21,29,36,44,51,59),(22,30,37,45,52,60),(23,31,38,46,53,61),(24,),(25,32,40),(26,33,41,48,56),(27,34,42,49,57),(28,35,43,50,58),(29,36,44,51,59),(30,37,45,52,60),(31,38,46,53,61),(32,40),(33,41,48,56),(34,42,49,57),(35,43,50,58),(36,44,51,59),(37,45,52,60),(38,46,53,61),(39,47,54,62),(40,),(41,48,56),(42,49,57),(43,50,58),(44,51,59),(45,52,60),(46,53,61),(47,54,62),(48,56),(49,57),(50,58),(51,59),(52,60),(53,61),(54,62),(55,63),(56,),(57,),(58,),(59,),(60,),(61,),(62,),(63,)),-60:((0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(8,0),(9,1),(10,2),(11,3),(12,4),(13,5),(14,6),(15,7),(16,9,1),(17,10,2),(18,11,3),(19,12,4),(20,13,5),(21,14,6),(22,15,7),(23,),(24,16,9,1),(25,17,10,2),(26,18,11,3),(27,19,12,4),(28,20,13,5),(29,21,14,6),(30,22,15,7),(31,23),(32,25,17,10,2),(33,26,18,11,3),(34,27,19,12,4),(35,28,20,13,5),(36,29,21,14,6),(37,30,22,15,7),(38,31,23),(39,),(40,32,25,17,10,2),(41,33,26,18,11,3),(42,34,27,19,12,4),(43,35,28,20,13,5),(44,36,29,21,14,6),(45,37,30,22,15,7),(46,38,31,23),(47,39),(48,41,33,26,18,11,3),(49,42,34,27,19,12,4),(50,43,35,28,20,13,5),(51,44,36,29,21,14,6),(52,45,37,30,22,15,7),(53,46,38,31,23),(54,47,39),(55,),(56,48,41,33,26,18,11,3),(57,49,42,34,27,19,12,4),(58,50,43,35,28,20,13,5),(59,51,44,36,29,21,14,6),(60,52,45,37,30,22,15,7),(61,53,46,38,31,23),(62,54,47,39),(63,55)),60:((0,9,17,26,34,43,51,60),(1,10,18,27,35,44,52,61),(2,11,19,28,36,45,53,62),(3,12,20,29,37,46,54,63),(4,13,21,30,38,47,55),(5,14,22,31,39),(6,15,23),(7,),(8,16,25,33,42,50,59),(9,17,26,34,43,51,60),(10,18,27,35,44,52,61),(11,19,28,36,45,53,62),(12,20,29,37,46,54,63),(13,21,30,38,47,55),(14,22,31,39),(15,23),(16,25,33,42,50,59),(17,26,34,43,51,60),(18,27,35,44,52,61),(19,28,36,45,53,62),(20,29,37,46,54,63),(21,30,38,47,55),(22,31,39),(23,),(24,32,41,49,58),(25,33,42,50,59),(26,34,43,51,60),(27,35,44,52,61),(28,36,45,53,62),(29,37,46,54,63),(30,38,47,55),(31,39),(32,41,49,58),(33,42,50,59),(34,43,51,60),(35,44,52,61),(36,45,53,62),(37,46,54,63),(38,47,55),(39,),(40,48,57),(41,49,58),(42,50,59),(43,51,60),(44,52,61),(45,53,62),(46,54,63),(47,55),(48,57),(49,58),(50,59),(51,60),(52,61),(53,62),(54,63),(55,),(56,),(57,),(58,),(59,),(60,),(61,),(62,),(63,))}

