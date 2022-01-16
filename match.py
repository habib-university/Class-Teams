'''Computes teams of students based on their preferences.

Author: Waqar Saleem
Contact: wsaleem@gmail.com
Last Edit:  16 Jan, 2022
'''

import copy
import random
import sys

from colorama import Fore, Style
from ProgressBar import *
from preferences import Preferences

# Number of random matchings to compute; the highest scoring is chosen.
NUM_TRIES: int = 100000
DUMMY: str = 'XXX'


def get_teaming_score(pref: Preferences, teams: [[]]) -> float:
    """Scores a teaming.

    The score is maximum when every team in the teaming consists of people who
    want to work with each other.

    Parameters:
    - pref: preferences of the teamed students.
    - teams: contains the teams which have to be scored.

    Returns:
    The score for matching.
    """
    team_scores = []
    n = len(teams[0])
    for team in teams:
        actual_score = perfect_score = 0
        for s in team:
            if s == DUMMY:
                continue
            greens = pref.get_greens(s)
            if (num_greens := min(n, len(greens))):
                actual_score += sum((1 for t in team if t in greens and t != DUMMY))
                perfect_score += num_greens
        if perfect_score:
            team_scores.append(actual_score / perfect_score)
    return sum(team_scores) / len(team_scores)


def get_pretty_string(pref: Preferences, teams: [[]]) -> str:
    """Builds and returns a string describing teams made from pref.

    Parameters:
    - pref: preferences of the teamed students.
    - teams: contains the teams which have to be scored.

    Returns:
    a string description of the teams.
    """
    strings = []
    for team in teams:
        string = []
        team = set(team)
        for s in team:
            if s == DUMMY:
                string.append(DUMMY)
                continue
            greens = set(pref.get_greens(s))
            if greens:
                if greens & team:
                    string.append(f'{Fore.GREEN}{s}{Style.RESET_ALL}')
                else:
                    string.append(f'{Fore.YELLOW}{s}{Style.RESET_ALL}')
            else:
                string.append(s)
        strings.append(','.join(string))
    return '\n'.join(strings)


def get_teams(pref: Preferences, size: int) -> [[str]]:
    """Partitions all the students whose information is in pref into teams of size.

    One of the teams is padded with dummy students, XXX, if there are not enough
    students. Students are picked in a random order and checked if they can work
    with each other. Teaming can fail if the remaining students to be teamed
    cannot work with each other.

    Parameters:
    - pref: contains the students to be teamed and their preferences.

    Returns:
    The list of teams. The list is empty if teaming fails.

    """
    # Get students to be teamed, randomize their order. Initialize dummy student
    # to be used to pad small team.
    students = pref.get_students()
    random.shuffle(students)
    # Initialize the teams and the teamed students so far.
    teams = []
    teamed = set()
    # Make as many teams of size as possible.
    while len(students) >= size:
        # Initialize empty team and add size students who can be teamed
        # together.
        team = []
        for i in range(size):
            idx = len(students) - 1
            while any([not pref.can_team(students[idx], s) for s in team]) and idx >= 0:
                idx -= 1
            # Exit with failure if teaming failed.
            if idx < 0:
                return []
            # Update team, teamed students, and remaining students.
            team.append(students[idx])
            teamed.add(students[idx])
            students.pop(idx)
        # Save team.
        teams.append(team)
    # Exit successfully if all the students have been teamed.
    if len(students) == 0:
        return teams
    # Exit with failure if the remaining students cannot be teamed.
    for src in students:
        if any([not pref.can_team(src, s) for s in students]):
            return []
    # Add team padded with dummy student, and exit successfully.
    team = students + ['XXX'] * (size - len(students))
    teams.append(team)
    return teams


# WORKS WELL ON ITS OWN. EDIT ONLY IF YOU KNOW WHAT YOU ARE DOING.


def main():
    '''Computes the best matching from input preferences.'''
    # Build graph from preferences, and mark the nodes that are
    # indifferent. Visualize the graph, and compute NUM_TRIES matchings. Store
    # the matching with the highest score. Show progress bar as matchings are
    # computed.
    filename = 'preferences.csv'
    pref = Preferences(filename)
    pref.visualize()
    high_score: int = -sys.maxsize - 1
    best_teams: {(str, str)} = set()
    progress_bar = ProgressBar("progress", NUM_TRIES)
    print(f'Making {NUM_TRIES} matching attempts:')
    progress_bar.start_progress()
    for _ in range(NUM_TRIES):
        progress_bar.update_progress(_)
        if (teams := get_teams(pref, 2)):
            teams = [tuple(sorted(t)) for t in teams]
            teams = tuple(sorted(teams))
            if (score := get_teaming_score(pref, teams)) >= high_score:
                if score > high_score:
                    high_score = score
                    best_teams.clear()
                    best_teams.add(teams)
    progress_bar.end_progress()
    # Output the best (highest scoring) match in a suitable format and its
    # score.
    print(f'{len(best_teams)} best teams with score of {high_score}')
    for teams in best_teams:
        print(f'{get_pretty_string(pref, teams)}')
        # print(teams)


if __name__ == '__main__':
    main()
