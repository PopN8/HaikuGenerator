#import PyDictionary
import cmudict
import syllables
from random import randint
import re

d = cmudict.dict()

def get_instances(lines: list) -> dict:
    """
    Returns a dictionary of all words as keys
    """
    regex = re.compile(r"[^a-zA-Z0-9 \-']")

    word_list = {}
    for line in lines:

        words = regex.sub('', line).split(' ')

        for i, word in enumerate(words):
            if word.lower() not in word_list.keys():
                word_list[word.lower()] = []

            if i + 1 < len(words):
                word_list[word.lower()].append(words[i + 1])

    return word_list


def instance_dict() -> dict:
    with open('haikus.txt', 'r', encoding = 'utf-8') as haikus_file:
        lines = re.sub(r'\n\n', '\n', haikus_file.read()).splitlines()

    return get_instances(lines)


def syllable_dict(lst: list) -> (dict, dict):
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
    if syl == max_syl:
        return lst

    next_syl = randint(1, max_syl - syl)
    word_list = syl_word_dict[next_syl]
    word = word_list[randint(0, len(word_list) - 1)]

    return full_random_line(max_syl, syl_word_dict, lst + [word], syl + next_syl)


def full_random_haiku() -> str:
    word_syl_dict, syl_word_dict = syllable_dict(instance_dict().keys())

    first_line = ' '.join(full_random_line(5, syl_word_dict))
    second_line = ' '.join(full_random_line(7, syl_word_dict))
    third_line = ' '.join(full_random_line(5, syl_word_dict))

    return f'{first_line}\n{second_line}\n{third_line}'


if __name__ == "__main__":
    #with open('haiku_occ.txt', 'w') as f:
    #    f.write(str(instance_dict()))

    #print(len(instance_dict().keys()))
    #input()

    with open('full_random.txt', 'a') as f:
        f.write(f'{full_random_haiku()}\n\n')
