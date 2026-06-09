import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
# from config.config import OUTPUT_DIR
# from build_graph import execute as build_graph
from graph.build_graph import execute as build_graph
import sys 
import os 
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_DIR, ROOT_DIR
print(OUTPUT_DIR)
print(ROOT_DIR)

def load_graph(graph_json_path):

    with open(
        graph_json_path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    G = nx.Graph()

    # ------------------
    # Nodes
    # ------------------

    for node in data["nodes"]:

        G.add_node(
            node["id"],
            label=node.get(
                "label",
                node["id"]
            )
        )

    # ------------------
    # Edges
    # ------------------

    for edge in data["edges"]:

        similarities = edge.get(
            "similarities",
            {}
        )
        
        similarities = edge.get(
            "similarities",
            {}
        )
        
        if "weighted_score" in similarities:
        
            weight = similarities["weighted_score"]
        
        else:
        
            weight = (
                sum(similarities.values())
                / len(similarities)
            )

        G.add_edge(

            edge["source"],
            edge["target"],

            weight=weight,

            similarities=similarities
        )

    return G




def detect_communities(G):

    communities = list(

        nx.community
        .greedy_modularity_communities(
            G
        )

    )

    node_to_community = {}

    for idx, community in enumerate(
        communities
    ):

        for node in community:

            node_to_community[node] = idx

    return (
        communities,
        node_to_community
    )



def build_report(
        G,
        communities
):

    degrees = dict(
        G.degree()
    )

    top_nodes = sorted(

        degrees.items(),

        key=lambda x: x[1],

        reverse=True

    )[:10]

    report = {

        "num_papers":
            G.number_of_nodes(),

        "num_edges":
            G.number_of_edges(),

        "num_clusters":
            len(communities),

        "top_connected_papers":

            [
                {
                    "paper_id": node,
                    "degree": degree
                }

                for node, degree
                in top_nodes
            ]
    }

    return report




def draw_graph(
        G,
        node_to_community,
        output_file=f"{OUTPUT_DIR}/graph.png"
):

    fig = plt.figure(
        figsize=(18, 12)
    )

    fig.patch.set_facecolor("#e8e8e8")
  
    pos = nx.spring_layout(
        G,
        k=1.2,
        iterations=100,
        seed=42
    )

    communities = sorted(
        set(
            node_to_community.values()
        )
    )

    cmap = plt.cm.tab20

    # ------------------
    # Nodes
    # ------------------

    degrees = dict(
        G.degree()
    )

    node_sizes = [

        300 + degrees[node] * 200

        for node
        in G.nodes()
    ]

    node_colors = [

        node_to_community[node]

        for node
        in G.nodes()
    ]

    nx.draw_networkx_nodes(

        G,
        pos,

        node_size=node_sizes,

        node_color=node_colors,

        cmap=cmap,

        alpha=0.9
    )

    # ------------------
    # Edges
    # ------------------

    weights = [

        G[u][v].get(
            "weight",
            0.5
        ) * 4

        for u, v
        in G.edges()
    ]

    nx.draw_networkx_edges(

        G,
        pos,

        width=weights,

        alpha=0.4
    )

    # ------------------
    # Labels
    # ------------------

    labels = {}

    for node in G.nodes():

        label = (
            G.nodes[node]
            .get(
                "label",
                node
            )
        )

        if len(label) > 30:

            label = (
                label[:30]
                + "..."
            )

        labels[node] = label

    nx.draw_networkx_labels(

        G,
        pos,

        labels=labels,

        font_size=8
    )

    plt.title(
        "Scientific Paper Similarity Graph",
        fontsize=18
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved graph image to {output_file}"
    )


def execute():

    build_graph()

    paper_graph = f"{OUTPUT_DIR}/paper_graph.json"
    graph_json = (
        paper_graph
    )

    G = load_graph(
        graph_json
    )

    communities, node_to_community = (

        detect_communities(G)

    )

    report = build_report(
        G,
        communities
    )

    with open(

        f"{OUTPUT_DIR}/graph_report.json",

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            report,

            f,

            indent=2,

            ensure_ascii=False
        )

    draw_graph(

        G,

        node_to_community,

        f"{OUTPUT_DIR}/paper_graph.png"
    )
