from hiveminder.volant import Volant

board_width = 8
board_height = 8
board_pos = board_width * board_height

def xy_to_pos(x,y):
    global board_width
    return board_width*x+y

out0    = tuple( (x,board_height-1) for x in range(board_width) )
out180  = tuple( (x,0) for x in range(board_width) )
out60   = ((0,7), (2,7), (4,7), (6,7), (7,7), (7,6), (7,5), (7,4), (7,3), (7,2), (7,1), (7,0))
out_60  = ((6,7), (4,7), (2,7), (0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0))
out120  = ((1,0), (3,0), (5,0), (7,0), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7))
out_120 = ((0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0), (1,0), (3,0), (5,0), (7,0))

out0_8    = ((0,7), (1,7), (2,7), (3,7), (4,7), (5,7), (6,7), (7,7))
out180_8  = ((0,0), (1,0), (2,0), (3,0), (4,0), (5,0), (6,0), (7,0))
out60_8   = ((0,7), (2,7), (4,7), (6,7), (7,7), (7,6), (7,5), (7,4), (7,3), (7,2), (7,1), (7,0))
out_60_8  = ((6,7), (4,7), (2,7), (0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0))
out120_8  = ((1,0), (3,0), (5,0), (7,0), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7))
out_120_8 = ((0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0), (1,0), (3,0), (5,0), (7,0))

reverse = {0:180, 180:0, 60:-120, -120:60, -60:120, 120:-60}

out = dict()
out[0]    = tuple( x*board_width+y for (x,y) in out0 )
out[180]  = tuple( x*board_width+y for (x,y) in out180 )
out[60]   = tuple( x*board_width+y for (x,y) in out60 )
out[-60]  = tuple( x*board_width+y for (x,y) in out_60 )
out[-120] = tuple( x*board_width+y for (x,y) in out_120 )
out[120]  = tuple( x*board_width+y for (x,y) in out120 )

def main():
    global out
    global board_width
    global board_heigt
    global board_pos
    if board_width == board_height == 8:
        assert out0 == out0_8
        assert out180 == out180_8
        assert out60  == out60_8
        assert out_60 == out_60_8
        assert out120 == out120_8
        assert out_120 == out_120_8

    #print(out)
    #print('---------')
    headings = (0,60,120,180,-120,-60)
    nnew_pos = dict()
    for heading in headings:
        pos_to_add = []
        for pos in range(board_pos):
            x = pos // board_width
            y = pos - x * board_width

            v = Volant(x,y,heading)
            va = v.advance()

            #if pos not in out[heading]:
            if not (va.x < 0 or va.x >= board_height or va.y < 0 or va.y >= board_height):
                pos_to_add.append(xy_to_pos(va.x,va.y))
            else:
                pos_to_add.append(-100)
        nnew_pos[heading] = pos_to_add
    
    onnew_pos = dict()
    for heading in headings:
        pos_to_add = []
        for pos in range(board_pos):
            x = pos // board_width
            y = pos - x * board_width

            v = Volant(x,y,heading)
            va = v.advance(reverse=True)

            #if pos not in out[heading]:
            #if pos not in out[reverse[heading]]:
            if not (va.x < 0 or va.x >= board_height or va.y < 0 or va.y >= board_height):
                #print('%d,%d' % (va.x,v.y))
                pos_to_add.append(xy_to_pos(va.x,va.y))
            else:
                pos_to_add.append(-100)
        onnew_pos[heading] = pos_to_add

    for heading in headings:
        nnew_pos[heading] = tuple(nnew_pos[heading])
        onnew_pos[heading] = tuple(onnew_pos[heading])

    print(nnew_pos)
    print(onnew_pos)

    
if __name__ == '__main__':
    main()
