import networkx as nx
import random

random.seed(67)


chrs = ['t', 's']
def gen_call(n, outgoing):
    s = f"""
bool f{n}(int fuel1, int fuel2, char* choices) {{
    switch (*choices) {{
"""
    for k,o in enumerate(outgoing):
        f1 = o[2] - random.randint(1,o[2]-1)
        f2 = o[2] - f1

        s += f"""
        case '{chrs[k]}':
            return f{o[1]}(fuel2 - {f1}, fuel2 - {f2}, choices + 1);
        """
    s += """
        default:
            return false;
    }
}
    """
    return s
    

# build graph
G = nx.random_k_out_graph(1000, 2, 50, self_loops=False,seed=66)
for u,v,k in G.edges(keys=True):
    G.edges[u,v,k]['weight'] = random.randint(2,50)

length, path = nx.single_source_dijkstra(G, 0)

for n in range(1000):
    print(f"bool f{n}(int, int, char*);")
for n in G.nodes():
    print(gen_call(n, (G.out_edges([n], data='weight'))))


print(path[882], length[882])
