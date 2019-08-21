from colorama import Fore, Style
import random, os

class Student:
    def __init__(self, name):
        self.name = name
        self.green = set()
        self.red = set()
        self.paired = False
        
    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name
    
    def __hash__(self):
        # makes instances hashable so they can be added to a dict or set.
        return hash((self.name))

    def __lt__(self, other):
        # less than operator for comparing instances.
        return self.name < other.name

def find_student(students, key):
    return next(student for student in students if student.name == key)

def add_green(students, src_name, dst_names):
    src = find_student(students, src_name)
    dst_list = filter(lambda s: s.name in dst_names, students)
    src.green.update(dst_list)

def add_red(students, src_name, dst_names):
    src = find_student(students, src_name)
    dst_list = filter(lambda s: s.name in dst_names, students)
    src.red.update(dst_list)

def is_valid_pair(s1, s2):
    return (s1 != s2) and not s1.paired and not s2.paired and (s1 not in s2.red) and (s2 not in s1.red)

def find_match(src, candidates, max_tries = 10):
    if candidates:
        for _ in range(max_tries):
            dst = random.sample(candidates, 1)[0]
            if is_valid_pair(src, dst):
                return dst

def get_pairs(students, max_tries = 100):
    students = students.copy()
    pairs = []
    tries = 0
    while students and tries < max_tries:
        src = random.sample(students, 1)[0]
        # print(f'{tries}. Finding match for {src}')
        dst = find_match(src, src.green)
        if not dst:
            dst = find_match(src, students)
        if dst:
            # print(f'Matched with {dst}')
            pair = (src, dst)
            src.paired = dst.paired = True
            students.difference_update(pair)
            pairs.append(pair)
        # else:
            # print("Couldn't match.")
        tries += 1
    if tries < max_tries:
        # print(f'Found pairing: {pairs}')
        pairs = [tuple(sorted(pair)) for pair in pairs]
        pairs = tuple(sorted(pairs))
        return pairs

def reset_students(students):
    for s in students:
        s.paired = False
    
def get_match_score(pairs):
    score = 0
    for src,dst in pairs:
        if src in dst.green:
            score += 1
        if dst in src.green:
            score += 1
    return score / (2 * len(pairs))

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def showProgressBar(currentScore, total):
    stepSize = total/10
    number_dec = str(currentScore/stepSize-int(currentScore/stepSize))[1:]
    if(number_dec == ".0"):
      cls()
      for i in range (int(currentScore/stepSize)):
          print(".", end ="")
      print("")
      for i in range (10-int(currentScore/stepSize)):
          print(" ", end ="")
      print("|", end ="")
    

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

def init_students():
    ### EDIT: Enter names of students in this list.
    students = [chr(ord('B')+i) for i in range(8)]
    
    ### DO NOT EDIT
    students = {Student(name) for name in students}

    ### EDIT: Add red and green edges below.
    add_green(students, 'B', ['E'])
    add_green(students, 'C', ['G'])
    add_red(students, 'C', ['I'])
    add_green(students, 'D', ['H', 'C'])
    add_red(students, 'D', ['I'])
    add_green(students, 'E', ['B'])
    add_green(students, 'F', ['D', 'C'])
    add_red(students, 'F', ['H'])
    add_green(students, 'G', ['H'])
    add_red(students, 'G', ['E'])
    add_green(students, 'H', ['G'])
    add_red(students, 'H', ['D'])
    add_green(students, 'I', ['G', 'C'])
    add_red(students, 'I', ['D'])
    
    ### DO NOT EDIT
    return students

### WORKS WELL ON ITS OWN. EDIT IF YOU KNOW WHAT YOU ARE DOING. 
def main():
    students = init_students()
    pairs = []
    while not pairs:
        reset_students(students)
        pairs = get_pairs(students)
    max_score = get_match_score(pairs)
    best_pairs = {pairs}
    for _ in range(1000):
        showProgressBar(_, 1000)
        pairs = []
        while not pairs:
            reset_students(students)
            pairs = get_pairs(students)
        score = get_match_score(pairs)
        if score > max_score:
            best_pairs = {pairs}
            max_score = score
        elif score == max_score:
            best_pairs.add(pairs)

    print(f'\nGot {len(best_pairs)} pairings with score of {max_score}:')
    color_print(best_pairs)

if __name__ == '__main__':
    main()
