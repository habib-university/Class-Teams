'''Computes a matching of students based on their preferences.

Author: Waqar Saleem
Contact: wsaleem@gmail.com
Last Edit: 26 Oct, 2019

CSV reading adapted from:
- https://realpython.com/python-csv/ and
- https://stackoverflow.com/questions/17262256/how-to-read-one-single-line-of-csv-data-in-python
'''

import copy
import csv
import itertools
import random
import sys
import networkx as nx

from colorama import Fore, Style
from graphviz import Digraph

# Number of random matchings to compute; the highest scoring is chosen.
NUM_TRIES: int = 10000
GROUP_SIZE: int = 5

# Progress bar initialization.
PROGRESS_X = 0

# -------------------- PROGRESS BAR FUNCTIONS BEGIN


def start_progress(title: str) -> None:
    '''Initializes progress bar internals and and sets the title.'''
    global PROGRESS_X
    sys.stdout.write(title + ": [")
    sys.stdout.flush()
    PROGRESS_X = 0


def show_progress_bar(current_score: int, max_score: int) -> None:
    """Updates progress bar with the current progress.

    Args:
    - current_score: the progress so far
    - max_score: the progress to be reached
    """
    def progress(score: int) -> None:
        """Display progress bar with current progress.

        Args:
        - score: the progress so far
        """
        global PROGRESS_X
        score = int(score * 40 // 100)
        sys.stdout.write("#" * (score - PROGRESS_X))
        sys.stdout.flush()
        PROGRESS_X = score

    step_size = max_score/10
    number_dec = str(current_score/step_size - (current_score//step_size))[1:]
    if number_dec == ".0":
        progress(((current_score/max_score)*100))


def end_progress() -> None:
    '''Terminates progress bar.'''
    sys.stdout.write("#" * (40 - PROGRESS_X) + "]\n")
    sys.stdout.flush()
# -------------------- PROGRESS BAR FUNCTIONS END


def read_data(csv_filename: str) -> nx.DiGraph:
    """Builds a graph representing the preference data read from file.

    Args:
    - csv_filename: name of csv file which contains preference data.

    Returns:
    the graph built from the preference data read from the file.
    """
    graph = nx.DiGraph()  # graph to store input preferences.

    def add_preferences(src: str, greens: [str], reds: [str]) -> None:
        """Adds preferences to the graph.

        Args:
        - src: the node whose preferences are to be added
        - greens: contains the green nodes of src
        - reds: contains the red nodes of src
        """
        # Add preferences to graph. Store whether src indicated preferences.
        any((graph.add_edge(src, n, pref=True) for n in greens))
        any((graph.add_edge(src, n, pref=False) for n in reds))
        if greens or reds:
            graph.nodes[src]['pref'] = True

    # Read the header row and identify the columns in the file that contain the
    # greens and the reds. In each remaining row, read the source node, its
    # greens and reds, and add the preferences to graph. When reading, ignore
    # extraneous whitespace that may arise due to bad CSV saving.
    with open(csv_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        headers = list(map(lambda s: s.strip().lower(), next(csv_reader)))
        green_indexes = [i for i, head in enumerate(headers)
                         if "green" in head]
        red_indexes = [i for i, head in enumerate(headers) if "red" in head]
        for row in csv_reader:
            row = list(map(str.strip, row))
            if (src := row[0]):
                greens = [g for i in green_indexes if (g := row[i])]
                reds = [r for i in red_indexes if (r := row[i])]
                add_preferences(src, greens, reds)
    # Print a summary of the information read from the file. Return graph.
    print(f'Read preferences of {len(graph.nodes())} students with up to '
          f'{len(green_indexes)} greens and {len(red_indexes)} reds.')
    return graph


def get_matching(graph: nx.DiGraph) -> [(str,) * GROUP_SIZE]:
    """Builds a matching based on the preferences indicated in graph.

    Args:
    - graph: contains nodes and edges indicating input preferences.

    Returns:
    a feasible matching. if none is found, the returned list is empty.
    """
    # Make a working copy of the graph with the matching as an attribute. The
    # matching is currently empty.
    graph = copy.deepcopy(graph)
    graph.graph['matching'] = []

    def is_mismatch(src: str, dsts: [str]) -> bool:
        '''Is matching str with any member of dsts disallowed? i.e. is src a red
        of any member of dsts?
        '''
        return any(graph.has_edge(dst, src) and not graph[dst][src]['pref']
                   for dst in dsts)

    def add_match(src: str, candidates: [str]) -> bool:
        """Finds a match for src from candidates and reports the success.

        Some candidates may be disqualified as per preferences.

        Args:
        - src: the node to be matched
        - canddates: the list of possible matches for src

        Returns:
        True if a match is found from candidates, False otherwise.
        """
        # Shuffle candidates to avoid bias and iterate through them. Report
        # success on finding the first valid match but first remove the matched
        # nodes from the graph so as to remove them from any further matchings.
        random.shuffle(candidates)
        for dsts in itertools.combinations(candidates, GROUP_SIZE-1):
            if not is_mismatch(src, dsts):
                match = (src, *dsts)
                graph.graph['matching'].append(match)
                graph.remove_nodes_from(match)
                return True
        # Could not find a valid match in candidates. Return failure.
        return False

    # Choose a random node from graph and try to match it with its greens. If
    # that fails, try to match it with nodes that it is indifferent to. Store
    # any found match and repeat for another node until all nodes are
    # matched. If any node cannot be matched, exit with failure.
    while graph.nodes() and (src := random.choice([*graph.nodes()])):
        greens = [n for n in graph.successors(src) if graph[src][n]['pref']]
        if not add_match(src, greens):
            dont_cares = set(graph.nodes()) - set(graph.neighbors(src)) - {src}
            if not add_match(src, list(dont_cares)):
                return []
    return graph.graph['matching']


def get_score_for_matching(graph: nx.DiGraph, matching: [(str,) * GROUP_SIZE]) -> float:
    """Scores a matching.

    Args:
    - graph: contains the nodes and edges to be used to compute the score
    - matching: the matching to be scored

    Returns:
    the score for matching.
    """
    # This matching's score is the number of greens included in the matching.
    # That is, how many nodes are matched with their greens?
    score = perfect_score = 0
    for match in matching:
        for i, src in enumerate(match):
            partners = match[:i] + match[i+1:]
            greens = [dst for dst in graph[src] if graph[src][dst]['pref']]
            score += len(set(partners) & set(greens))
            perfect_score += min(len(greens), GROUP_SIZE-1)
    return score / perfect_score


def get_pretty_string(graph: nx.DiGraph, matching: [(str,) * GROUP_SIZE]) -> str:
    """Builds and returns a string describing the matching.

    Args:
    - graph: contains the nodes and edges that indicate input preferences.
    - matching: the matching for which the string is to be built.

    Returns:
    a string description of the matching.
    """
    def get_color_string(src: str, dsts: [str]) -> str:
        """Returns a colored src depending on the preference of src to dst.

        src is indifferent: black
        src has preferences but none in dsts: yellow
        dsts contains a green of src: green
        dsts contains a red of src: src red

        Args:
        - src: the node to be colored
        - dsts: src's preferences to memebrs in dst determine the color to
          assign to src

        Returns:
        a colored src
        """
        if not graph.nodes[src]['pref']:  # src is indifferent
            return src
        else:
            greens = [dst for dst in graph[src] if graph[src][dst]['pref']]
            reds = [dst for dst in graph[src] if not graph[src][dst]['pref']]
            dsts, greens, reds = map(set, (dsts, greens, reds))
            if dsts & greens:
                return f'{Fore.GREEN}{src}{Style.RESET_ALL}'
            elif dsts & reds:
                return f'{Fore.RED}{src}{Style.RESET_ALL}'
            else:
                return f'{Fore.YELLOW}{src}{Style.RESET_ALL}'

    # Sort the matching so that duplicate matchings can be visually identified
    # when printed. Build a colored string for each match in the matching and
    # return the matching in a print-friendly format.
    matching = sorted([sorted(match) for match in matching])
    print(f'matching: {matching}')
    to_print = []
    for match in matching:
        match_str = [get_color_string(src, match[:i]+match[i+1:])
                     for i, src in enumerate(match)]
        match_str = f"({', '.join(match_str)})"
        to_print.append(match_str)
    return ', '.join(to_print)


def visualize(graph: nx.DiGraph) -> None:
    '''Visualizes the preferences indicated in graph.'''
    file_name = "preferences"  # output file name
    dot = Digraph()  # graph to be visualized
    dot.attr('edge', color='darkgreen:red')  # edge colors in visualization
    for src, dst in graph.edges():  # add graph edges to visualization
        if graph[src][dst]['pref']:
            dot.edge(src, dst, color='darkgreen')
        else:
            dot.edge(src, dst, color='red')
    dot.render(file_name, view=True)  # save and render visualization


# WORKS WELL ON ITS OWN. EDIT ONLY IF YOU KNOW WHAT YOU ARE DOING.


def main():
    '''Computes the best matching from input preferences.'''
    # Build graph from preferences and mark the nodes that have preferences and
    # those that are indifferent. Visualize the graph, and compute NUM_TRIES
    # matchings. Store the matching with the highest score. Display a progress
    # bar as the matchings are computed.
    filename = 'preferences.csv'
    graph = read_data(filename)
    for src in graph.nodes():
        graph.nodes[src].setdefault('pref', False)
    visualize(graph)
    high_score: int = -sys.maxsize - 1
    best_matching: [(str, str)] = []
    start_progress("progress")
    for _ in range(NUM_TRIES):
        show_progress_bar(_, NUM_TRIES)
        if (matching := get_matching(graph)) and \
           (score := get_score_for_matching(graph, matching)) > high_score:
            high_score = score
            best_matching = matching
    end_progress()
    # Output the best (highest scoring) match in a suitable format and its
    # score.
    print(f'{get_pretty_string(graph, best_matching)}\n{high_score}')


if __name__ == '__main__':
    main()
