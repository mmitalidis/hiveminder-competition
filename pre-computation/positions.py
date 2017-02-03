from hiveminder.volant import Volant
#from algos.algo5 import new_pos, onew_pos

def xy_to_pos(x,y):
    return 8*x+y

out0    = ((0,7), (1,7), (2,7), (3,7), (4,7), (5,7), (6,7), (7,7))
out180  = ((0,0), (1,0), (2,0), (3,0), (4,0), (5,0), (6,0), (7,0))
out60   = ((0,7), (2,7), (4,7), (6,7), (7,7), (7,6), (7,5), (7,4), (7,3), (7,2), (7,1), (7,0))
out_60  = ((6,7), (4,7), (2,7), (0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0))
out120  = ((1,0), (3,0), (5,0), (7,0), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7))
out_120 = ((0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0), (1,0), (3,0), (5,0), (7,0))

out = dict()
out[0]    = tuple( x*8+y for (x,y) in out0 )
out[180]  = tuple( x*8+y for (x,y) in out180 )
out[60]   = tuple( x*8+y for (x,y) in out60 )
out[-60]  = tuple( x*8+y for (x,y) in out_60 )
out[-120] = tuple( x*8+y for (x,y) in out_120 )
out[120]  = tuple( x*8+y for (x,y) in out120 )

def main():
    global out
    #print(out)
    #print('---------')
    headings = (0,60,120,180,-120,-60)
    nnew_pos = dict()
    for heading in headings:
        pos_to_add = []
        for pos in range(64):
            x = pos // 8
            y = pos - x * 8
            if pos not in out[heading]:
                v = Volant(x,y,heading)
                va = v.advance()
                pos_to_add.append(xy_to_pos(va.x,va.y))
            else:
                pos_to_add.append(-100)
        nnew_pos[heading] = pos_to_add
    
    onnew_pos = dict()
    for heading in headings:
        pos_to_add = []
        for pos in range(64):
            x = pos // 8
            y = pos - x * 8
            if pos not in out[heading]:
                v = Volant(x,y,heading)
                va = v.advance(reverse=True)
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

    
    """
    for i,v in nnew_pos.items():
        for j in range(len(v)):
            assert nnew_pos[i][j] == new_pos[i][j]
    for i,v in onnew_pos.items():
        for j in range(len(v)):
            assert onnew_pos[i][j] == onew_pos[i][j]
    """

if __name__ == '__main__':
    main()
