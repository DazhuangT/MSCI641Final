import nltk
import random
from nltk.corpus import wordnet
# This script apply the Data augmentation method to some data
# Have to download the following before the script running
nltk.download('punkt')
nltk.download('wordnet')


# This method transforming a sentence. Three ways: random deletion, random disturb and random insertion
def random_transform(sentence, op, n=1):
    words = nltk.word_tokenize(sentence)
    new_words = words.copy()
    # Filter words to only include alphanumeric characters
    words = [word for word in words if word.isalnum()]
    n = min(n, len(words))  # Limit the value of n not to exceed the total number of words
    for _ in range(n):
        if op == 'insertion':  # random insertion method
            word_to_insert = random.choice(words)
            new_words.insert(random.randint(0, len(new_words) - 1), word_to_insert)
        elif op == 'deletion':  # random deletion method
            word_to_delete = random.choice(words)
            new_words.remove(word_to_delete)
        elif op == 'disturb':  # random disturb word insert method
            random_word = get_random_word()
            new_words.insert(random.randint(0, len(new_words) - 1), random_word)
    new_sentence = ' '.join(new_words)
    return new_sentence


# This method get random word from nltk wordnet
def get_random_word():
    word_list = list(wordnet.words())
    random_word = random.choice(word_list)
    return random_word


operations = ['insertion', 'deletion', 'disturb']
weights = [0.5, 0.4, 0.1]  # choose the weight of different method

# save new dataset
with open('hermione_dialogue.txt', 'a', encoding='utf-8') as outfile:  # Note that we're appending to the file now ('a')
    with open('hermione_dialogue_no.txt', 'r', encoding='utf-8') as infile:  # Replace the name with any dataset you collected
        for line in infile:
            # Remove double quotes from the line
            line = line.replace('"', '')
            outfile.write(line)  # write the original sentence first
            # expand dataset by 2 times
            for _ in range(1):
                chosen_operations_list = random.choices(operations, weights, k=1)
                chosen_operation = chosen_operations_list[0]
                expanded_line = random_transform(line, chosen_operation)
                expanded_line = expanded_line.replace('"', '')
                outfile.write(expanded_line + '\n')  # then write the expanded sentences
