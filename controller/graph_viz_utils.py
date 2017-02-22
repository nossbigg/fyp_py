import collections
import json

import matplotlib.pyplot as plt
import networkx as nx


def get_d3_data_format(G):
    # ref: http://bl.ocks.org/mbostock/4062045
    nodes = []
    for node in G.nodes():
        d = {}
        d['id'] = node
        d['group'] = 1
        nodes.append(d)

    edges = []
    for edge in G.edges():
        d = {}
        d['source'] = edge[0]
        d['target'] = edge[1]
        d['value'] = 1
        edges.append(d)

    return_dict = {}
    return_dict["nodes"] = nodes
    return_dict["links"] = edges

    return json.dumps(return_dict, indent=2)


def gen_plt_degree_dist(G):
    # https://networkx.github.io/documentation/development/examples/drawing/degree_histogram.html

    degree_sequence = sorted(nx.degree(G).values(), reverse=True)  # degree sequence

    # print "Degree sequence", degree_sequence
    degree_count = collections.Counter(degree_sequence)
    deg, cnt = zip(*degree_count.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')

    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d + 0.4 for d in deg])
    ax.set_xticklabels(deg)

    plt.show()
