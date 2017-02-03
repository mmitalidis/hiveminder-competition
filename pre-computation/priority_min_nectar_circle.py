from copy import deepcopy

game_1_blue = [ [1,1], [3,1], [5,1], [7,1], \
                [0,2], [2,2], [4,2], [6,2], \
                [1,4], [3,4], [5,4], [7,4], \
                [0,5], [2,5], [4,5], [6,5], \
                [1,7], [3,7], [5,7], [7,7] ]

game_1_orange = [ [0,0], [1,0], \
                  [5,0], [7,0], \
                  [7,2], [7,3], [7,5], [7,6], \
                  [6,7], [4,7], [2,7], [0,7], \
                  [0,6], [0,4], [0,3], [3,0]  ]

game_1_green = [ [0,1], [3,2],  \
                 [5,2], [6,3], [6,4], \
                 [6,6], [5,6], [4,6], [3,6], \
                 [2,6], [1,6], [1,5], [1,3], \
                 [2,0], [4,0], [6,0] ]

game_1_red = [ [1,2], [2,3], [3,3], [4,3], [5,3], \
               [5,5], [4,4], [3,5], [2,4], [2,1], [4,1], [6,1] ]


game_2_blue = [ [0,0], [2,0], [4,0], [6,0], \
                [1,2], [3,2], [5,2], [7,2], \
                [0,3], [2,3], [4,3], [6,3], \
                [1,5], [3,5], [5,5], [7,5], \
                [0,6], [2,6], [4,6], [6,6] ]

game_2_orange = [ [1,0], [3,0], [5,0], [7,0], \
                  [7,1], [7,3], [7,4], \
                  [7,7], [6,7], [4,7], \
                  [2,7], [0,7], \
                  [0,5], [0,4], [0,2], [0,1] ]

game_2_green = [ [1,1], [2,1], [3,1], [4,1], \
                 [5,1], [6,1], [6,2], [6,4], \
                 [4,5], [7,6], \
                 [2,5], [1,4], [1,3], \
                 [1,7], [5,7], [3,7] ]

game_2_red = [ [2,2], [3,3], [4,2], [5,3], \
               [5,4], [4,4], [3,4], [2,4], \
               [1,6], [3,6], [5,6], [6,5] ]

game_3_blue = [ [1,0], [3,0], [5,0], [7,0], \
                [0,1], [2,1], [4,1], [6,1], \
                [1,3], [3,3], [5,3], [7,3], \
                [0,4], [2,4], [4,4], [6,4], \
                [1,6], [3,6], [5,6], [7,6], \
                [0,7], [2,7], [4,7], [6,7] ]

game_3_orange = [ [0,0], [1,1], [2,0], [4,0], [6,0], \
                  [7,1], [7,2], [7,4], [7,5], \
                  [7,7], [5,7], [3,7], [1,7], \
                  [0,6], [0,5], [0,3], [0,2] ]

game_3_green = [ [1,2], [3,1], [5,1], [6,2], \
                 [6,3], [6,5], [6,6], [4,6], \
                 [2,6], [1,5], [1,4] ]

game_3_red = [ [2,2], [3,2], [4,2], [5,2], \
               [2,3], [3,4], [4,3], [5,4], \
               [5,5], [4,5], [3,5], [2,5] ]

game_1_bluep   = [x[0]*8 + x[1] for x in game_1_blue]
game_1_orangep = [x[0]*8 + x[1] for x in game_1_orange]
game_1_greenp  = [x[0]*8 + x[1] for x in game_1_green]
game_1_redp    = [x[0]*8 + x[1] for x in game_1_red]
game_1p = game_1_bluep + game_1_orangep + game_1_greenp + game_1_redp

game_2_bluep   = [x[0]*8 + x[1] for x in game_2_blue]
game_2_orangep = [x[0]*8 + x[1] for x in game_2_orange]
game_2_greenp  = [x[0]*8 + x[1] for x in game_2_green]
game_2_redp    = [x[0]*8 + x[1] for x in game_2_red]
game_2p = game_2_bluep + game_2_orangep + game_2_greenp + game_2_redp

game_3_bluep   = [x[0]*8 + x[1] for x in game_3_blue]
game_3_orangep = [x[0]*8 + x[1] for x in game_3_orange]
game_3_greenp  = [x[0]*8 + x[1] for x in game_3_green]
game_3_redp    = [x[0]*8 + x[1] for x in game_3_red]
game_3p = game_3_bluep + game_3_orangep + game_3_greenp + game_3_redp


games_bluep   = [game_1_bluep  , game_2_bluep  , game_3_bluep  ]
games_orangep = [game_1_orangep, game_2_orangep, game_3_orangep]
games_greenp  = [game_1_greenp , game_2_greenp , game_3_greenp ]
games_redp    = [game_1_redp   , game_2_redp   , game_3_redp   ]


def main():
    game_1p_tmp = deepcopy(game_1p)
    game_2p_tmp = deepcopy(game_2p)
    game_3p_tmp = deepcopy(game_3p)
    assert( tuple(set(sorted(game_1p_tmp))) == tuple(list(range(64))) )
    assert( tuple(set(sorted(game_2p_tmp))) == tuple(list(range(64))) )
    assert( tuple(set(sorted(game_3p_tmp))) == tuple(list(range(64))) )

    priority = [ [-1 for pos in range(64)] for _ in range(3) ]

    def xyp(xy):
        return xy[0]*8 + xy[1]

    secondary = {0: [13 for i in range(64)], \
                 1: [13 for i in range(64)], \
                 2: [13 for i in range(64)] }

    secondary[0][xyp( (1,1) )] = 0
    secondary[0][xyp( (7,7) )] = 1
    secondary[0][xyp( (7,1) )] = 2
    secondary[0][xyp( (1,7) )] = 3
    secondary[0][xyp( (0,5) )] = 4
    secondary[0][xyp( (7,4) )] = 5
    secondary[0][xyp( (0,2) )] = 6
    secondary[0][xyp( (3,7) )] = 7
    secondary[0][xyp( (3,1) )] = 8
    secondary[0][xyp( (5,7) )] = 9
    secondary[0][xyp( (5,1) )] = 10

    secondary[1][xyp( (6,6) )] = 0
    secondary[1][xyp( (2,0) )] = 1
    secondary[1][xyp( (2,6) )] = 2
    secondary[1][xyp( (6,0) )] = 3
    secondary[1][xyp( (7,5) )] = 4
    secondary[1][xyp( (0,3) )] = 5
    secondary[1][xyp( (7,2) )] = 6
    secondary[1][xyp( (0,0) )] = 7
    secondary[1][xyp( (4,0) )] = 8
    secondary[1][xyp( (4,6) )] = 9
    secondary[1][xyp( (0,6) )] = 10

    secondary[2][xyp( (1,6) )] = 0
    secondary[2][xyp( (6,1) )] = 1
    secondary[2][xyp( (7,6) )] = 2
    secondary[2][xyp( (0,1) )] = 3
    secondary[2][xyp( (7,3) )] = 4
    secondary[2][xyp( (0,4) )] = 5
    secondary[2][xyp( (2,1) )] = 6
    secondary[2][xyp( (3,6) )] = 7
    secondary[2][xyp( (4,1) )] = 8
    secondary[2][xyp( (5,6) )] = 9
    secondary[2][xyp( (1,3) )] = 10

    for game in range(3):
        for pos in range(64):
            if pos in games_bluep[game]:
                priority[game][pos] = 0 + secondary[game][pos]
            elif pos in games_orangep[game]:
                priority[game][pos] = 1*64
            elif pos in games_greenp[game]:
                priority[game][pos] = 2*64
            elif pos in games_redp[game]:
                priority[game][pos] = 3*64
            else:
                raise RuntimeError("Could not find %d on game %d" % (pos,game))
        priority[game] = tuple(priority[game])
    priority = tuple(priority)


    for game in range(3):
        assert(-1 not in priority[game])

    print(priority)
    print('')


    # game that we play
    pos_game = []
    for pos in range(64):
        if pos in game_1_bluep:       
            pos_game.append(0)
        elif pos in game_2_bluep:
            pos_game.append(1)
        elif pos in game_3_bluep:
            pos_game.append(2)
        else:
            raise RuntimeError("Could not find %d on game %d" % (pos,game))
    pos_game = tuple(pos_game)

    print(pos_game)
    
        


if __name__ == '__main__':
    main()

