import json
import numpy as np
import networkx as nx
from pathlib import Path
# from config.config import OUTPUT_DIR
from langchain_ollama import OllamaEmbeddings
import sys 
import os 
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_DIR, ROOT_DIR
print(OUTPUT_DIR)
print(ROOT_DIR)
def load_profiles(output_dir):

    papers = []

    output_dir = Path(output_dir)

    for paper_dir in output_dir.iterdir():

        if not paper_dir.is_dir():
            continue

        analysis_file = (
            paper_dir /
            "paper_analysis.json"
        )
        title_file = (
            paper_dir /
            "root_sections.json"
        )
        if title_file.exists():

          with open(
                    title_file,
                    "r",
                    encoding="utf-8"
                ) as f:

            title = json.load(f)


          paper_title = (
              title
              .get("document_profile", {})
              .get("title", paper_dir.name)
          )

        if not analysis_file.exists():
            continue

        with open(
            analysis_file,
            "r",
            encoding="utf-8"
        ) as f:

            analysis = json.load(f)

        profile = analysis.get(
            "document_profile",
            {}
        )
        # print(type(profile))
        # print(profile)
        # print(profile)
        if isinstance(profile, str):

          profile = (
              profile
              .replace("```json", "")
              .replace("```", "")
              .strip()
          )

          profile = json.loads(profile)
        papers.append({

            "paper_id":
                paper_dir.name,

            "title":
                paper_title
                ,
            "methods":
                profile.get(
                    "methods",
                    []
                ),

            "research_field":
                profile.get(
                    "research_topics",
                    []
                ),



            "applications":
                profile.get(
                    "applications",
                    []
                ),

            "main_contributions":
                profile.get(
                    "main_contributions",
                    []
                ),

              "keywords":
                profile.get(
                    "keywords",
                    []
                ),

              "research_topics":
                profile.get(
                    "research_topics",
                    []
              )
        })

    return papers




def embed_text(text):
    
    embedding_model = (
        OllamaEmbeddings(
            model="embeddinggemma"
        )
    )

    return (
        embedding_model
        .embed_query(text)
    )




def build_profile_embeddings(papers):

    for paper in papers:

        paper["method_embedding"] = (
            embed_text(
                "\n".join(
                    paper["methods"]
                )
            )
        )

        paper["application_embedding"] = (
            embed_text(
                "\n".join(
                    paper["applications"]
                )
            )
        )

        paper["contribution_embedding"] = (
            embed_text(
                "\n".join(
                    paper[
                        "main_contributions"
                    ]
                )
            )
        )

        paper["keywords_embeddings"] = (
            embed_text(
                "\n".join(
                    paper[
                        "keywords"
                    ]
                )
            )
        )

        paper["research_embeddings"] = (
            embed_text(
                "\n".join(
                    paper[
                        "research_topics"
                    ]
                )
            )
        )

    return papers



def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a)
        *
        np.linalg.norm(b)
    )




def build_graph(
        papers,
        threshold=0.6
):

    graph = nx.Graph()

    # -------------------
    # Nodes
    # -------------------

    for paper in papers:

        graph.add_node(

            paper["paper_id"],

            title=paper["title"]
        )

    # -------------------
    # Edges
    # -------------------

    for i in range(len(papers)):

        for j in range(
            i + 1,
            len(papers)
        ):

            paper_a = papers[i]
            paper_b = papers[j]

            # Method

            method_sim = (
                cosine_similarity(

                    paper_a[
                        "method_embedding"
                    ],

                    paper_b[
                        "method_embedding"
                    ]
                )
            )

            # Application

            app_sim = (
                cosine_similarity(

                    paper_a[
                        "application_embedding"
                    ],

                    paper_b[
                        "application_embedding"
                    ]
                )
            )


            # Contribution

            contrib_sim = (
                cosine_similarity(

                    paper_a[
                        "contribution_embedding"
                    ],

                    paper_b[
                        "contribution_embedding"
                    ]
                )
            )


            # Keywords

            key_sim = (
                cosine_similarity(

                    paper_a[
                        "keywords_embeddings"
                    ],

                    paper_b[
                        "keywords_embeddings"
                    ]
                )
            )



            # Topic field

            topic_sim = (
                cosine_similarity(

                    paper_a[
                        "research_embeddings"
                    ],

                    paper_b[
                        "research_embeddings"
                    ]
                )
            )

            WEIGHTS = {
                "topic": 0.20,
                "keyword": 0.15,
                "method": 0.30,
                "application": 0.15,
                "contribution": 0.20
            }

            final_score = (
                topic_sim * WEIGHTS["topic"]
                + key_sim * WEIGHTS["keyword"]
                + method_sim * WEIGHTS["method"]
                + app_sim * WEIGHTS["application"]
                + contrib_sim * WEIGHTS["contribution"]
            )
            if final_score >= threshold:
              graph.add_edge(

                paper_a["paper_id"],
                paper_b["paper_id"],

                weight=float(final_score),

                similarities={
                    "weighted_score":
                        float(final_score),

                    "topic":
                        float(topic_sim),

                    "keyword":
                        float(key_sim),

                    "method":
                        float(method_sim),

                    "application":
                        float(app_sim),

                    "contribution":
                        float(contrib_sim)
                }
            )

    return graph



def export_graph(graph, output_file=OUTPUT_DIR):

    graph_data = {
        "nodes": [],
        "edges": []
    }

    # Nodes
    for node, data in graph.nodes(data=True):

        graph_data["nodes"].append({

            "id": node,

            "label": data.get(
                "title",
                node
            )
        })

    # Edges
    for source, target, data in graph.edges(data=True):

        graph_data["edges"].append({

            "source": source,

            "target": target,

            "similarities": data.get(
                "similarities",
                {}
            )
        })

    with open(
        f"{output_file}/paper_graph.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            graph_data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Graph saved to {output_file}/paper_graph.json"
    )





def execute():

    SIMILARITY_THRESHOLD = 0.6
    print("Loading profiles...")

    papers = load_profiles(
        OUTPUT_DIR
    )

    print(
        f"Loaded {len(papers)} papers"
    )

    print(
        "Building embeddings..."
    )

    papers = build_profile_embeddings(
        papers
    )

    print(
        "Building graph..."
    )

    graph = build_graph(
        papers,
        threshold=SIMILARITY_THRESHOLD
    )

    print(
        f"Nodes: {graph.number_of_nodes()}"
    )

    print(
        f"Edges: {graph.number_of_edges()}"
    )

    export_graph(graph)
