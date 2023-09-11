import nltk
import re
nltk.download('punkt')

# This script read a txt file, and then split the long paragraphs into sentences.
# Then save them into a new txt files.
# This prepare the data for create token data base
# This script used twice, once with raw data, once with expanded data.


def split_sentences(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    sentences = nltk.sent_tokenize(text)

    filtered_sentences = []
    for sentence in sentences:
        if re.search('[a-zA-Z]', sentence):  # This checks if there is at least one alphabet letter in the sentence
            filtered_sentences.append(sentence)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(filtered_sentences))

    print("Done！")


input_file = 'other_dialogue.txt'    # enter input file, replace name with any other files.
output_file = 'other.txt'  # enter output file, replace name with any other files

split_sentences(input_file, output_file)