import re
import json

with open('beemovie.txt', 'r', encoding='utf-8') as f:
    txt = f.read()

regex = re.compile('[^a-zA-Z ]')
clean_text = regex.sub('', txt)

word_list = clean_text.lower().split()

word_stats = {}

for word in word_list:
    if word not in word_stats:
        word_stats[word] = 1
    else:
        word_stats[word] += 1

with open('wordstats.json', 'w', encoding='utf-8') as f:
    json.dump(word_stats, f)