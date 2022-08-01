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


def read_dictionary(dictionary_file_name):
    words = []
    with open(dictionary_file_name, "r") as dictionary_file:
        for line in dictionary_file:
            for word in line.split():
                words.append(word)
    return words


def main(arguments):
    command_line_documentation = "Wordle.py -h -v -s -l {tapestries_file} {start_word} {end_word}"
    num_letters = 4
    dictionary_name = f"{num_letters}_letter_words.txt"
    list = ''
    verbose = False
    stats = False

    dictionary = read_dictionary(dictionary_name)
   
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
        keys = read_keys(list)
    elif len(args) > 1:
        keys = args
    else:
        keys = ["iamb", "poem"]

    if len(keys) % 2 != 0:
        print(f'Invalid Arguments: {command_line_documentation}')
        exit(2)

    while keys:
        first = keys[0]
        last = keys[1]
        keys = keys[2:]
        
        if verbose:
            print(f'Weaving from {first} to {last}')

    if stats:
        pass

if __name__ == '__main__':
    main(argv[1:])
