import re

# This script removed the heading of a txt file

with open("hermione_dialogue.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

harry_dialogue = []

for line in lines:
    if line.startswith("Hermione:"):
        line = line.replace("Hermione:", "").strip()
        harry_dialogue.append(line)

with open("Hermione_dialogue_no.txt", "w", encoding="utf-8") as file:
    for line in harry_dialogue:
        file.write(line + '\n')
