from algos.MitMinder import new_pos, valid_headings

def main():

    board_pos = 64
 
    all_crosses = dict()

    for heading in valid_headings:
        all_crosses[heading] = [ [i] for i in range(board_pos) ]

    for heading in valid_headings:
        for pos in range(board_pos):
            the_new_pos = new_pos[heading][pos]
            while 0<= the_new_pos < board_pos:
                all_crosses[heading][pos].append( the_new_pos )
                the_new_pos = new_pos[heading][the_new_pos]
            all_crosses[heading][pos] = tuple(all_crosses[heading][pos])
        all_crosses[heading] = tuple(all_crosses[heading])

    print(all_crosses)

if __name__ == '__main__':
    main()
  
