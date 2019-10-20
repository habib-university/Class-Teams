from colorama import Fore, Style
import networkx as nx
import random
import sys

############### PROGRESS BAR FUNCTIONS BEGIN

def startProgress(title : str):
    global progress_x
    sys.stdout.write(title + ": [")
    sys.stdout.flush()
    progress_x = 0

def progress(x : int):
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

############### PROGRESS BAR FUNCTIONS END
    
def get_score_for_matching(G : nx.DiGraph, matching : [(str, str)]) -> float:
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
        
    matching = sorted([sorted(match) for match in matching])
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
            match = (src, dst)
            if not is_mismatch(*match):
                G.graph['matching'].append(match)
                G.remove_nodes_from(match)
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
    dot.format = 'png'
    dot.render(file_name, view=True)
            
def enter_data(G : nx.DiGraph) -> None:
    '''Populates the digraph with student preferences.'''

    def add_targets(src : str, greens : [str], reds : [str]):
        for n in greens:
            G.add_edge(src, n, pref=True)
        for n in reds:
            G.add_edge(src, n, pref=False)
        G.nodes[src]['pref'] = True
        
    ### EDIT: Add greens and reds below.
    add_targets("U", ["Z", "P", "W"], ["T"])
    add_targets("X", ["Z", "P", "Q"], ["T"])
    add_targets("Q", ["X", "Z", "R"], ["T"])
    add_targets("R", ["V", "S", "U"], ["T"])
    add_targets("S", ["V", "P", "U"], ["T"])
    add_targets("W", ["U", "P", "S"], ["T"])
    add_targets("Z", ["S", "U", "P"], ["T"])
    add_targets("V", ["R", "U", "P"], ["W"])
    # add_targets("Y", ["P", "R", "V"], ["T"])

    ### EDIT: Add students that are not included above but need to be matched.
    no_data = [] # populate this list with ID's.
    G.add_nodes_from(no_data)
    
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
           (score := get_score_for_matching(preferences, matching)) > high_score:
            high_score = score
            best_matching = matching
    endProgress()
    print(f'{get_pretty_string(preferences, best_matching)}\n{high_score}')
    
if __name__ == '__main__':
    main()
