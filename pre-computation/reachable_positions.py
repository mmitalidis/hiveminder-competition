from algos.MitMinder import new_pos

def main():
    headings = (0,60,120,180,-120,-60)
    reach_pos = dict()

    for heading in headings:
        reach_pos[heading] = []
        for pos in range(64):
            reach_pos[heading].append([])
            # add positions to reach_pos[heading][pos]
            current_pos = new_pos[heading][pos]
            while 0<= current_pos < 64:
                reach_pos[heading][pos].append(current_pos)
                current_pos = new_pos[heading][current_pos]

        # start converting to tuples
        for pos in range(64):
            reach_pos[heading][pos] = tuple(reach_pos[heading][pos])
        reach_pos[heading] = tuple(reach_pos[heading])

    print(reach_pos)



if __name__ == '__main__':
    main()
