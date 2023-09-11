# Define the prefix
prefix = "hermione"

# Read the file
with open("hermione.txt", "r", encoding='utf-8') as file:
    lines = file.readlines()

# Add the prefix at the beginning of each line
lines = [prefix + " " + line for line in lines]

# Write the modified content back into the file
with open("hermione_.txt", "w", encoding='utf-8') as file:
    for line in lines:
        file.write(line)
