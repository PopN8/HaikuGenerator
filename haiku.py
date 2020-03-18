from random import randint
import sys


def first_letter_pref(lst: list, pref: str) -> list:
    return [line for line in lst if line[0].lower() == pref.lower()]


with open('haikus.txt', 'r', encoding = 'utf-8') as haikus_file:
    haikus = haikus_file.read().split('\n\n')
print(len(haikus))

first_lines = [haiku.split('\n')[0] for haiku in haikus]
second_lines = [haiku.split('\n')[1] for haiku in haikus]
third_lines = [haiku.split('\n')[2] for haiku in haikus]

if len(sys.argv) > 1:
    fl = first_letter_pref(first_lines, sys.argv[1])
    sl = first_letter_pref(second_lines, sys.argv[2])
    tl = first_letter_pref(third_lines, sys.argv[3])

    print(fl[randint(0, len(fl) - 1)])
    print(sl[randint(0, len(sl) - 1)])
    print(tl[randint(0, len(tl) - 1)])
else:
    print(first_lines[randint(0, len(haikus) - 1)])
    print(second_lines[randint(0, len(haikus) - 1)])
    print(third_lines[randint(0, len(haikus) - 1)])