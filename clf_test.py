from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import pickle
import re
# This script test the model accuary by using the classifier.
# move the model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# This model get
def generate_and_predict(model, tokenizer, clf, vec, label, input, isthree):
    generated_sentences = []
    predictions = []

    for _ in range(99):
        # Generate a sentence
        if isthree:
            input_text = f"{label} {input}"
        else:
            input_text = f"{input}"

        encoded_input = tokenizer.encode(input_text, return_tensors='pt').to(device)
        generated_output = model.generate(encoded_input, max_length=55, temperature=0.8, pad_token_id=tokenizer.pad_token_id, do_sample=True)
        generated_sentence = tokenizer.decode(generated_output[0], skip_special_tokens=True)
        generated_sentences.append(generated_sentence)

        # Preprocess generated_sentence
        temp_sentence = re.sub(r'[_.,\-!?"#$%&()*+/:;<=>@\[\\\]^`{|}~\t\n]', ' ', generated_sentence)

        # Predict with the classifier
        classifier_input = vec.transform([temp_sentence])
        prediction = clf.predict(classifier_input)
        predictions.append(prediction[0])

    return generated_sentences, predictions


def main():
    model_path = 'three'
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    model = model.to(device)

    isthree = False

    if model_path == 'three':
        isthree = True

    # Specify label here
    character = 'hermione'
    # Specify the input texts
    input_texts = 'you'

    # open required type of model
    with open("data/mnb_uni_bi.pkl", 'rb') as f:
        classifier = pickle.load(f)

    # open required type of vectorizer
    with open("data/mnb_uni_bi_vec.pkl", 'rb') as f:
        vectorizer = pickle.load(f)

    sentences, predictions = generate_and_predict(model, tokenizer, classifier, vectorizer, character, input_texts, isthree)

    # Calculate accuracy
    correct_predictions = 0

    for prediction in predictions:
        # If the prediction matches the target label
        if prediction == character:
            # Increase the counter
            correct_predictions += 1

    accuracy = correct_predictions / len(predictions)
    print(f"Accuracy: {accuracy}")

    for sentence, prediction in zip(sentences, predictions):
        print(f"Original Sentence: {sentence}, Predicted Character: {prediction}")


main()
