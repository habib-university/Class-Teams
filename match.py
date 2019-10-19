from colorama import Fore, Style
import networkx as nx
import random
import sys

def startProgress(title):
    global progress_x
    sys.stdout.write(title + ": [")
    sys.stdout.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x

def endProgress():
    sys.stdout.write("#" * (40 - progress_x) + "]\n")
    sys.stdout.flush()
    
def get_matching_score(G, pairs):
    score = sum((1 for src, dst in pairs
                 if G.has_edge(src, dst) and G[src][dst]['pref']))
    score += sum((1 for src, dst in pairs
                  if G.has_edge(dst, src) and G[dst][src]['pref']))
    perfect_score = sum((1 for n in G.nodes() if G.nodes[n]['pref']))
    return score / perfect_score

def showProgressBar(currentScore, total):
    stepSize = total/10
    number_dec = str(currentScore/stepSize-int(currentScore/stepSize))[1:]
    if(number_dec == ".0"):
        progress(((currentScore/total)*100))    

def pretty_string(G, matching):
    def get_color_string(src : str, dst : str) -> str:
        if not G.has_edge(src, dst):
            if G.nodes[src]['pref']:
                return f'{Fore.YELLOW}{src}{Style.RESET_ALL}'
            return src
        elif G[src][dst]['pref']:
            return f'{Fore.GREEN}{src}{Style.RESET_ALL}'
        else:
            return f'{Fore.RED}{src}{Style.RESET_ALL}'
        
    matching = sorted([sorted(pair) for pair in matching])
    to_print = [f'({get_color_string(src, dst)}, {get_color_string(dst, src)})'
                for src, dst in matching]
    return ', '.join(to_print)

def get_pairs(preferences : nx.DiGraph) -> ([(str, str)], bool):
    '''Extract feasible pairs from preferences.'''
    import copy
    G = copy.deepcopy(preferences)
    G.graph['matching'] = []

    def is_mismatch(src : str, dst : str) -> bool:
        return G.has_edge(dst, src) and not G[dst][src]['pref']

    def add_match(src : str, candidates : [str]) -> bool:
        random.shuffle(candidates)
        for dst in candidates:
            pair = (src, dst)
            if not is_mismatch(*pair):
                G.graph['matching'].append(pair)
                G.remove_nodes_from(pair)
                return True
        return False
        
    while G.nodes() and (src := random.choice([*G.nodes()])):
        greens = [n for n in G.successors(src) if G[src][n]['pref']]
        if add_match(src, greens):
            continue
        non_neighbors = set(G.nodes()) - set(G.neighbors(src)) - {src}
        if not add_match(src, list(non_neighbors)):
            return []
    return G.graph['matching']
    
def enter_data(preferences : nx.DiGraph) -> None:
    '''Populates the digraph with student preferences.'''

    def add_targets(src : str, greens : [str], reds : [str]):
        for n in greens:
            preferences.add_edge(src, n, pref=True)
        for n in reds:
            preferences.add_edge(src, n, pref=False)
        preferences.nodes[src]['pref'] = True
        
    ### EDIT: Add red and green edges below.
    add_targets("Omema", ["Salma", "Aiman", "Muzammil"], ["Peshawarwala"])
    add_targets("Munawwar", ["Warisha", "Nofil", "Muzammil"],
                ["Hasan", "Peshawarwala"])
    add_targets("Shams", ["Saad", "Nofil", "Anand"], ["Omema", "Aiman"])
    add_targets("Arif", ["Shams", "Arhum"], ["Warisha"])
    add_targets("Marium", ["Arhum", "Neha", "Saad"], ["Amin", "Mehak"])
    add_targets("Amin", ["Omema", "Shams", "Arhum"], ["Hasan", "Fatima"])
    add_targets("Nofil", ["Warisha", "Munawwar", "Sabihul"], ["Hasan"])
    add_targets("Sabihul", ["Omema", "Arhum", "Shams"], ["Hasan"])
    add_targets("Mehak", ["Neha", "Rida", "Warisha"], ["Anand", "Saad"])
    add_targets("Arhum", ["Shams", "Anand", "Omema"], ["Amin", "Marium"])
    add_targets("Neha", ["Mehak", "Rida", "Muzammil"], ["Amin", "Saad"])
    add_targets("Aiman", ["Omema", "Salma", "Muzammil"], ["Peshawarwala"])
    add_targets("Rida", ["Neha", "Mehak", "Warisha"], ["Hasan", "Peshawarwala"])
    add_targets("Warisha", ["Nofil", "Munawwar", "Shams"], ["Hasan"])
    add_targets("Anand", ["Shams", "Munawwar", "Omema"], ["Arhum", "Hasan"])
    add_targets("Mahdi", ["Omema", "Anand", "Mehak"], ["Amin", "Hasan"])
    add_targets("Hasan", ["Sabihul", "Arhum", "Omema"], ["Amin", "Mahdi"])
    add_targets("Ozair", ["Sabihul", "Arhum", "Muzammil"], ["Warisha", "Mahdi"])
    add_targets("Peshawarwala", ["Hasan", "Salma", "Amin"], ["Anand", "Rida"])
    add_targets("Salma", ["Omema", "Aiman", "Muzammil"], ["Peshawarwala"])
    add_targets("Ali", ["Munawwar", "Amin", "Shams"], ["Nofil", "Anand"])
    add_targets("Muzammil", ["Munawwar", "Omema", "Salma"], ["Amin"])
    add_targets("Fatima", ["Omema", "Aiman", "Salma"], ["Peshawarwala"])

### WORKS WELL ON ITS OWN. EDIT IF YOU KNOW WHAT YOU ARE DOING. 
def main():
    preferences = nx.DiGraph()
    enter_data(preferences)
    for n in preferences.nodes():
        # preferences.nodes[n]['pref'] = preferences.nodes[n].get('pref', False)
        preferences.nodes[n].setdefault('pref', False)
    [print(n,preferences.nodes[n]['pref']) for n in preferences.nodes()]
    num_tries : int = 5000
    high_score : int = -1
    best_matching : [(str, str)] = []
    startProgress("progress")
    for _ in range(num_tries):
        showProgressBar(_, num_tries)
        if (matching := get_pairs(preferences)) and \
           (score := get_matching_score(preferences, matching)) > high_score:
            high_score = score
            best_matching = matching
    endProgress()
    print(f'{pretty_string(preferences, best_matching)}\n{high_score}')
    

if __name__ == '__main__':
    main()
