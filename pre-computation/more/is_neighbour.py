from algos.MitMinder import new_pos

def main():
    headings = (0,60,120,180,-60,-120)
    is_neighbour = [ [False for pos_i in range(64)] for pos_j in range(64) ]

    for pos_i in range(64):
        for heading in headings:
            pos_j = new_pos[heading][pos_i]
            if 0<= pos_j < 64:
                is_neighbour[pos_i][pos_j] = True

        is_neighbour[pos_i] = tuple(is_neighbour[pos_i])
    is_neighbour = tuple(is_neighbour)
            
    print(is_neighbour)



if __name__ == '__main__':
    main()
