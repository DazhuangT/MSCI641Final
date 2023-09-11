import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import sys

# move the model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# This method generate the text based on input, also encode the input and decode the responses
def generate_reply(model, tokenizer, input_text):
    encoded_input = tokenizer.encode(input_text, return_tensors='pt')

    # also move encoded_input to the same device as your model
    encoded_input = encoded_input.to(device)

    # Generate the response
    output = model.generate(encoded_input, max_length=55, temperature=0.8, pad_token_id=tokenizer.pad_token_id, do_sample=True)
    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)

    return decoded_output


def main():
    # No input arguments we exit
    if len(sys.argv) < 3:
        print("Missing at least 1 argument!")
        exit()

    character = sys.argv[1]
    model_path = sys.argv[2]

    # Not correctly input the character we exit
    if character not in ["ron", "harry", "hermione"]:
        print("No such character!")
        exit()

    model_name = os.path.basename(model_path)
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    model = model.to(device)

    #  exit boolean for the program
    exit_bol = False

    # If didn't exit we get response
    while not exit_bol:
        input_text = input("User: ")  # User's input, you have to have at least one word or mark in the input
        if input_text.lower() == "exit":
            exit_bol = True
            print("Exiting the program.")
            continue
        # Special setting for three characters model, give the pre as the condition
        if model_name == 'three':
            input_text = character + ' ' + input_text

        response = generate_reply(model, tokenizer, input_text)

        # Remove a common format error
        response = response.replace("’", "'").replace("' ", "'").replace("''", "'")

        print(character + ": ", response)


main()
