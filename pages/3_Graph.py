import json

import streamlit as st

import sys 
import os 
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_DIR, UPLOADS_DIR

from core.session_manager import (
    load_settings,
    save_settings
)

settings = load_settings()

if not settings["is_processed"]:

    st.warning(
        "Start a session first."
    )

    st.stop()


st.title(
    "Paper Graph"
)

graph_image = (

    OUTPUT_DIR
    / "paper_graph.png"

)

st.image(
    str(graph_image)
)


report_file = (

    OUTPUT_DIR
    / "graph_report.json"
)

with open(
    report_file,
    "r",
    encoding="utf-8"
) as f:

    report = json.load(f)


col1, col2, col3 = st.columns(3)

col1.metric(
    "Papers",
    report["num_papers"]
)

col2.metric(
    "Edges",
    report["num_edges"]
)

col3.metric(
    "Clusters",
    report["num_clusters"]
)


st.subheader(
    "Top Connected Papers"
)

for item in (

    report[
        "top_connected_papers"
    ]

):

    st.write(

        f"{item['paper_id']} "
        f"(degree={item['degree']})"
    )