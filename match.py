'''Computes a matching of students based on their preferences.

Author: Waqar Saleem
Contact: wsaleem@gmail.com
Last Edit: 26 Oct, 2019
'''

import copy
import csv
import random
import sys
import networkx as nx

from colorama import Fore, Style
from graphviz import Digraph

# Number of random matchings to compute; the highest scoring is chosen.
NUM_TRIES: int = 10000

# Progress bar initialization.
PROGRESS_X = 0

############### PROGRESS BAR FUNCTIONS BEGIN

def start_progress(title: str) -> None:
    '''Initializes progress bar internals and and sets the title.'''
    global PROGRESS_X
    sys.stdout.write(title + ": [")
    sys.stdout.flush()
    PROGRESS_X = 0

def show_progress_bar(current_score: int, max_score: int) -> None:
    """Updates progress bar with the current progress.

    Args:
    current_score: the progress so far
    max_score: the progress to be reached
    """
    def progress(score: int) -> None:
        """Display progress bar with current progress.

        Args:
        score: the progress so far
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
############### PROGRESS BAR FUNCTIONS END


def get_score_for_matching(graph: nx.DiGraph, matching: [(str, str)]) -> float:
    """Scores a matching.

    Args:
    graph: contains the nodes and edges to be used to compute the score
    matching: the matching to be scored

    Returns:
    the score for matching.
    """
    score = sum((1 for src, dst in matching
                 if graph.has_edge(src, dst) and graph[src][dst]['pref']))
    score += sum((1 for src, dst in matching
                  if graph.has_edge(dst, src) and graph[dst][src]['pref']))
    perfect_score = sum((1 for n in graph.nodes() if graph.nodes[n]['pref']))
    return score / perfect_score

def get_pretty_string(graph: nx.DiGraph, matching: [(str, str)]) -> str:
    """Builds and returns a string describing the matching.

    Args:
    graph: contains the nodes and edges that indicate input preferences.
    matching: the matching for which the string is to be built.

    Returns:
    a string description of the matching.
    """
    def get_color_string(src: str, dst: str) -> str:
        """Returns a colored src depending on the preference of src to dst.

        src does not have any preference: black
        src has preferences but dst is not one of them: yellow
        dst is a green of src: green
        dst is a red of src: src red

        Args:
        src: the node to be colored
        dst: the preference of src to dst determines the color assigned to src

        Returns:
        a colored src
        """
        if not graph.has_edge(src, dst):
            if graph.nodes[src]['pref']:
                return f'{Fore.YELLOW}{src}{Style.RESET_ALL}'
            else:
                return src
        elif graph[src][dst]['pref']:
            return f'{Fore.GREEN}{src}{Style.RESET_ALL}'
        else:
            return f'{Fore.RED}{src}{Style.RESET_ALL}'

    matching = sorted([sorted(match) for match in matching])
    to_print = [f'({get_color_string(src, dst)}, {get_color_string(dst, src)})'
                for src, dst in matching]
    return ', '.join(to_print)

def get_matching(graph: nx.DiGraph) -> [(str, str)]:
    """Builds a matching based on the preferences indicated in graph.

    Args:
    graph: contains nodes and edges indicating input preferences.

    Returns:
    a feasible matching. if none is found, the returned list is empty.
    """
    graph = copy.deepcopy(graph)
    graph.graph['matching'] = []

    def is_mismatch(src: str, dst: str) -> bool:
        '''Is matching str with dst disallowed? That is, is src a red of dst?'''
        return graph.has_edge(dst, src) and not graph[dst][src]['pref']

    def add_match(src: str, candidates: [str]) -> bool:
        """Finds a match for src from candidates and reports the success.

        Some candidates may be disqualified as per preferences.

        Args:
        src: the node to be matched
        canddates: the list of possible matches for src

        Returns:
        True if a match is found from candidates, False otherwise.
        """
        random.shuffle(candidates)
        for dst in candidates:
            match = (src, dst)
            if not is_mismatch(*match):
                graph.graph['matching'].append(match)
                graph.remove_nodes_from(match)
                return True
        return False

    while graph.nodes() and (src := random.choice([*graph.nodes()])):
        greens = [n for n in graph.successors(src) if graph[src][n]['pref']]
        if add_match(src, greens):
            continue
        non_neighbors = set(graph.nodes()) - set(graph.neighbors(src)) - {src}
        if not add_match(src, list(non_neighbors)):
            return []
    return graph.graph['matching']

def visualize(graph: nx.DiGraph) -> None:
    '''Visualizes the preferences indicated in graph.'''
    file_name = "preferences"
    dot = Digraph()
    dot.attr('edge', color='darkgreen:red')
    for src, dst in graph.edges():
        if graph[src][dst]['pref']:
            dot.edge(src, dst, color='darkgreen')
        else:
            dot.edge(src, dst, color='red')
    dot.render(file_name, view=True)

def read_data(csv_filename: str) -> nx.DiGraph:
    """Builds a graph representing the preference data read from file.

    Args:
    csv_filename: name of csv file which contains preference data.

    Returns:
    the graph built from the preference data read from the file.
    """
    graph = nx.DiGraph()

    def add_targets(src: str, greens: [str], reds: [str]):
        _ = [graph.add_edge(src, n, pref=True) for n in greens]
        _ = [graph.add_edge(src, n, pref=False) for n in reds]
        if greens or reds:
            graph.nodes[src]['pref'] = True

    # Reading a CSV file, adapted from:
    # https://realpython.com/python-csv/ and
    # https://stackoverflow.com/questions/17262256/how-to-read-one-single-line-of-csv-data-in-python
    with open('preferences.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        headers = next(csv_reader)
        headers = list(map(lambda s: s.strip().lower(), headers))
        green_indexes = [i for i, head in enumerate(headers) if "green" in head]
        red_indexes = [i for i, head in enumerate(headers) if "red" in head]
        for row in csv_reader:
            row = list(map(str.strip, row))
            if not row[0]:
                continue
            greens = [g for i in green_indexes if (g := row[i])]
            reds = [r for i in red_indexes if (r := row[i])]
            add_targets(row[0], greens, reds)
    print(f'Read preferences of {len(graph.nodes())} students with up to '
          f'{len(green_indexes)} greens and {len(red_indexes)} reds.')
    return graph

### WORKS WELL ON ITS OWN. EDIT ONLY IF YOU KNOW WHAT YOU ARE DOING.
def main():
    '''Computes the best matching from input preferences.'''
    filename = 'preferences.csv'
    preferences = read_data(filename)
    visualize(preferences)
    for src in preferences.nodes():
        preferences.nodes[src].setdefault('pref', False)
    high_score: int = -sys.maxsize -1
    best_matching: [(str, str)] = []
    start_progress("progress")
    for _ in range(NUM_TRIES):
        show_progress_bar(_, NUM_TRIES)
        if (matching := get_matching(preferences)) and \
           (score := get_score_for_matching(preferences, matching)) > high_score:
            high_score = score
            best_matching = matching
    end_progress()
    print(f'{get_pretty_string(preferences, best_matching)}\n{high_score}')

if __name__ == '__main__':
    main()
