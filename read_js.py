import json
# This script read a json file and write the data into a txt file.
# Load the JSON data
with open('en_test_set.json', 'r', encoding='utf-8') as json_file:  # Use 'utf-8' encoding to read the file
    data = json.load(json_file)

# Extract dialogues and write into a TXT file
with open('dialogue.txt', 'w', encoding='utf-8') as txt_file:
    for session in data.values():
        dialogues = session['dialogue']
        for dialogue in dialogues:
            txt_file.write(dialogue + '\n')
