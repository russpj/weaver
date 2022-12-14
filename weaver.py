#!/usr/bin/python3

# weaver
# Plays the popular game with the two words input on the command line

from sys import argv
from getopt import getopt, GetoptError
from time import process_time
from collections import deque


class ansi_colors:
    letter_right_place = '\033[32m'
    letter_wrong_place = '\033[33m'
    letter_missing = '\033[37m'
    bold = '\033[1m'
    normal = '\033[0m'
    score_great = '\033[1m\033[32m'
    score_good = '\033[32m'
    score_fair = '\033[33m'
    score_bad = '\033[31m'


def bold_text(text):
    return f'{ansi_colors.bold}{text}{ansi_colors.normal}'


def convert_score_to_colors(score):
    colors = ['', 'grey', 'yellow', 'green']
    letters = []
    while score > 0:
        color = score % 10
        letters.append(colors[color])
        score = score // 10
    letters = list(reversed(letters))
    return letters


def read_words(words_file_name, bad_words=set(), verbose=False):
    words = []
    with open(words_file_name, "r") as words_file:
        for line in words_file:
            for word in line.split():
                if word not in bad_words:
                    words.append(word)
                else:
                    if verbose:
                        print(f'Removing {word}.')      

    return words


def different_letters(word1, word2):
    differences = 0
    for letter1, letter2 in zip(word1, word2):
        if letter1 != letter2:
            differences += 1
    return differences


class Step:
    def __init__(self, word, step, previous_word):
        self.word = word
        self.step = step
        self.previous_word = previous_word
        return


class Solver:
    def __init__(self, start, target, dictionary, verbose=False, find_paths=False):
        self.target = target
        self.dictionary = dictionary
        first_step = Step(start, 0, 0)
        self.steps = [first_step]
        self.verbose = verbose
        self.find_paths = find_paths
        self.solutions_found = False
        self.solutions_level = -1
        self.stop_solver = False
        self.solutions = []
        self.previous_words = {}

    def print_solution(self, step_index):
        solution = []
        while True:
            step = self.steps[step_index]
            solution.append(step.word)
            if step.step == 0:
                break
            step_index = step.previous_word
        solution.reverse()
        solution_display = '-->'.join(str(x) for x in solution)
        print(f'{solution_display}')

    def print_solutions(self):
        print(f'{len(self.solutions)} {self.solutions_level}-step solutions')
        for solution in self.solutions:
            self.print_solution(solution)
       
    def word_used_previously(self, step):
        if step.word in self.previous_words:
            if step.step > self.previous_words[step.word]:
                return True
        return False

    def add_step(self, step):
        if self.solutions_found and step.step > self.solutions_level:
            self.stop_solver = True
            return
        target_found = step.word == self.target
        new_word = not self.word_used_previously(step)
        if target_found or new_word:
            step_index = len(self.steps)
            self.steps.append(step)
            if new_word:
                self.previous_words[step.word] = step.step
            if target_found:
                if not self.solutions_found:
                    self.solutions_found = True
                    self.solutions_level = step.step
                self.solutions.append(step_index)

    def solve(self):
        if self.verbose:
            print(f'Find {self.target} starting with {self.steps[0].word}')
            
        if self.target not in self.dictionary:
            print(f'Cannot reach {self.target} with this dictionary.')
            return

        step_index = 0
        while not self.stop_solver and step_index < len(self.steps):
            step = self.steps[step_index]
            
            if self.verbose:
                print(f'Looking at {step.word} at step {step.step}')
            
            for word in self.dictionary:
                if different_letters(step.word, word) == 1:
                    next_step = Step(word, step.step+1, step_index)
                    self.add_step(next_step)

            step_index += 1


class Counter:
    def __init__(self, dictionary, verbose=False):
        self.dictionary = dictionary
        self.verbose = verbose  
        self.found_words = {}
        self.next_words = deque()
        
    def add_word(self, word, step):
        if word not in self.found_words:
            if self.verbose:
                print(f'Adding {word}')
            self.next_words.append((word, step))
            self.found_words[word] = step

    def count(self, start):
        self.found_words = {}
        self.next_words = deque()
        self.add_word(start, 0)
        while self.next_words:
            current_word, step = self.next_words.popleft()
            for next_word in self.dictionary:
                if different_letters(current_word, next_word) == 1:
                    self.add_word(next_word, step+1)

    def print_info(self):
        return


def run_test(test, dictionary, verbose):
    start = test[0]
    target = test[1]
    num_solutions = test[2]
    solution_length = test[3]
    solver = Solver(start, target, dictionary, verbose)
    solver.solve()
    if len(solver.solutions) != num_solutions or solver.solutions_level != solution_length:
        print(f'{start}-->{target} test failed:') 
        print(f'found {len(solver.solutions)} solutions of length {solver.solutions_level} ')
        print(f'expected {num_solutions} of {solution_length}')
        return False
    return True

def main(arguments):
    command_line_documentation = "Wordle.py -h -v -s -c -p -l -e {word_to_eliminate} {tapestries_file} {start_word} {end_word}"
    num_letters = 4
    dictionary_name = f"{num_letters}_letter_words.txt"
    list_file = ''
    verbose = False
    stats = False
    count = False
    find_paths = False
    test = False
    bad_words = set()

    try:
        opts, args = getopt(arguments, "hvscpte:l:", 
            ("help", "verbose", "statistics", "count", "paths", "test", "eliminate=", "list="))
    except GetoptError:
        print(f'Invalid Arguments: {command_line_documentation}')
        exit(2)

    for opt, arg in opts:	
        if opt in ('-h', '--help'):
            print(command_line_documentation)
            exit(0)

        if opt in ('-v', '--verbose'):
            verbose = True

        if opt in ('-s', '--statistics'):
            stats = True

        if opt in ('-c', '--count'):
            count = True

        if opt in ('-p', '--paths'):
            find_paths = True

        if opt in ('-t', '--test'):
            test = True

        if opt in ('-e', '--eliminate'):
            bad_words.add(arg)

        if opt in ('-l', '--list'):
            list_file = arg

    if list_file != '':
        keys = read_words(list_file)
    else:
        keys = args

    dictionary = read_words(dictionary_name, bad_words, verbose)
   
    start_time = process_time()
    if count or find_paths:
        if len(keys) == 0:
            keys = dictionary
        sets = []
        counter = Counter(dictionary, verbose)
        printed_words = {}
        for starting_word in keys:
            if find_paths or starting_word not in printed_words:
                counter.count(starting_word)
                sets.append(counter.found_words)
                if count:
                    printed_words = {**printed_words, **counter.found_words}

        print(f'Found {len(sets)} connected sets across {len(keys)} words.')
        if count:
            total_words_found = 0
            for reachable_set in sets:
                print(f'found a set of {len(reachable_set)} words:', end='')
                total_words_found += len(reachable_set)
                for output_word in reachable_set:
                    print(f'{output_word} ', end='')
                print()
            print (f'{total_words_found} total words found')

        if find_paths:
            for reachable_set in sets:
                if verbose:
                    print(reachable_set)
                words = list(reachable_set.keys())
                start_word = words[0]
                max_depth = reachable_set[words[len(words)-1]]
                print(f'{start_word} {max_depth} ', end='')
                for word in reversed(words):
                    if reachable_set[word] == max_depth:
                        print(f'{word} ', end='')
                    else:
                        break
                print ()

    elif test:
        tests = [
            ['oaky', 'wine', 7, 5],
            ['soft', 'ware', 3, 4],
            ['stay', 'woke', 1, 7],
            ['very', 'much', 2, 6],
            ['wham', 'boom', 8, 6],
            ['fear', 'calm', 2, 5],
            ['iamb', 'poet', 23, 7],
            ['palm', 'read', 1, 5]
        ]

        all_tests_passed = True # so far
        for test in tests:
            passed = run_test(test, dictionary, verbose)
            if not passed:
                all_tests_passed = False
        if all_tests_passed:
            print('All Tests Passed!')

    else:
        while keys:
            first = keys[0]
            last = keys[1]
            keys = keys[2:]

            solver = Solver(first, last, dictionary, verbose)
            solver.solve()
            solver.print_solutions()

    end_time = process_time()

    if stats:
        print(f'Duration: {end_time - start_time} seconds')


if __name__ == '__main__':
    if len(argv[1:]) == 0:
        command_line = input('Enter the command line: ')
        cl_arguments = command_line.split()
        argv.extend(cl_arguments)

    main(argv[1:])
