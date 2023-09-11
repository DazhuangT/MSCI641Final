# MSCI641Final
Final project for the MSCI 641 
This is a harry porter style-conditioned text generation which would create 4 dialogue generation models.

For all script:
main.py: This script do the whole train progress of fine tune gpt2 model, all four models was using the same script.
clf.py: This script train the classifier of each characters.
clf_test.py: This script uses the classfier to test the perfornmance of each model
data_expand.py: This script apply the Data augmentation method to some data
data_process.py: This script created dataset and labels with the given data
split.py: This script split the data in a txt file into sentences
prefix.py: This script add a word in front of each data sentences
read_dia.py: This script read dialogue.txt and split dialogues by different characters
read_js.py: This script read the json file data.
remove_heading.py: This script remove the heading of each sentences
try.py: This script try if the gpu is work on the current enviroment
inference.py: script used to test the final model
method.py: script all classfier related script needs.

