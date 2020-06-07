#import PyDictionary
import cmudict
import syllables
import random
from random import randint
import re
import json
import traceback
import logging

logging.basicConfig(filename='testlog.log', filemode='a', level=logging.DEBUG)

d = cmudict.dict()

def get_markov_instances(lines: list) -> (dict, list):
    """
    Returns a dictionary of all words as keys with following words as a value and a list of all first words.
    :param lines lines in haikus.
    """
    regex = re.compile(r"[^a-zA-Z0-9 \-']")

    word_list = {}
    first_words = []

    for line in lines:
        words = regex.sub('', line).split(' ')
        first_words.append(words[0])

        for i, word in enumerate(words):
            if word.lower() not in word_list.keys():
                word_list[word.lower()] = []

            if i + 1 < len(words):
                if words[i + 1].lower() not in word_list[word.lower()]:
                    word_list[word.lower()].append(words[i + 1].lower())

    return word_list, first_words


def markov_instance_dict() -> (dict, list):
    """
    Returns a markovified dict of line by line analysis of the haikus.txt file + first lines.
    """
    with open('haikus.txt', 'r', encoding = 'utf-8') as haikus_file:
        lines = re.sub(r'\n\n', '\n', haikus_file.read()).splitlines()

    return get_markov_instances(lines)


def syllable_dict(lst: list) -> (dict, dict):
    """
    Returns a dict of word:syllable counts pairs and a dict of syllable count: words pairs.
    :param lst a list of all words.
    """
    word_syl_dict = {}
    syl_word_dict = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    for word in lst:
        word_syl_dict[word] = []
        if d[word]:
            for syl in d[word]:
                word_syl_dict[word].append(len([s for s in syl if s[-1].isdigit()]))
                syl_word_dict[len([s for s in syl if s[-1].isdigit()])].append(word)
        else:
            word_syl_dict[word].append(syllables.estimate(word))
            syl_word_dict[syllables.estimate(word)].append(word)

    return word_syl_dict, syl_word_dict


def full_random_line(max_syl: int, syl_word_dict: dict, lst = [], syl=0) -> list:
    """
    Returns a list of words corresponding to the syllable count.
    :param max_syl: Syllable length of the line.
    :param syl_word_dict: dict containing syllable:words pairs.
    :param lst: list of words currently in the line.
    :param syl: Current syllable count.
    """
    if syl == max_syl:
        return lst

    next_syl = randint(1, max_syl - syl)
    word_list = syl_word_dict[next_syl]
    word = word_list[randint(0, len(word_list) - 1)]

    return full_random_line(max_syl, syl_word_dict, lst + [word], syl + next_syl)


def full_random_haiku() -> str:
    """
    Returns a haiku using fully randomized words.
    """
    markov_dict = markov_instance_dict()[0]
    syl_word_dict = syllable_dict(markov_dict.keys())[1]

    first_line = ' '.join(full_random_line(5, syl_word_dict))
    second_line = ' '.join(full_random_line(7, syl_word_dict))
    third_line = ' '.join(full_random_line(5, syl_word_dict))

    return f'{first_line}\n{second_line}\n{third_line}'


def markov_random_line(max_syl: int, first_words_lst: list, word_syl_dict: dict, markov_dict: dict, lst = [], syl=0) -> list:
    """
    Returns a line using a dict organized as a markov chain.
    May return None therefore seeding must be ajusted
    :param max_syl: Syllable length of the line.
    :param first_words_lst: list of all first words from haikus.
    :param word_syl_dict: dictionnary of words with their syllable count.
    :param markov_dict: markov chain dictionary.
    :param lst: list of words currently in the line.
    :param syl: Current syllable count.
    """
    if syl == max_syl:
        return lst

    if syl == 0:
        word = first_words_lst[randint(0, len(first_words_lst) - 1)]
        next_syl = word_syl_dict[word.lower()][randint(0, len(word_syl_dict[word.lower()]) - 1)]
        return markov_random_line(max_syl, first_words_lst, word_syl_dict, markov_dict, lst + [word.lower()], syl + next_syl)

    if syl > max_syl:
        return None

    logging.debug(lst)
    word_pool = markov_dict[lst[len(lst) - 1]].copy()
    while word_pool:
        word = word_pool.pop(randint(0, len(word_pool) - 1))
        word_syls = word_syl_dict[word.lower()].copy()
        while word_syls:
            next_syl = word_syls.pop(randint(0, len(word_syls) - 1))
            next_line = markov_random_line(max_syl, first_words_lst, word_syl_dict, markov_dict, lst + [word.lower()], syl + next_syl)
            # print(next_line)
            if next_line is not None:
                # print(next_line)
                return next_line

    return None


def markov_random_line_2(max_syl: int, first_words_lst: list, word_syl_dict: dict, markov_dict: dict, lst = []) -> list:
    first_words_dict = dict((k, word_syl_dict[k]) for k in first_words_lst)

    while first_words_dict:
        word = random.choice(list(first_words_dict))
        lst[0] = word
        syl = first_words_dict[word][randint(0, len(first_words_dict[word.lower()]) - 1)]

        if syl == max_syl:
            return lst

        first_words_dict[word].remove(syl)

        if syl > max_syl:
            continue

        if not first_words_dict[word]:
            first_words_dict.pop(word)

        while syl < max_syl:
            word_pool = markov_dict[word].copy()

            # While current word candidates are not empty
            while word_pool:
                word = word_pool.pop(randint(0, len(word_pool) - 1))
                word_syls = word_syl_dict[word.lower()].copy()

                # While next word candidate has available syllable counts
                while word_syls:
                    word_syl = word_syls.pop(randint(0, len(word_syls) - 1))
                    if syl + word_syl > max_syl:
                        continue

                    lst.append(word)
                    syl += word_syl
                    if syl == max_syl:
                        return lst

                    break

                # word_pool.remove(word)


def markov_random_line3(max_syl: int, word_syl_dict: dict, markov_dict: dict, lst: list, syl=0) -> list:
    """
    Returns a line using a dict organized as a markov chain.
    May return None therefore seeding must be ajusted
    :param max_syl: Syllable length of the line.
    :param first_words_lst: list of all first words from haikus.
    :param word_syl_dict: dictionnary of words with their syllable count.
    :param markov_dict: markov chain dictionary.
    :param lst: list of words currently in the line.
    :param syl: Current syllable count.
    """
    if syl == max_syl:
        return lst

    if syl > max_syl:
        return None

    logging.debug(lst)
    word_pool = markov_dict[lst[len(lst) - 1]].copy()
    while word_pool:
        word = word_pool.pop(randint(0, len(word_pool) - 1))
        word_syls = word_syl_dict[word.lower()].copy()
        while word_syls:
            next_syl = word_syls.pop(randint(0, len(word_syls) - 1))
            next_line = markov_random_line3(max_syl, word_syl_dict, markov_dict, lst + [word.lower()], syl + next_syl)
            if next_line is not None:
                return next_line

    return None


def markov_first_word(max_syl: int, first_words_lst: list, word_syl_dict: dict, markov_dict: dict, syl=0) -> list:
    """
    Returns a line using a dict organized as a markov chain.
    May return None therefore seeding must be ajusted
    :param max_syl: Syllable length of the line.
    :param first_words_lst: list of all first words from haikus.
    :param word_syl_dict: dictionnary of words with their syllable count.
    :param markov_dict: markov chain dictionary.
    :param lst: list of words currently in the line.
    :param syl: Current syllable count.
    """
    while first_words_lst:
        word = first_words_lst.pop(randint(0, len(first_words_lst) - 1))
        potential_syls = word_syl_dict[word.lower()]

        while potential_syls:
            next_syl = potential_syls.pop(randint(0, len(word_syl_dict[word.lower()]) - 1))

            if next_syl > max_syl:
                continue
            line = markov_random_line3(max_syl, word_syl_dict, markov_dict, [word.lower()], next_syl)

            if line is None:
                continue
            else:
                return line

    return None


def markov_random_haiku2() -> str:
    markov_dict, first_words = markov_instance_dict()
    word_syl_dict, syl_word_dict = syllable_dict(markov_dict.keys())

    fl = markov_first_word(5, first_words, word_syl_dict, markov_dict)
    sl = markov_first_word(7, first_words, word_syl_dict, markov_dict)
    tl = markov_first_word(5, first_words, word_syl_dict, markov_dict)
    print(f'{fl}\n{sl}\n{tl}')
    first_line = ' '.join(fl)
    second_line = ' '.join(sl)
    third_line = ' '.join(tl)

    return f'{first_line}\n{second_line}\n{third_line}'


def markov_random_haiku() -> str:
    markov_dict, first_words = markov_instance_dict()
    word_syl_dict, syl_word_dict = syllable_dict(markov_dict.keys())

    fl = markov_random_line(5, first_words, word_syl_dict, markov_dict)
    sl = markov_random_line(7, first_words, word_syl_dict, markov_dict)
    tl = markov_random_line(5, first_words, word_syl_dict, markov_dict)
    print(f'{fl}\n{sl}\n{tl}')
    first_line = ' '.join(fl)
    second_line = ' '.join(sl)
    third_line = ' '.join(tl)

    return f'{first_line}\n{second_line}\n{third_line}'


if __name__ == "__main__":
    with open('haiku_occ.json', 'w') as f:
        json.dump(markov_instance_dict(), f)
    """
    try:
        haiku = markov_random_haiku()
        print(haiku)
        logging.debug(haiku)

        with open('markov_random_haiku.txt', 'a') as f:
            f.write(f'{haiku}\n\n')
    except:
        traceback.print_exc()
        logging.exception('Exception in haiku handling')
    finally:
        input()
    """

    try:
        haiku = markov_random_haiku2()
        print(haiku)
        logging.debug(haiku)

        with open('markov_random_haiku.txt', 'a') as f:
            f.write(f'{haiku}\n\n')
    except:
        traceback.print_exc()
        logging.exception('Exception in haiku handling')
    finally:
        input()

    #print(len(markov_instance_dict().keys()))
    #input()

    #with open('full_random.txt', 'a') as f:
    #    f.write(f'{full_random_haiku()}\n\n')
