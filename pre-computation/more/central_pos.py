
def main():
    pos_xy = ((3,5), (4,4), (5,5), (3,4), (4,3), (5,4), (3,3), (4,2), (5,3))
    pos = []
    for xy in pos_xy:
        pos.append( xy[0]*8 + xy[1] )
    pos = tuple(pos)

    print(pos)

    
    

if __name__ == '__main__':
    main()
