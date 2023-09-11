import sys
import csv
import pickle
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from method import do_nothing  # please put method.py under the same folder of inference and main python file

# This script training a bayes classifier with input data.

test = []  # test data array
val = []  # val data array
train = []  # train data array

test_ns = []  # test data without stopwords array
val_ns = []  # val data without stopwords array
train_ns = []  # train data without stopwords array

path = ""  # input folder path


# get the data label from the txt file I saved, also please save all extra txt files under the same folder with all csv files, i assumened they saved under same path
# Removed all the numbers from key they leave on two labels" Geralt of Rivia and Not Geralt
def get_label(file):
    with open(file, "r", encoding='utf-8') as f:
        label = [line.translate(str.maketrans("", "", "0123456789\n")) for line in f.readlines()]  # remove the numbers from key
    return label


# get the actul data from csv files, pleased save all csv files along with it's label txt file in the same folder
def get_data(data, file):
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            token_list = row
            data.append(token_list)


# use sklearn lib to train the MNB model for data, this time the data load is not heavy, so I train all the data at once
# inta and intb here are for n_gram range, unigram is 1,1 , bigram is 2,2 , uni and birgams is 1,2
def train_basic_model(data, label, inta, intb, val_d, val_l, pik, vec):
    # Combine training data and validation data
    all_data = data + val_d
    all_label = label + val_l

    vectorizer = CountVectorizer(ngram_range=(inta, intb), tokenizer=do_nothing, preprocessor=do_nothing, token_pattern=None)

    x_train = vectorizer.fit_transform(all_data)  # Transform all data to vector

    classifier = MultinomialNB()  # create the basic model
    classifier.fit(x_train, all_label)  # Train the model with all data

    # Save the model as a pickle file, in the same folder where all other txt, csv files located
    with open(pik, 'wb') as f:
        pickle.dump(classifier, f)

    # Save the vectorizer as pickle file, this is for further using, if we want to test the model or use model to predict some other data
    with open(vec, 'wb') as f:
        pickle.dump(vectorizer, f)

    return classifier


# test the accrucy of the model
def test_model(model, vec, data, label):
    # open the model
    with open(model, 'rb') as f:
        classifier = pickle.load(f)

    # open the vectorizer than the model used
    with open(vec, 'rb') as f:
        vectorizer = pickle.load(f)

    x_test = vectorizer.transform(data)  # transform test data for further test
    prediction = classifier.predict(x_test)  # test the data
    print(prediction)
    accuracy = (prediction == label).mean()  # calculate the accuracy by calculate the mean of matched times.

    return accuracy


# if there is a input folder, keep going, if not break
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    print("No Path entered!")
    exit()

# get all label with stopwords
train_label = get_label(path+"/train.txt")
val_label = get_label(path+"/val.txt")
test_label = get_label(path+"/test.txt")


# get data with stopwords
get_data(train, path+"/train.csv")
get_data(val, path+"/val.csv")
get_data(test, path+"/test.csv")

# train and fine tune model with stopwords in 3 different grams type
# unigrams = train_basic_model(train, train_label, 1, 1, val, val_label, path+"/mnb_uni.pkl", path+"/mnb_uni_vec.pkl")
# bigrams = train_basic_model(train, train_label, 2, 2, val, val_label, path+"/mnb_bi.pkl", path+"/mnb_bi_vec.pkl")
uniandbi = train_basic_model(train, train_label, 1, 3, val, val_label, path+"/mnb_uni_bi.pkl", path+"/mnb_uni_bi_vec.pkl")

# train and fine tune model without stopwords in 3 different grams type
# unigrams_ns = train_basic_model(train_ns, train_label_ns, 1, 1, val_ns, val_label_ns, path+"/mnb_uni_ns.pkl", path+"/mnb_uni_ns_vec.pkl")
# bigrams_ns = train_basic_model(train_ns, train_label_ns, 2, 2, val_ns, val_label_ns, path+"/mnb_bi_ns.pkl", path+"/mnb_bi_ns_vec.pkl")
# uniandbi_ns = train_basic_model(train_ns, train_label_ns, 1, 4, val_ns, val_label_ns, path+"/mnb_uni_bi_ns.pkl", path+"/mnb_uni_bi_ns_vec.pkl")

# test model with stopwords
# acc = test_model(path+"/mnb_uni.pkl", path+"/mnb_uni_vec.pkl", test, test_label)
# acc1 = test_model(path+"/mnb_bi.pkl", path+"/mnb_bi_vec.pkl", test, test_label)
acc2 = test_model(path+"/mnb_uni_bi.pkl", path+"/mnb_uni_bi_vec.pkl", test, test_label)

# test data without stopwords
# acc3 = test_model(path+"/mnb_uni_ns.pkl", path+"/mnb_uni_ns_vec.pkl", test_ns, test_label_ns)
# acc4 = test_model(path+"/mnb_bi_ns.pkl", path+"/mnb_bi_ns_vec.pkl", test_ns, test_label_ns)
# acc5 = test_model(path+"/mnb_uni_bi_ns.pkl", path+"/mnb_uni_bi_ns_vec.pkl", test_ns, test_label_ns)

# print out the accruacy
# print("Unigrams model have a accuracy of "+str(acc))  # mnb_uni
# print("Bigrams model have a accuracy of " + str(acc1))  # mnb_bi
print("Unigrams + Bigrams model have a accuracy of "+str(acc2))  # mnb_uni_bi

# print("Unigrams without stopwords model have a accuracy of "+str(acc3))  # mnb_uni_ns
# print("Bigrams without stopwords model have a accuracy of "+str(acc4))  # mnb_bi_ns
# print("Unigrams + Bigrams without stopwords model have a accuracy of "+str(acc5))  # mnb_uni_bi_ns

