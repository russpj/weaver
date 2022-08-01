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


class wordle:
    def __init__(self, word):
        self.key_word = word
        self.guesses = []

    def add_guess(self, guess, info):
        score = self.score_guess(guess)
        self.guesses.append((guess, score, info))

    def print_guesses(self):
        for guess in self.guesses:
            word, score, info = guess
            word_string = ""
            for letter, color in zip(word, score):
                letter_color = ansi_colors.letter_missing 
                if color == 'green':
                    letter_color = ansi_colors.letter_right_place
                if color == 'yellow':
                    letter_color = ansi_colors.letter_wrong_place
                word_string += f'{letter_color}{letter}'
            word_string += ansi_colors.normal
            
            info_string = ""
            if info:
                info_string = f"({info})"
            print(f"{word_string} ({info})")

    def score_guess(self, guess):
        return convert_score_to_colors(score_word(guess, self.key_word))

    def is_consistent_guess(self, guess):
        guess_key = wordle(guess)
        for guess in self.guesses:
            score = guess_key.score_guess(guess[0])
            if score != guess[1]:
                return False
        return True

    def solved(self):
        num_guesses = len(self.guesses)
        if num_guesses > 0:
            score = self.guesses[num_guesses-1][1]
            if score == ['green', 'green','green','green','green']:
                return True
        return False
        

def score_word(guess, target):
    score = 0
    size = len(target)
    for _ in range(size):
        score *= 10
        score += 1
    if size != len(guess):
        return score

    used_guess_indices = []
    used_target_indices = []
    for index, letter in enumerate(guess):
        if target[index] == letter:
            score += 2*10**(size-index-1)
            used_guess_indices.append(index)
            used_target_indices.append(index)
    for index, letter in enumerate(guess):
        if index not in used_guess_indices:
            for target_index, target_letter in enumerate(target):
                if target_index not in used_target_indices:
                    if letter == target_letter:
                        score += 1*10**(size-index-1)
                        used_guess_indices.append(index)
                        used_target_indices.append(target_index)
                        break
    return score


def convert_score_to_colors(score):
    colors = ['', 'grey', 'yellow', 'green']
    letters = []
    while score > 0:
        color = score % 10
        letters.append(colors[color])
        score = score // 10
    letters = list(reversed(letters))
    return letters


def add_letter_frequencies(word, frequency_table):
    letters = []
    for letter in word:
        if letter not in letters:
            letters.append(letter)
    score = 0
    for letter in letters:
        score += frequency_table[letter]
    return score


def add_letter_frequencies_adjusted(line, frequency_table, threshold_frequency, bonus_score):
    score = add_letter_frequencies(line[0], frequency_table)
    if line[1] > threshold_frequency:
        score += bonus_score
    return score


def gather_letter_frequencies(words, frequency_dictionary=None):
    table = {}
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        table[letter] = 0

    for word in words:
        if frequency_dictionary is None or not frequency_dictionary.is_plural(word):
            for letter in word:
                table[letter] += 1

    return table


def find_next_guess(game, sorted_word_list):
    for index, word in enumerate(sorted_word_list):
        if game.is_consistent_guess(word):
            return (index, word)
    return None


def read_dictionary(dictionary_file_name):
    words = []
    with open(dictionary_file_name, "r") as dictionary_file:
        for line in dictionary_file:
            for word in line.split():
                words.append(word)
    return words


def add_dictionary_words(frequency_list, dictionary):
    current_words = [line[0] for line in frequency_list]
    for word in dictionary.keys():
        if not word in current_words:
            frequency_list.append((word, 0))
    return


def get_percentile_frequency(frequency_list, threshold):
    frequency_list.sort(key=lambda line: line[1])
    percentile = int(len(frequency_list)*threshold)
    line = frequency_list[percentile]
    return line[1]


def read_keys(file):
    keys = []
    with open(file, 'r') as keys_file:
        for line in keys_file:
            keys.append(line.strip())
    return keys


def get_singular_words(frequency_dictionary):
    word_list = []
    for item in frequency_dictionary.items():
        word = item[0]
        frequency = item[1][0]
        plural = item[1][1]
        if not plural:
            word_list.append((word, frequency))
    return word_list


def get_word_list(frequency_dictionary):
    words = []
    for item in frequency_dictionary.dictionary.items():
        word = item[0]
        frequency = frequency_dictionary.frequency(word)
        words.append((word, frequency))
    return words


def solve_helper(key_word, sorted_word_list):
    game = wordle(key_word)
    solution_found = False
    while not solution_found:
        index, word = find_next_guess(game, sorted_word_list)
        if word is None:
            return None
        game.add_guess(word, index)
        solution_found = game.solved()
    return game


class frequency_dictionary():
    def __init__(self, dictionary_name, num_letters):
        self.dictionary = {}
        with open(dictionary_name, 'r') as frequency_list:
            for line in frequency_list:
                word, frequency, plural = line.strip().split('\t')
                if len(word) == num_letters:
                    entry = (int(frequency), plural == 'P')
                    self.dictionary[word] = entry
        return

    def frequency(self, word):
        return self.dictionary[word][0]

    def is_plural(self, word):
        return self.dictionary[word][1]


class old_letter_frequency_solver():
    def __init__(self, frequency_dictionary, verbose=False):
        self.frequency_dictionary = frequency_dictionary
        self.verbose = verbose
        self.calculate_word_list()
        return

    def solve(self, key):
        return solve_helper(key, self.sorted_word_list)

    def calculate_word_list(self):
        word_list = get_singular_words(self.frequency_dictionary.dictionary)
        if self.verbose:
            stderr.write(f'Read {len(word_list)} singular words to analyze')
        num_words = len(word_list)
        num_letters = len(word_list[0][0])

        frequency_table = gather_letter_frequencies([word[0] for word in word_list], self.frequency_dictionary)
        sorted_letters = sorted(frequency_table.items(), reverse=True, key=lambda item: item[1])
        if self.verbose:
            stderr.write(f"The letter frequencies:\n{sorted_letters}\n")
        add_dictionary_words(word_list, self.frequency_dictionary.dictionary)
        if self.verbose:
            stderr.write(f"Added {len(word_list)-num_words} more words from dictionary.\n")

        best_letter = sorted_letters[0][0]
        best_word =	[best_letter] * num_letters
        best_score = add_letter_frequencies(best_word, frequency_table)
        threshold_frequency = get_percentile_frequency(word_list, .75)
    
        word_list.sort(reverse=True, key=lambda line: add_letter_frequencies_adjusted(line, frequency_table, threshold_frequency, best_score))
        
        self.sorted_word_list = [word[0] for word in word_list]
        return


class new_letter_frequency_solver():
    def __init__(self, frequency_dictionary, verbose=False):
        self.frequency_dictionary = frequency_dictionary
        self.verbose = verbose
        self.calculate_word_list()
        return

    def solve(self, key):
        return solve_helper(key, self.sorted_word_list)

    def calculate_word_list(self):
        word_list = get_word_list(self.frequency_dictionary)
        num_words = len(word_list)
        num_letters = len(word_list[0][0])

        if self.verbose:
            print(f'The word list has {len(word_list)} words.')

        frequency_table = gather_letter_frequencies([word[0] for word in word_list], self.frequency_dictionary)
        sorted_letters = sorted(frequency_table.items(), reverse=True, key=lambda item: item[1])
        if self.verbose:
            stderr.write(f"The letter frequencies:\n{sorted_letters}\n")

        best_letter = sorted_letters[0][0]
        best_word =	[best_letter] * num_letters
        best_score = add_letter_frequencies(best_word, frequency_table)
        threshold_frequency = get_percentile_frequency(word_list, .75)
    
        word_list.sort(reverse=True, 
                       key=lambda line: add_letter_frequencies_adjusted(line, frequency_table, threshold_frequency, best_score))
        word_list.sort(reverse=False, 
                       key=lambda line: self.frequency_dictionary.is_plural(line[0]))
        
        self.sorted_word_list = [word[0] for word in word_list]
        return


def word_list_sorted_by_word_frequency(frequency_dictionary, verbose):
    word_list = get_word_list(frequency_dictionary)
    num_words = len(word_list)

    if verbose:
        print(f'The word list has {len(word_list)} words.')

    word_list.sort(reverse=True, 
                    key=lambda item: frequency_dictionary.frequency(item[0]))
    word_list.sort(reverse=False, 
                    key=lambda item: frequency_dictionary.is_plural(item[0]))

    return list(word[0] for word in word_list)


class word_frequency_solver():
    def __init__(self, frequency_dictionary, verbose=False):
        self.frequency_dictionary = frequency_dictionary
        self.verbose = verbose
        self.calculate_word_list()
        return

    def solve(self, key):
        return solve_helper(key, self.sorted_word_list)

    def calculate_word_list(self):
        self.sorted_word_list = word_list_sorted_by_word_frequency(self.frequency_dictionary, self.verbose)
        return


def create_guesses(word_list):
    guesses = []
    for index, word in enumerate(word_list):
        guesses.append((word, index))
    return guesses


def remove_bad_guesses(game, guesses):
    good_guesses = []
    index = 0
    for guess in guesses:
        if game.is_consistent_guess(guess[0]):
            good_guesses.append(guess)
            index += 1
    return good_guesses


def score_word_against_all(guess, word_list):
    scores = {}
    largest_bucket_size = 0
    for key in word_list:
        score = score_word(guess[0], key[0])
        if score in scores:
            scores[score] = scores[score] + 1
        else:
            scores[score] = 1
        largest_bucket_size = max(largest_bucket_size, scores[score])
    return largest_bucket_size


def entropy(guess, word_list):
    scores = {}
    for key in word_list:
        score = score_word(guess[0], key[0])
        if score in scores:
            scores[score] += 1
        else:
            scores[score] = 1
    total_keys = len(word_list)
    total_entropy = 0
    for item in scores.items():
        score = item[1]
        probability = score/total_keys
        total_entropy += probability*log2(1/probability)
    return total_entropy


def get_best_guess(candidate_words):
    best_bucket_size = len(candidate_words)
    best_word = candidate_words[0]
    for guess in candidate_words[:10]:
        largest_bucket_size = score_word_against_all(guess, candidate_words)
        if largest_bucket_size < best_bucket_size:
            best_bucket_size = largest_bucket_size
            best_word = guess
    return best_word


def find_highest_entropy(candidate_words, search_depth):
    highest_entropy = 0.0
    best_guess = candidate_words[0]
    for guess in candidate_words[0:search_depth]:
        word_entropy = entropy(guess, candidate_words)
        if word_entropy > highest_entropy:
            highest_entropy = word_entropy
            best_guess = guess
    return best_guess


class reduced_search_solver():
    best_first_guesses = {}

    def __init__(self, frequency_dictionary, search_depth=1, verbose=False):
        self.frequency_dictionary = frequency_dictionary
        self.search_depth = search_depth
        self.verbose = verbose
        self.calculate_word_list()
        return

    def solve(self, key):
        game = wordle(key)
        possible_guesses = create_guesses(self.sorted_word_list)
        while not game.solved():
            if possible_guesses:
                if len(game.guesses) == 0 and self.search_depth in reduced_search_solver.best_first_guesses:
                    guess = reduced_search_solver.best_first_guesses[self.search_depth]
                else:
                    guess = find_highest_entropy(possible_guesses, self.search_depth)
                    if len(game.guesses) == 0:
                        reduced_search_solver.best_first_guesses[self.search_depth] = guess
                game.add_guess(guess[0], guess[1])
            else:
                return None
            possible_guesses = remove_bad_guesses(game, possible_guesses)
        return game

        return solve_helper(key, self.sorted_word_list)

    def calculate_word_list(self):
        self.sorted_word_list = word_list_sorted_by_word_frequency(self.frequency_dictionary, self.verbose)
        return


def print_game_results(name, key, number_of_guesses):
    key_string = ''.join((ansi_colors.score_good, key, ansi_colors.normal))
    
    score_color = ansi_colors.score_great
    if number_of_guesses > 2:
        score_color = ansi_colors.score_good
    if number_of_guesses > 4:
        score_color = ansi_colors.score_fair
    if number_of_guesses > 6:
        score_color = ansi_colors.score_bad
    score_string = ''.join((score_color, str(number_of_guesses), ansi_colors.normal))

    print(f"{name} has solved for {key_string} in {score_string} guesses.")


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
