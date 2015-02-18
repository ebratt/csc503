from sys import argv, exit
import re
 
# open the file and get read to read data
file = open(argv[1], "r");
p = re.compile("\d+");

# initialize the graph
vertices, edges = map(int, p.findall(file.readline()))
graph = [[None]*vertices for _ in range(vertices)]

for i in range(edges):
    u, v, weight = map(int, p.findall(file.readline()))
    graph[u][v] = weight
    graph[v][u] = weight

# initialize the MST and the set X
T = set();
X = set();
 
# select an arbitrary vertex to begin with
X.add(0);
 
while len(X) != vertices:
    crossing = set();
    # for each element x in X, add the edge (x, k) to crossing if
    # k is not in X
    edge = d = None
    for x in X:
        for k in range(vertices):
            if k not in X:
                link = graph[x][k]
                if link is not None:
                    if d==None or link<d:
                        edge, d = (x,k), link
                        
    # add this edge to T
    T.add(edge)
    # add the new vertex to X
    X.add(edge[1])
 
# print the edges of the MST
for edge in T:
    print edge
