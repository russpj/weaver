#!/usr/bin/python3

# weaver
# Plays the popular game with the two words input on the command line

from sys import stdin, stdout, stderr, argv
from getopt import getopt, GetoptError
from math import log2


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


def read_words(words_file_name):
    words = []
    with open(words_file_name, "r") as words_file:
        for line in words_file:
            for word in line.split():
                words.append(word)
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
    def __init__(self, start, target, dictionary):
        self.start = start
        self.target = target
        self.dictionary = dictionary
        first_step = Step(start, 1, 0)
        self.steps = [first_step]
        return


    def print_solution(self, step_index):
        solution = []
        while True:
            step = self.steps[step_index]
            solution.append(step.word)
            if step.word == self.start:
                break
            step_index = step.previous_word
        solution.reverse()
        solution_display = '-->'.join(str(x) for x in solution)
        print(f'The solution is {solution_display}')

    def word_used_previously(self, step):
        for previous_step in self.steps:
            if previous_step.step == step.step:
                break
            if previous_step.word == step.word:
                return True
        return False


    def solve(self, verbose=False):
        if verbose:
            print(f'Find {self.target} starting with {self.start}')

        step_index = 0
        while step_index < len(self.steps):
            step = self.steps[step_index]
            if step.word == self.target:
                self.print_solution(step_index)
                break

            if (verbose):
                print(f'Looking at {step.word} at step {step.step}')
            for word in self.dictionary:
                if different_letters(step.word, word) == 1:
                    next_step = Step(word, step.step+1, step_index)
                    if not self.word_used_previously(next_step):
                        self.steps.append(next_step)
            
            step_index += 1

        return


def main(arguments):
    command_line_documentation = "Wordle.py -h -v -s -l {tapestries_file} {start_word} {end_word}"
    num_letters = 4
    dictionary_name = f"{num_letters}_letter_words.txt"
    list = ''
    verbose = False
    stats = False

    dictionary = read_words(dictionary_name)
   
    try:
        opts, args = getopt(arguments, "hvsl:", ("help", "verbose", "statistics", "list="))
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

        if opt in ('-l', '--list'):
            list = arg

    if list != '':
        keys = read_words(list)
    elif len(args) > 1:
        keys = args
    else:
        keys = ["dogs","bark"]

    if len(keys) % 2 != 0:
        print(f'Invalid Arguments: {command_line_documentation}')
        exit(2)

    while keys:
        first = keys[0]
        last = keys[1]
        keys = keys[2:]
        
        solver = Solver(first, last, dictionary)
        solver.solve(verbose)

    if stats:
        pass

if __name__ == '__main__':
    main(argv[1:])
