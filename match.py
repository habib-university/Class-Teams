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

def showProgressBar(currentScore : int, total: int):
    stepSize = total/10
    number_dec = str(currentScore/stepSize-int(currentScore/stepSize))[1:]
    if(number_dec == ".0"):
        progress(((currentScore/total)*100))    
    
def get_matching_score(G : nx.DiGraph, matching : [(str, str)]) -> float:
    score = sum((1 for src, dst in matching
                 if G.has_edge(src, dst) and G[src][dst]['pref']))
    score += sum((1 for src, dst in matching
                  if G.has_edge(dst, src) and G[dst][src]['pref']))
    perfect_score = sum((1 for n in G.nodes() if G.nodes[n]['pref']))
    return score / perfect_score

def get_pretty_string(G : nx.DiGraph, matching : [(str, str)]) -> str:
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

def get_matching(preferences : nx.DiGraph) -> [(str, str)]:
    '''Extract feasible matching from preferences.'''
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

def visualize(G : nx.DiGraph) -> None:
    from graphviz import Digraph
    file_name = "preferences"
    dot = Digraph()
    dot.attr('edge', color = 'darkgreen:red')
    for src,dst in G.edges():
        if G[src][dst]['pref']:
            dot.edge(src,dst, color='darkgreen' )
        else:
            dot.edge(src,dst, color='red' )
    dot.render(file_name, view=True)
            
def enter_data(preferences : nx.DiGraph) -> None:
    '''Populates the digraph with student preferences.'''

    def add_targets(src : str, greens : [str], reds : [str]):
        for n in greens:
            preferences.add_edge(src, n, pref=True)
        for n in reds:
            preferences.add_edge(src, n, pref=False)
        preferences.nodes[src]['pref'] = True
        
    ### EDIT: Add red and green edges below.
    add_targets("A", ["B", "C", "D"], ["E"])
    add_targets("F", ["G", "H", "D"], ["I", "E"])
    add_targets("J", ["K", "H", "L"], ["A", "C"])
    add_targets("M", ["J", "N"], ["G"])
    add_targets("O", ["N", "P", "K"], ["Q", "R"])
    add_targets("Q", ["A", "J", "N"], ["I", "S"])
    add_targets("H", ["G", "F", "T"], ["I"])
    add_targets("T", ["A", "N", "J"], ["I"])
    add_targets("R", ["P", "U", "G"], ["L", "K"])
    add_targets("N", ["J", "L", "A"], ["Q", "O"])
    add_targets("P", ["R", "U", "D"], ["Q", "K"])
    add_targets("C", ["A", "B", "D"], ["E"])
    add_targets("U", ["P", "R", "G"], ["I", "E"])
    add_targets("G", ["H", "F", "J"], ["I"])
    add_targets("L", ["J", "F", "A"], ["N", "I"])
    add_targets("V", ["A", "L", "R"], ["Q", "I"])
    add_targets("I", ["T", "N", "A"], ["Q", "V"])
    add_targets("W", ["T", "N", "D"], ["G", "V"])
    add_targets("E", ["I", "B", "Q"], ["L", "U"])
    add_targets("B", ["A", "C", "D"], ["E"])
    add_targets("X", ["F", "Q", "J"], ["H", "L"])
    add_targets("D", ["F", "A", "B"], ["Q"])
    add_targets("S", ["A", "C", "B"], ["E"])

### WORKS WELL ON ITS OWN. EDIT IF YOU KNOW WHAT YOU ARE DOING. 
def main():
    preferences = nx.DiGraph()
    enter_data(preferences)
    visualize(preferences)
    for n in preferences.nodes():
        preferences.nodes[n].setdefault('pref', False)
    num_tries : int = 10000
    high_score : int = -1
    best_matching : [(str, str)] = []
    startProgress("progress")
    for _ in range(num_tries):
        showProgressBar(_, num_tries)
        if (matching := get_matching(preferences)) and \
           (score := get_matching_score(preferences, matching)) > high_score:
            high_score = score
            best_matching = matching
    endProgress()
    print(f'{get_pretty_string(preferences, best_matching)}\n{high_score}')
    
if __name__ == '__main__':
    main()
