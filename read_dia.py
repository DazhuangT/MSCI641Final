import re
# This script read the a dialogue.txt and split data.

with open("dialogue.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

harry_dialogue = []

for line in lines:
    if line.startswith("Harry:"):
        harry_dialogue.append(line)

with open("harry_d.txt", "w", encoding="utf-8") as file:
    for line in harry_dialogue:
        file.write(line)

