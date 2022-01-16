'''Computes a matching of students based on their preferences.

Author: Waqar Saleem
Contact: wsaleem@gmail.com
Last Edit: 26 Oct, 2019

CSV reading adapted from:
- https://realpython.com/python-csv/ and
- https://stackoverflow.com/questions/17262256/how-to-read-one-single-line-of-csv-data-in-python
'''

import csv
import random
import networkx as nx

from graphviz import Digraph


class Preferences(object):
    """Reads and stores student preferences for teaming up. Supports related queries.

    Preferences are stored in a directed graph. Each student is represented by a
    node.  Preferences are represented by edges between nodes. Each edge has a
    source and a destination student corresponding to its source and destination
    nodes. Each edge has a 'pref' property whose value is True if the source
    wants to work with the destination, and False if the source does not want to
    work with the destination.
    """

    def __init__(self, csv_path: str) -> None:
        '''Reads preferences from a CSV file at csv_path.

        The CSV file has student IDs in the first column. The header of the
        column is ignored. Each row contains the preferences of the student who
        ID is contained in the first column.

        Every other column has a header which is either 'Green' or 'Red' and
        optionally contains students IDs. 'Green' indicates a positive
        preference, and 'Red' a negative preference.

        Parameters:
        - self: mandatory reference to this object
        - csv_path: path to a the CSV file which contains the preferences

        Returns:
        None
        '''
        # Initialize the graph to store the preferences.
        self.graph = nx.DiGraph()
        # Process input file.
        with open(csv_path) as csv_file:
            # Identify Green and Red columns.
            csv_reader = csv.reader(csv_file, delimiter='\t')
            headers = list(map(lambda s: s.strip().lower(), next(csv_reader)))
            green_indexes = [i for i, head in enumerate(
                headers) if "green" in head]
            red_indexes = [i for i, head in enumerate(
                headers) if "red" in head]
            # Identify the green and red students in each row and add them to
            # the graph.
            for row in csv_reader:
                row = list(map(str.strip, row))
                if (src := row[0]):
                    greens = [g for i in green_indexes if (g := row[i])]
                    reds = [r for i in red_indexes if (r := row[i])]
                    self._add_student_preferences(src, greens, reds)
        # Print a summary of the information read from the file. Return graph.
        print(f'Read preferences of {len(self.graph.nodes())} students: {list(self.graph)}\n with up to '
              f'{len(green_indexes)} greens and {len(red_indexes)} reds.')

    def _add_student_preferences(self, src: str, greens: [str], reds: [str]) -> None:
        """Updates the graph with the src student and their preferences.

        A node is added for the src student, and edges are added for the preferences.

        Parameters:
        - self: mandatory reference to this object
        - src: the student whose preferences are to be added
        - greens: list of students whom src wants to work with
        - reds: list of students whom src does not want to work with

        Returns:
        None
        """
        # Add student node, initially with no preference.
        self.graph.add_node(src)
        self.graph.nodes[src]['pref'] = False
        # Add green and red edges.
        for dst in greens:
            self.graph.add_edge(src, dst, pref=True)
        for dst in reds:
            self.graph.add_edge(src, dst, pref=False)

    def visualize(self, anonymize: bool = True) -> None:
        """Visualizes the preferences.

        Parameters:
        - self: mandatory reference to this object
        - anonymize: whether stored IDs should be anonymized

        Returns:
        None
        """
        file_name = "preferences"  # output file name
        if anonymize:
            aliases = random.sample(range(101, 1000), len(self.graph.nodes()))
            mapping = dict(zip(self.graph.nodes(), map(str, aliases)))
            graph = nx.relabel.relabel_nodes(self.graph, mapping, True)
        else:
            graph = self.graph
        # Generate visualization.
        dot = Digraph()  # graph to be visualized
        dot.attr('edge', color='darkgreen:red')  # edge colors in visualization
        for src, dst in graph.edges():  # add graph edges to visualization
            if graph[src][dst]['pref']:
                dot.edge(src, dst, color='darkgreen')
            else:
                dot.edge(src, dst, color='red')
        dot.render(file_name, view=True)  # save and render visualization

    def can_team(self, src: str, dst: str) -> bool:
        """Returns whether src and dst can be in the same team.

        Parameters:
        - self: mandatory reference to this object
        - src: one of the students to check
        - dst: the other student to check

        Returns:
        True if none of the students is a red of the other, False otherwise.
        """
        # Check that the students' data is stored.
        if src not in self.graph.nodes() or dst not in self.graph.nodes():
            return False
        if self.graph.has_edge(src, dst) and not self.graph[src][dst]['pref']:
            return False
        if self.graph.has_edge(dst, src) and not self.graph[dst][src]['pref']:
            return False
        return True

    def get_students(self) -> [str]:
        """Returns the names of all the stored students.

        Parameters:
        - self: mandatory reference to this object

        Returns:
        A list of student names.
        """
        return list(self.graph)

    def is_green(self, src: str, dst: str) -> bool:
        """Returns whether src wants to work with dst.

        Parameters:
        - self: mandatory reference to this object
        - src: the source student to check
        - dst: the destination student to check

        Returns:
        True if src wants to work with dst, False otherwise.
        """
        # Check that the students' data is stored.
        if src not in self.graph.nodes() or dst not in self.graph.nodes():
            return False
        return self.graph.has_edge(src, dst) and self.graph[src][dst]['pref']

    def has_preference(self, src: str) -> bool:
        """Returns whether there is any stored preference of src.

        Parameters:
        - self: mandatory reference to this object
        - src: the student whose preferences is queried

        Returns:
        True if there are stored preferences of src, False otherwise.
        """
        return len(self.graph.successors(src)) > 0

    def get_greens(self, src: str) -> [str]:
        """Returns the students that src wants to work with.

        Parameters:
        - self: mandatory reference to this object
        - src: the student whose preference is queried

        Returns:
        A list of students that src wants to work with.
        """
        return [dst for dst in self.graph.successors(src) if self.is_green(src, dst)]
