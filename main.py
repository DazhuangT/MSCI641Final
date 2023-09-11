from transformers import GPT2Tokenizer, GPT2Config
from transformers import GPT2LMHeadModel
from torch.optim import AdamW
from torch.optim import lr_scheduler
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader
from method import do_nothing  # please put method.py under the same folder of inference and main python file
import torch
import csv
import pickle
import re
import sklearn

path = "data"

test = []  # Test data array
val = []  # Validation data array
train = []  # Training data array

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
tokenizer.pad_token = tokenizer.eos_token  # Set the padding token, short data need to be expand longer
tokenizer.padding_side = 'left'  # for fine tune, all text need to be processed before training, this line get the tokenizer gpt2 can use


# Get data from CSV files
def get_data(data, file):
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            token_list = row
            data.append(token_list)


#  This method covert text into token that can be used for training
def gpt_tokenizer(data):

    gpt_token = []
    for sentence in data:
        sentence_str = ' '.join(sentence)
        tokenized_sentence = tokenizer.encode(sentence_str)
        tokenized_sentence = torch.tensor(tokenized_sentence)  # Convert tokenized sentence to tensor
        gpt_token.append(tokenized_sentence)
    return gpt_token


# This method expand short text and also create a attention mask that tell gpt model to ignore all the paddings
def collate_fn(batch):
    inputs = pad_sequence(batch, batch_first=True, padding_value=tokenizer.pad_token_id)
    attention_mask = inputs.ne(tokenizer.pad_token_id).float()
    inputs = inputs.long()  # Convert inputs to LongTensor type
    return inputs, attention_mask


# I didn't use this method, but it was supposed transfer a sentence into a format my sklearn classfier can understand
def token_model_sentence(sentence):
    sentence_no_char = re.sub(r'[\'_.,\-!?"#$%&()*+/:;<=>@\[\\\]^`{|}~\t\n]', ' ', sentence)
    sentence_token = sentence_no_char.split()
    return sentence_token


# This is a important method in training, this method would check the val_loss
# and accuracy of the sentences generated by the model each epoch, the sentence would be test by my classfier
# if after several epochs the model stop improvement in any of these number, it means the model arrives the limit and training will be stopped
def early_stopping(avg_val_loss, best_val_loss, avg_reward, best_reward, no_improvement_epochs, early_stop_ep):
    stop = False
    if avg_val_loss < best_val_loss or avg_reward > best_reward:
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
        if avg_reward > best_reward:
            best_reward = avg_reward
        no_improvement_epochs = 0
    else:
        no_improvement_epochs += 1
    if no_improvement_epochs >= early_stop_ep:
        stop = True
        print(f"No improvement in validation loss or reward for {no_improvement_epochs} epochs. Stopping training.")
    return stop, best_val_loss, best_reward, no_improvement_epochs


# This method fine tune a gpt model with collected data and classifier
# For all arguments:
# train_data,val_data are the dataloader I prepared for fine tuning
# drop_rate is drop out layer rate
# opt_type is the type of the optimizer, default as adamw
# learning_rate is the learning rate of the optimizer
# l2_rate is the rate of l2 normalization which also in the optimizer
# epoch_size is the total epochs I want to train the model
# early_stop_ep is the number of epochs I would allow the model has no improvement
# clf and vec are the classifier I trained to see if a sentence is said by geralt of rivia and it's vectorized
def train_model(train_data, val_data, drop_rate, opt_type, learning_rate, l2_rate, epoch_size, early_stop_ep, clf, vec, clf_label):
    # Get configuration from the pre-trained model
    config = GPT2Config.from_pretrained('gpt2')

    # Modify the dropout parameter in the configuration
    config.dropout = drop_rate

    # Load gpt2 raw model, with new drop out rate
    model = GPT2LMHeadModel.from_pretrained('gpt2', config=config)

    # Set the optimizer
    if opt_type == "sgd":
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=l2_rate)
    elif opt_type == "rm":
        optimizer = torch.optim.RMSprop(model.parameters(), lr=learning_rate, weight_decay=l2_rate)
    else:  # it is obvious the previous two was two other optimizer, I set deafult as adamw
        optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=l2_rate)  # lr is learning rate and weight_decay is l2 rate

    # Here I tried multiple scheduler
    # scheduler = lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)  # this is a learn rate modifier, it changes learning rate every 5 epochs, by time the rate with gamma
    # scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min')
    # scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    # Set the scheduler
    scheduler = lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)

    # Move training to gpu
    device = torch.device('cuda')
    model.to(device)

    # Start training
    model.train()

    best_val_loss = float('inf')  # Track the best validation loss, any loss will be smaller than infinity, there fore first epochs will be caught correctly
    best_reward = float('-inf')  # Track the best reward, same reason, this time reward we want larger number, so the initial is negtiave infinity
    no_improvement_epochs = 0  # Track how many epochs have passed without improvement

    for epoch in range(epoch_size):  # num_epochs is the number of training epochs I plan to run
        rewards = []
        for batch in train_data:
            inputs, attention_mask = [item.to(device) for item in batch]  # I set the inputs and attetion mask in dataloader already

            # Forward pass
            outputs = model(inputs, attention_mask=attention_mask, labels=inputs)
            loss = outputs.loss

            # Generate text for getting reward weight
            generated_outputs = model.generate(inputs, max_length=55, pad_token_id=tokenizer.pad_token_id, attention_mask=attention_mask, do_sample=True)  # argument are some basic settings, one thing speical, the max length is 51 because the longest sentence is 50
            generated_text = tokenizer.batch_decode(generated_outputs, skip_special_tokens=True)   # there are some special tokens we want to avoid, because when I was training the classifier, I removed all the special tokens too.

            # This is the special setting for the three character model, a different reward calculation
            if clf_label == 'other':
                # Create an empty list to hold the processed sentences
                processed_text = []

                # Iterate through each sentence in the generated text
                for sentence in generated_text:
                    # Split the sentence into a list of words using space as the delimiter
                    words = sentence.split(' ')

                    # Remove the first word, becuase in this data we added a name as a first word of all sentences
                    new_words = words[1:]

                    # Join the remaining words back into a sentence using space as the delimiter
                    new_sentence = ' '.join(new_words)

                    # Add the new sentence to the list of processed text
                    processed_text.append(new_sentence)

                # Assign the processed text back to generated_text
                generated_text = processed_text

                # print(generated_text)

            classifier_inputs = vec.transform(generated_text)

            # Calculate reward and adjust loss
            # Get probabilities of being required label
            classifier_proba = clf.predict_proba(classifier_inputs)
            pre_proba = classifier_proba[:, clf.classes_ == clf_label]

            # Calculate reward and adjust loss
            reward = pre_proba.mean()  # If classifier think the generated text is belong to required label, gives a reward
            rewards.append(reward)  # Add the reward to the list
            reward_weight = 1.0  # adjust this value to change the influence of the reward

            # Special setting for three model
            if clf_label == 'other':
                adjusted_loss = loss * (1 + reward_weight * reward)
            # regular setting for single character model
            else:
                adjusted_loss = loss * (1 - reward_weight * reward)

            # Backward pass
            adjusted_loss.backward()

            # Update weights
            optimizer.step()
            optimizer.zero_grad()

            # Print the loss
            print(loss.item())

        # Calculate and print average reward
        if clf_label == 'other':  # Three character model
            avg_reward = 1 - sum(rewards) / len(rewards)
        else:  # single character model
            avg_reward = sum(rewards) / len(rewards)

        print('Average reward:', avg_reward)

        # Evaluate on the validation set after each epoc
        model.eval()
        with torch.no_grad():
            total_loss = 0

            # same process as the train data
            for batch in val_data:
                inputs, attention_mask = [item.to(device) for item in batch]
                outputs = model(inputs, attention_mask=attention_mask, labels=inputs)
                total_loss += outputs.loss.item()   # Save the val loss

            # Calculate and print average validation loss
            avg_val_loss = total_loss / len(val_data)
            print('Validation loss:', avg_val_loss)

        # Modify learning rate
        scheduler.step()

        # Check for early stopping
        stop, best_val_loss, best_reward, no_improvement_epochs = early_stopping(avg_val_loss, best_val_loss, avg_reward, best_reward, no_improvement_epochs, early_stop_ep)
        if not stop:  # If the model is still improving we keep going, but the current model need to be saved
            best_model_state = model.state_dict()  # Save the best model state when validation loss or reward improves
            model.save_pretrained('three')
            tokenizer.save_pretrained('three')
        else:  # If the model reaches the limit, we save the final model and stop training
            model.load_state_dict(best_model_state)  # Save the best model state when validation loss or reward improves
            break

        model.train()

    return model


def main():
    # Get the data
    get_data(train, "data/three_train.csv")
    get_data(val, "data/three_val.csv")

    # Open required type of model
    with open("data/mnb_uni_bi.pkl", 'rb') as f:
        classifier = pickle.load(f)

    print(classifier.classes_)
    # open required type of vectorizer
    with open("data/mnb_uni_bi_vec.pkl", 'rb') as f:
        vectorizer = pickle.load(f)

    # Tokenize the data
    gpt_train = gpt_tokenizer(train)
    gpt_val = gpt_tokenizer(val)

    # Create dataloader
    train_dataloader = DataLoader(gpt_train, batch_size=16, shuffle=True, collate_fn=collate_fn)
    val_dataloader = DataLoader(gpt_val, batch_size=16, shuffle=False, collate_fn=collate_fn)

    # Here I trained multiple models
    # Train and save model, the final model and it's tokenizer would be a folder/ dictionary

    # final_model = train_model(train_dataloader, val_dataloader, 0.2, "adamw", 2e-4, 1e-2, 21, 5, classifier, vectorizer)
    # final_model = train_model(train_dataloader, val_dataloader, 0.2, "adamw", 2e-3, 1e-2, 26, 5, classifier, vectorizer, 'harry')
    # final_model = train_model(train_dataloader, val_dataloader, 0.2, "adamw", 2e-4, 1e-2, 13, 5, classifier, vectorizer)

    # Adjust the argument to train correct model
    final_model = train_model(train_dataloader, val_dataloader, 0.2, "adamw", 2e-4, 1e-2, 26, 5, classifier, vectorizer, 'other')
    final_model.save_pretrained('three')
    tokenizer.save_pretrained('three')

    print("done")


main()