from algos.MitMinder import new_pos, valid_headings

def main():
 
    all_crosses = dict()

    for heading in valid_headings:
        all_crosses[heading] = [ [i] for i in range(64) ]

    for heading in valid_headings:
        for pos in range(64):
            the_new_pos = new_pos[heading][pos]
            while 0<= the_new_pos <64:
                all_crosses[heading][pos].append( the_new_pos )
                the_new_pos = new_pos[heading][the_new_pos]
            all_crosses[heading][pos] = tuple(all_crosses[heading][pos])
        all_crosses[heading] = tuple(all_crosses[heading])

    print(all_crosses)

if __name__ == '__main__':
    main()
  
