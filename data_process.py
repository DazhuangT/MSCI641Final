import re
import csv
import sys
import random

# This script created dataset and labels with the given data

ori_dict = {}   # dict with raw data
token_dict = {}  # tokenized data dict
ran_token = {}  # random token data

no_stopword_dict = {}  # raw data with no stop word
no_stopword_token_dict = {}  # no stopword token
ran_ns_token = {}  # random no stopword token

train_dict = {}  # train dataset with s
valid_dict = {}  # val dataset with s
test_dict = {}  # test dataset with s

test_dict_no_stopword = {}  # rain dataset ns
valid_dict_no_stopword = {}  # val dataset ns
train_dict_no_stopword = {}  # test dataset ns

# Stopwords list found online+ I added some to it
stopword = r"\b('|didn|d|shan|couldn|doesn|don|mustn|ll|ve|re|m|shouldn|hadn|hasn|haven|aren|isn|weren|wasn|i|me|my|myself|we|our|ours|ourselves|you|your|yours|yourself|yourselves|he|him|his|himself|she|her|hers|herself|it|its|itself|they|them|their|theirs|themselves|what|which|who|whom|this|that|these|those|am|is|are|was|were|be|been|being|have|has|had|having|do|does|did|doing|a|an|the|and|but|if|or|because|as|until|while|of|at|by|for|with|about|against|between|into|through|during|before|after|above|below|to|from|up|down|in|out|on|off|over|under|again|further|then|once|here|there|when|where|why|how|all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|very|s|t|can|will|just|don|should|now)\b"

# some stopwords in the txt have cap first letter, use it to find them
cap = r"\b[A-Z][a-zA-Z]*\b"


# read txt data and save in a dictionary
def read_txt_to_dict(name, label, dict_param):
    i = 0
    with open(name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            dict_param[label + str(i)] = line.strip()
            i += 1


# this method count how many lines in a txt file, I thought it might be useful, but i didn't use it at all.
def count_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return len(lines)


# write the data from a dictionary into a csv
def write_dict_to_csv(dict_param, filename):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
        for key, value in dict_param.items():
            writer = csv.writer(file)
            writer.writerow(dict_param[key])


# remove the special characters in the data
def remove_special_mark(dict_param):
    for key, value in dict_param.items():
        dict_param[key] = re.sub(r'[_.,\-!?"#$%&()*+/:;<=>@\[\\\]^`{|}~\t\n]', ' ', dict_param[key])


# split sentence into tokens
def tokenize_dict(dict_param1, dict_param2):
    for key, value in dict_param1.items():
        tokens = value.split()
        dict_param2[key] = tokens


# this is remove stop words from dictionary to create database without stopwords
def remove_stopword_dict(dict_param):
    for key, value in dict_param.items():
        dict_param[key] = re.sub(stopword + r"|" + cap, "", dict_param[key])


# Because in python version 3.9, dict data is ordered data type, I need to random then myself, also this method saved the label of data
# the key in the dictionary is the label, i didn't create a csv for that but I can easily do that with the key in the dict
# this also split data into train, val and test
def random_split_dict_data(dict_param):
    random_dict = {}
    ran_keys = list(dict_param.keys())
    random.shuffle(ran_keys)
    for key in ran_keys:
        random_dict[key] = dict_param[key]
    data = list(random_dict.items())
    train = dict(data[:int(len(data) * 0.9)])
    valid = dict(data[int(len(data) * 0.9):int(len(data) * 1.0)])
    test = dict(data[int(len(data) * 0.9):])
    random_token = random_dict.copy()
    # print(random_token)
    random_dict.clear()
    return random_token, train, valid, test


# main method
def main():
    if len(sys.argv) > 1:
        pos = sys.argv[1]  # read the input path for pos.txt
    else:
        print("missing at least one arguments!")  # break

    if len(sys.argv) > 2:
        neg = sys.argv[2]  # read the input path for neg.txt
    else:
        print("missing at least one arguments!")  # break

    # read txt into and save data into dict
    read_txt_to_dict(pos, "Geralt of Rivia", ori_dict)
    # read_txt_to_dict(neg, "Not Geralt", ori_dict)
    read_txt_to_dict(pos, "Geralt of Rivia", no_stopword_dict)
    # read_txt_to_dict(neg, "Not Geralt", no_stopword_dict)
    # remove speical character in both version, ns and original
    remove_special_mark(ori_dict)
    # remove_stopword_dict(no_stopword_dict)  # create a dict with no stopwords
    # remove_special_mark(no_stopword_dict)

    # tokenize both dict
    tokenize_dict(ori_dict, token_dict)
    # tokenize_dict(no_stopword_dict, no_stopword_token_dict)

    # random both data set, but kept the relationship between key and value, which is also the label and data
    # this step also split the data into required data set, train,val and test
    ran_token, train_dict, valid_dict, test_dict = random_split_dict_data(token_dict)
    # ran_ns_token, train_dict_no_stopword, valid_dict_no_stopword, test_dict_no_stopword = random_split_dict_data(no_stopword_token_dict)

    # write different data set into correct csv
    # write_dict_to_csv(token_dict, "data/out.csv")
    write_dict_to_csv(train_dict, "three_train.csv")
    write_dict_to_csv(valid_dict, "three_val.csv")
    # write_dict_to_csv(test_dict, "data/gpt_test.csv")
    # write_dict_to_csv(no_stopword_token_dict, "data/out_ns.csv")
    #  write_dict_to_csv(train_dict_no_stopword, "data/train_ns.csv")
    # write_dict_to_csv(valid_dict_no_stopword, "data/val_ns.csv")
    # write_dict_to_csv(test_dict_no_stopword, "data/test_ns.csv")

    # showing the script was success complied
    print("Process Success!")

    # write_dict_to_txt(train_dict, "data/gpt_train.txt")
    # write_dict_to_txt(test_dict, "data/gpt_test.txt")
    # write_dict_to_txt(valid_dict, "data/gpt_val.txt")
    # write_dict_to_txt(train_dict_no_stopword, "data/train_ns.txt")
    # write_dict_to_txt(test_dict_no_stopword, "data/test_ns.txt")
    # write_dict_to_txt(valid_dict_no_stopword, "data/val_ns.txt")


# This method write the key of a param into a txt file
def write_dict_to_txt(dict_param, name):
    with open(name, 'w') as file:
        for key in dict_param.keys():
            file.write(key + '\n')


# compile main
if __name__ == '__main__':
    main()
