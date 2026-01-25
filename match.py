"""Compute student teams based on pairwise preferences.

This script reads student pairing preferences from a tab/comma-separated file,
constructs a compatibility graph, computes an optimal matching, and provides
both textual and graphical representations of the resulting teams.

Author: Waqar Saleem
Contact: wsaleem@gmail.com
Last Edit: Jan 25, 2026
"""

import csv
from typing import Dict, Iterable, Iterator, Set, Tuple, TypeAlias

import networkx as nx
from colorama import Fore, Style
from graphviz import Digraph
import random
from pathlib import Path

INPUT_FILE = "preferences.csv"  # tab-separated (TSV)
DELIMITER = "\t"

Student: TypeAlias = str
Preferences: TypeAlias = Dict[Student, Dict[Student, bool]]
Team: TypeAlias = Tuple[Student, Student]


def read_preferences(path: str) -> Preferences:
    """Read student preferences from a TSV file.

    The input file is expected to be tab-separated and structured as follows:

    - The first row is a header. Columns containing the substring "green"
      indicate students the row student wants to work with; columns containing
      "red" indicate students they do not want to work with.
    - Each subsequent row represents one student:
        * column 0: the student identifier (source)
        * column i: another student identifier (optional or blank)

    Args:
        path: Path to the TSV file containing student preferences.

    Returns:
        A nested dictionary ``pref`` such that:
        - ``pref[src][dst] == True`` if ``src`` wants to work with ``dst``.
        - ``pref[src][dst] == False`` if ``src`` does not want to work with ``dst``.
    """
    pref: Preferences = {}

    with open(path, newline="") as f:
        reader = csv.reader(f, delimiter=DELIMITER)
        header = [h.strip().lower() for h in next(reader)]

        for row in reader:
            row = [cell.strip() for cell in row]
            if not row or not (src := row[0]):
                continue

            pref.setdefault(src, {})

            for col_name, cell in zip(header[1:], row[1:]):
                if not cell:
                    continue

                # Ensure referenced student exists as a node
                pref.setdefault(cell, {})

                if "green" in col_name:
                    pref[src][cell] = True
                elif "red" in col_name:
                    pref[src][cell] = False

    return pref


def format_teams(pref: Preferences, teams: Iterable[Team]) -> str:
    """Format teams as a human-readable, colorized string.

    Each team is rendered on its own line. A student name is shown in:
    - green if they want to work with their partner,
    - red if they explicitly do not want to work with their partner,
    - the default terminal color if no preference was stated.

    Args:
        pref: Preference dictionary mapping students to their preferences.
        teams: Iterable of 2-tuples representing student teams.

    Returns:
        A multi-line string describing the teams.
    """
    def fmt(u: Student, v: Student) -> str:
        return (
            f"{Fore.GREEN if pref[u][v] else Fore.RED}{u}{Style.RESET_ALL}"
            if v in pref.get(u, {})
            else u
        )

    return "\n".join(f"{fmt(a, b)}, {fmt(b, a)}" for a, b in teams)


def build_graph(pref: Preferences) -> nx.Graph:
    """Build an undirected compatibility graph from preferences.

    An edge is added between two students if neither has expressed a red
    preference against the other. Edge weights reflect the number of green
    endpoints:

    - ``0.0``: no green preferences
    - ``1.0``: one-sided green preference
    - ``1.5``: two-sided green preference (capped to favor two single-greens
      over one mutual-green elsewhere)

    Args:
        pref: Preference dictionary mapping students to their preferences.

    Returns:
        An undirected NetworkX graph whose nodes are students and whose
        weighted edges represent compatibility.
    """
    G = nx.Graph()
    students = sorted(pref.keys())
    G.add_nodes_from(students)

    for i, u in enumerate(students):
        for v in students[i + 1:]:
            # Forbid pairing if red in either direction
            if pref.get(u, {}).get(v) is False:
                continue
            if pref.get(v, {}).get(u) is False:
                continue

            # Weight = number of green endpoints (capped)
            w = 0
            if pref.get(u, {}).get(v):
                w += 1
            if pref.get(v, {}).get(u):
                w += 1
            w = min(w, 1.5)

            G.add_edge(u, v, weight=w)

    return G


def visualize_preferences(
        pref: Dict[str, Dict[str, bool]],
        anonymize: bool = True,
        engine: str = "fdp",
        filename: str = "preferences",
) -> None:
    """Visualize preferences as a directed graph with colored arrows.

    Each student is represented as a node. Directed edges indicate preferences:
    - green arrows denote a desire to work together,
    - red arrows denote an explicit refusal.

    Args:
        pref: Preference dictionary where ``pref[u][v]`` is ``True`` (green)
            or ``False`` (red).
        anonymize: Whether to anonymize student identifiers in the visualization.
        engine: Graphviz layout engine to use. One of ``"dot"``, ``"neato"``,
            ``"fdp"``, ``"sfdp"``, ``"circo"``, or ``"twopi"``.
        filename: Base name of the output file (without extension).

    Returns:
        None. The function renders and saves a PNG file and opens it for viewing.
    """
    # Build a stable node list
    nodes = sorted(pref.keys())

    # Create anonymization mapping, if requested
    if anonymize:
        labels = {
            u: f"S{i:02d}"
            for u, i in zip(nodes, random.sample(range(len(nodes)), k=len(nodes)))
        }
        filename += "_anon"
    else:
        labels = {u: u for u in nodes}

    # Initialize Graphviz directed graph
    engine = Digraph(name="Preferences", engine=engine)

    # Global styling parameters
    engine.attr(
        overlap="false",
        splines="true",
        nodesep="0.35",
        ranksep="0.6",
    )
    engine.attr("node", shape="circle", fontsize="10")
    engine.attr("edge", arrowsize="0.8", penwidth="1.2")

    # Add nodes explicitly (ensures isolated nodes are shown)
    for u in nodes:
        engine.node(labels[u])

    # Add directed edges based on preferences
    for u, nbrs in pref.items():
        for v, is_green in nbrs.items():
            if u == v:
                continue
            engine.edge(
                labels[u],
                labels[v],
                color=("darkgreen" if is_green else "red"),
            )

    # Render output, anchoring to script directory when available
    try:
        base_dir = Path(__file__).resolve().parent
    except NameError:
        base_dir = Path.cwd()

    engine.render(str(base_dir / filename), format="png", view=True)


def main() -> None:
    """Run the full workflow: read preferences, compute teams, and display output."""
    pref = read_preferences(INPUT_FILE)
    G = build_graph(pref)

    teams: Set[Team] = nx.max_weight_matching(G, maxcardinality=True)
    matched = {p for uv in teams for p in uv}
    unmatched = sorted(set(pref) - matched)

    print(f"From data of {len(pref)} students,\n- made {len(teams)} teams:")
    print(format_teams(pref, teams))
    print("- following are unmatched:")
    print(unmatched)

    visualize_preferences(pref)


if __name__ == "__main__":
    main()
