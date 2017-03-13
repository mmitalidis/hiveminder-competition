# Explanation of the hiveminder player MitMinder.

The strategy to play this game is divided into two parts.

First, if there is no queen bee on the board, the player searches the game tree for an optimal move. In order to prune parts of the tree, a heuristic method is used. On the other hand, if there is a queen bee on the board, then the player will lead this queen bee to the position that is considered optimal.

## Bee Navigation

The bee strategy is to search the game state tree and find the optimal next move. For every state it evaluates, the algorithm expands only a constant number of children nodes, namely the ones with the highest static evaluation. In an effort to achieve the best solution, given the time limit, the Iterative Deepening Depth first search algorithm is used. Thus, we compute a solution, and constantly improve it, until we ran out of time. Finally, the static evaluation function takes into account the score of the state, the nectar that is carried and the direction of the bees. The final score is a weighed sum of the above, where the coefficients were determined experimentally.

## Queen Bee Navigation

An important element of the game, that is affected by the queen bees, is the position of the hives. In an effort to achive optimal hive placement, we use the following procedure. First, we assign a priority to each position of the board. This priority is used from the queen bees, in order to decide where to place the hive. In other words, a queen bee will choose to go to the position with the highest priority and create a hive there. If these positions are more than one, it goes to the nearest one. When, it reaches this position, it creates a new hive.

In order to achieve the navigation to the highest priority position, we define a graph G, where each node of the graph corresponds to an (x,y,heading) combination. Then, given the nodes i and j we say that:

- A[i,j] = 1 iff we can go from node i to node j, without changing our heading, 
- A[i,j] = 2 iff we can go from node i to node j, but a change of heading is necessary, 
- A[i,j] = 9 if we cannot directly go from node i to node j. 

A is the adjacency matrix of G. Every time a new hive is added, we use the Dijkstra algorithm to find all the shortest paths.
