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
    
def get_match_score(pairs):
    score = 0
    for src,dst in pairs:
        if src in dst.green:
            score += 1
        if dst in src.green:
            score += 1
    return score / (2 * len(pairs))

def showProgressBar(currentScore, total):
    stepSize = total/10
    number_dec = str(currentScore/stepSize-int(currentScore/stepSize))[1:]
    if(number_dec == ".0"):
        progress(((currentScore/total)*100))    

def color_print(pairings):
    for pairing in pairings:
        to_print = ''
        for student_a, student_b in pairing:
            to_print += '('
            if student_b in student_a.green:
                to_print += f'{Fore.GREEN}{student_a.name}{Style.RESET_ALL}'
            elif student_b in student_a.red:
                to_print += f'{Fore.RED}{student_a.name}{Style.RESET_ALL}'
            else:
                to_print += student_a.name
            to_print += ', '
            if student_a in student_b.green:
                to_print += f'{Fore.GREEN}{student_b.name}{Style.RESET_ALL}'
            elif student_a in student_b.red:
                to_print += f'{Fore.RED}{student_b.name}{Style.RESET_ALL}'
            else:
                to_print += f'{student_b.name}'
            to_print += ') '
        print(to_print[:-1])        

def get_pairs(preferences : nx.DiGraph) -> [(str, str)]:
    '''Extract feasible pairs from preferences.'''
    import copy
    G = copy.deepcopy(preferences)
    G.graph['matches'] = []

    def is_mismatch(src : str, dst : str) -> bool:
        return G.has_edge(dst, src) and not G[dst][src]['pref']

    def add_match(src : str, candidates : [str]) -> bool:
        random.shuffle(candidates)
        for dst in candidates:
            pair = tuple(sorted((src, dst)))
            if not is_mismatch(*pair):
                G.graph['matches'].append(pair)
                G.remove_nodes_from(pair)
                return True
        return False
        
    while G.nodes() and (src := random.choice([*G.nodes()])):
        greens = [n for n in G.successors(src) if G[src][n]['pref']]
        if add_match(src, greens):
            continue
        non_neighbors = set(G.nodes()) - set(G.neighbors(src)) - {src}
        if not add_match(src, list(non_neighbors)):
            print('Cannot match:', src)
            print('Matches found so far:', *G.graph['matches'])
            print('Still to match:', *G)
            return []
    return G.graph['matches']

        
                
            
        


    
def enter_data(preferences : nx.DiGraph) -> None:
    '''Populates the digraph with student preferences.'''

    def add_targets(source : str, greens : [str], reds : [str]):
        for s in greens:
            preferences.add_edge(source, s, pref=True)
        for s in reds:
            preferences.add_edge(source, s, pref=False)
        
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
    print(get_pairs(preferences))
    # students = init_students()
    # max_score = -1
    # best_pairs = set()
    # num_tries = 50000
    # print(f'Pairing {len(students)} students in {num_tries} attempts.')
    # startProgress("progress")
    # for _ in range(num_tries):
    #     showProgressBar(_, num_tries)
    #     pairs = []
    #     while not pairs:
    #         pairs = get_pairs(students)
    #         reset_students(students)
    #     score = get_match_score(pairs)
    #     if score > max_score:
    #         best_pairs = {pairs}
    #         max_score = score
    #     elif score == max_score:
    #         best_pairs.add(pairs)

    # endProgress()
    # print(f'\nGot {len(best_pairs)} pairings with score of {max_score}:')
    # color_print(best_pairs)
    

if __name__ == '__main__':
    main()
