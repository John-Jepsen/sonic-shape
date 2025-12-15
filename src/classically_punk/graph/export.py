"""
Graph export utilities.

Converts Edge collections to networkx graphs and serializes to JSON/GraphML for
downstream visualization or analysis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import networkx as nx

from classically_punk.graph.schema import Edge


def edges_to_networkx(edges: Iterable[Edge], directed: bool = True) -> nx.Graph:
    """
    Build a networkx graph from Edge objects.
    """
    G = nx.MultiDiGraph() if directed else nx.MultiGraph()
    for e in edges:
        G.add_edge(
            e.src,
            e.dst,
            type=e.type,
            weight=e.weight,
            source=e.source,
            version=e.version,
        )
    return G


def export_node_link_json(edges: Iterable[Edge], path: Path) -> None:
    """
    Write a node-link JSON from edges for web visualization.
    """
    G = edges_to_networkx(edges)
    data = nx.readwrite.json_graph.node_link_data(G)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def export_graphml(edges: Iterable[Edge], path: Path) -> None:
    """
    Write GraphML for offline graph tools.
    """
    G = edges_to_networkx(edges)
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(G, path)

