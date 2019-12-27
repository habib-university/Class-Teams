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
import random
import sys
import networkx as nx

from colorama import Fore, Style
from graphviz import Digraph

# Number of random matchings to compute; the highest scoring is chosen.
NUM_TRIES: int = 10000


class ProgressBar:
    def __init__(self, title: str, max_score: int, steps: int = 10, progress_length: int = 4) -> None:
        '''
        Initializer for the ProgressBar. Sets the given title, and max_score, and initializes
        current_progess as zero.
        steps equals the number of times the progress bar is updated.
        progress_length equals the number of times '#' is printed when show_progress is called.
        '''
        self.title = title
        self.max_score = max_score
        self.current_progress = 0
        self.step_size = max_score/steps
        self.progress_length = progress_length

    def start_progress(self) -> None:
        '''
        prints the title on the screen, to mark the start of progress bar.
        '''
        sys.stdout.write(self.title + ": [")
        sys.stdout.flush()

    def update_progress(self, current_score: int) -> None:
        '''
        updates the progress bar with the current_score.
        '''
        if current_score % self.step_size == 0:
            self.show_progress()

    def show_progress(self) -> None:
        '''
        adds '#' to the progress bar. Progress_length equals the number of times '#' is added.
        '''
        self.current_progress += self.progress_length
        sys.stdout.write("#" * (self.progress_length))
        sys.stdout.flush()

    def end_progress(self) -> None:
        '''
        ends the progress bar after printing any necesarry details.
        '''
        sys.stdout.write("#" * int((self.progress_length*(self.max_score/self.step_size))  - self.current_progress) + "]\n")
        sys.stdout.flush()


def get_score_for_matching(graph: nx.DiGraph, matching: [(str, str)]) -> float:
    """Scores a matching.

    Args:
    - graph: contains the nodes and edges to be used to compute the score
    - matching: the matching to be scored

    Returns:
    the score for matching.
    """
    # This matching's score is the number of greens included in the matching.
    # That is, how many nodes are matched with their greens?
    score = sum((1 for src, dst in matching
                 if (graph.has_edge(src, dst) and graph[src][dst]['pref'])))
    score += sum((1 for src, dst in matching
                  if (graph.has_edge(dst, src) and graph[dst][src]['pref'])))
    # The score is perfect when everyone is matched with one of their greens.
    perfect_score = sum((1 for n in graph.nodes() if graph.nodes[n]['pref']))
    # Normalize this matching's score w.r.t. the perfect score.
    return score / perfect_score

def get_pretty_string(graph: nx.DiGraph, matching: [(str, str)]) -> str:
    """Builds and returns a string describing the matching.

    Args:
    - graph: contains the nodes and edges that indicate input preferences.
    - matching: the matching for which the string is to be built.

    Returns:
    a string description of the matching.
    """
    def get_color_string(src: str, dst: str) -> str:
        """Returns a colored src depending on the preference of src to dst.

        src is indifferent: black
        src has preferences but dst is not one of them: yellow
        dst is a green of src: green
        dst is a red of src: src red

        Args:
        - src: the node to be colored
        - dst: the preference of src to dst determines the color assigned to src

        Returns:
        a colored src
        """
        if not graph.nodes[src]['pref']:  # src is indifferent
            return src
        elif not graph.has_edge(src, dst):  # src is indifferent to dst
            return f'{Fore.YELLOW}{src}{Style.RESET_ALL}'
        elif graph[src][dst]['pref']:  # dst is a green of src
            return f'{Fore.GREEN}{src}{Style.RESET_ALL}'
        else:  # dst is a red of src
            return f'{Fore.RED}{src}{Style.RESET_ALL}'

    # Sort the matching so that duplicate matchings can be visually identified
    # when printed. Build a colored string for each match in the matching and
    # return the matching in a print-friendly format.
    matching = sorted([sorted(match) for match in matching])
    to_print = [f'({get_color_string(src, dst)}, {get_color_string(dst, src)})'
                for src, dst in matching]
    return ', '.join(to_print)

def get_matching(graph: nx.DiGraph) -> [(str, str)]:
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

    def is_mismatch(src: str, dst: str) -> bool:
        '''Is matching str with dst disallowed? That is, is src a red of dst?'''
        return graph.has_edge(dst, src) and not graph[dst][src]['pref']

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
        for dst in candidates:
            match = (src, dst)
            if not is_mismatch(*match):
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
        _ = [graph.add_edge(src, n, pref=True) for n in greens]
        _ = [graph.add_edge(src, n, pref=False) for n in reds]
        if greens or reds:
            graph.nodes[src]['pref'] = True

    # Read the header row and identify the columns in the file that contain the
    # greens and the reds. In each remaining row, read the source node, its
    # greens and reds, and add the preferences to graph. When reading, ignore
    # extraneous whitespace that may arise due to bad CSV saving.
    with open(csv_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        headers = list(map(lambda s: s.strip().lower(), next(csv_reader)))
        green_indexes = [i for i, head in enumerate(headers) if "green" in head]
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

### WORKS WELL ON ITS OWN. EDIT ONLY IF YOU KNOW WHAT YOU ARE DOING.
def main():
    '''Computes the best matching from input preferences.'''
    # Build graph from preferences, and mark the nodes that are
    # indifferent. Visualize the graph, and compute NUM_TRIES matchings. Store
    # the matching with the highest score. Show progress bar as matchings are
    # computed.
    filename = 'preferences.csv'
    graph = read_data(filename)
    for src in graph.nodes():
        graph.nodes[src].setdefault('pref', False)
    visualize(graph)
    high_score: int = -sys.maxsize -1
    best_matching: [(str, str)] = []
    progress_bar = ProgressBar("progress", NUM_TRIES)
    progress_bar.start_progress()
    for _ in range(NUM_TRIES):
        progress_bar.update_progress(_)
        if (matching := get_matching(graph)) and \
           (score := get_score_for_matching(graph, matching)) > high_score:
            high_score = score
            best_matching = matching
    progress_bar.end_progress()
    # Output the best (highest scoring) match in a suitable format and its
    # score.
    print(f'{get_pretty_string(graph, best_matching)}\n{high_score}')

if __name__ == '__main__':
    main()
