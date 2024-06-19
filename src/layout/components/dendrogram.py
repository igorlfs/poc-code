import numpy as np
import plotly.figure_factory as ff
from numpy.typing import NDArray
from pandas import DataFrame
from plotly.graph_objs import Figure
from sklearn.cluster import AgglomerativeClustering

from src.colors import CRUST, WHITE
from src.layout.components.util import get_clustering


def get_linkage_matrix(clustering: AgglomerativeClustering) -> NDArray:
    counts = np.zeros(clustering.children_.shape[0])
    n_samples = len(clustering.labels_)
    for i, merge in enumerate(clustering.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    return np.column_stack([clustering.children_, clustering.distances_, counts])


def generate_dendrogram_figure(
    subgroups_df: DataFrame, pos_x: float | None
) -> tuple[Figure, float, float]:
    clustering, normal_matrix = get_clustering(subgroups_df)
    linkage_matrix = get_linkage_matrix(clustering)

    fig = ff.create_dendrogram(
        X=normal_matrix,
        orientation="left",
        labels=subgroups_df["subgroup"].astype(str).tolist(),
        colorscale=[
            "#89b4fa",
            "#f9e2af",
            "#f38ba8",
            "#89dceb",
            "#a6e3a1",
            "#fab387",
            "#eba0ac",
            "#cba6f7",
        ],
        linkagefun=lambda _: linkage_matrix,
    )

    if pos_x is not None:
        fig.add_vline(x=pos_x, line_width=4, line_color=WHITE)

    fig.update_layout(
        title="<b>COVERAGE DIFFERENCE BETWEEN SUBGROUPS</b>",
        title_x=0.5,
        width=800,
        height=600,
        plot_bgcolor=CRUST,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=WHITE,
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
    )
    min_x = min(clustering.distances_)
    max_x = max(clustering.distances_)
    fig.update_xaxes(range=[max(min_x - 0.1, 0), max_x + 0.05], showticklabels=True)

    return fig, min_x, max_x
