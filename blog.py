# A python script that automates the process of writting interviews
# interview questions are recursively taken as user input and sent as a prompt to the GTP-3
# the reply is fetched and saved as a text document.

import os
import shelve

from dotenv import load_dotenv
load_dotenv('./.env')

file_name = input('What is the file name (file_name/file-name): ')
topic = input('What is the topic of the interview: ').title()
intro = f"Hello and welcome to another session with GTP-3 and me. Our topic today is '{topic}' enjoy please leave reviews or request in the comment section\n"  

def interview_session():
    # Function which handles sending and recieving data between the user and open ai api
    import openai

    conversation = []
    total_tokens = 0

    while True:
        # Loop through user input and confirm validity of input
        prompt = input("Whats your question? or type (thank you) to quit: ").lower()
        try:
            # If user input can be converted into an integer pass
            prompt = int(prompt)
            print('Please type a valid question')
            pass
        except:
            # List of generic greetings 
            greetings = ['hello', 'good morning', 'good afternoon', 
                         'good evening', 'hi']

            if prompt in greetings:
                # If a generic greeting is typed reply with a generic answer to
                # avoid api charges 
                print('Hello how are you?')
                pass
            elif len(prompt) < 5:
                # If length of question is less then 5 characters 
                print('I dont understand your question?')
                pass
            elif prompt == 'thank you':
                # Thank you is the key word for interview completion
                status = input('Are you done with the interview?(Y/N): ').title()

                if status == 'Y':
                    # Close interview and return dialog
                    context = {
                        'conversation': conversation,
                        'total_tokens': total_tokens
                    }
                    return context
            else:
                # Connect to open ai and recieve data
                try:
                    openai.api_key = os.getenv("OPEN_AI_SEC_KEY")
                    synposis = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0.7,
                    )

                    # reply = synposis['choices'][0]['text']
                    reply = synposis['choices'][0]['text']
                    tokens = synposis['usage']['total_tokens']
                    print(reply)
                    total_tokens += tokens
                except Exception as e:
                    print(f'{e}')

                present_phrase = []
                present_phrase.append(f'{prompt}\n')
                present_phrase.append(reply)
                conversation.append(present_phrase)           


def write_article(file_name, intro, total_cost):
    # Function to create a text document from
    stat = 0
    e_list = []
    # Create a folder if it dosent exist
    try:
        os.mkdir('./blog_posts/')
    except Exception as e:
        pass

    # Open a file object
    article_file = open(f'./blog_posts/{file_name}.txt', 'w')
    # Extract the conversation from the api

    while stat != 1:
        try:
            con = interview_session()
            stat = 1
        except Exception as e:
            e = str(e)
            print(e)
            e_list.append(e)
    discussion = con['conversation']
    token = con['total_tokens'] 
    cost_metric = [0.1200, 0.06, 0.03, 0.015, 0.0075]
    price_bracket = [1000, 500, 250, 125, 62]
    if token % price_bracket[0] == 0:   cost = token * cost_metric[0]
    elif token % price_bracket[1] == 0:   cost = token * cost_metric[1]
    elif token % price_bracket[2] == 0:   cost = token * cost_metric[2]
    elif token % price_bracket[3] == 0:   cost = token * cost_metric[3]
    elif token % price_bracket[4] == 0:   cost = token * cost_metric[4]
    else:   cost = token * 0.00012

    # Calcutate life span cost
    total_cost += cost
    article_file.write(intro)

    # Write into file conversation
    for dis in discussion:
        for line in dis:
            article_file.write(f'{line}\n')
    article_file.close()

    context = {
        '_total_cost': total_cost,
        '_token': token,
        '_cost': cost,
        '_e': e_list
    }
    print(context)
    return context


# TODO: write a function that logs the api responses or failures
def logger(_metrics, _total):

    # Create a folder if it dosent exist
    try:
        os.mkdir('./logs/')
    except:
        pass 
    # Open a file object
    article_file = open(f'./logs/{file_name}logs.txt', 'w')
    article_file.write(f'Total for this interview is: {_metrics["_cost"]}\n')
    article_file.write(f'Total for this account is: {_total}\n')
    article_file.write(f'Total tokens for this interview is: {_metrics["_total_cost"]}\n')
    if len(_metrics['_e']) > 0:
        article_file.write(f'Errors encountered are:')
        for err in _metrics['_e']: # e is a list of errors
            article_file.write(f': {err}\n')
    else:
        article_file.write('No errors encountered')
    article_file.close()



# Retrieve total life span cost from system shelve
shelve_file = shelve.open('cost')

shelve_status = os.getenv("SHELVE")
_total = [0]
# Confirm if a shelve instance exists in the dir
if shelve_status != 'True':
    shelve_file['total'] = _total
total_cost = shelve_file['total'][0]
total_cost = float(total_cost)
print(total_cost)

# Update and close shelve
_metrics = write_article(file_name, intro, total_cost)
_total_cost = _metrics['_cost']

_total[0] = _total_cost
shelve_file['total'] = _total
shelve_file.close()
print(_total)

    #Call logger function
logger(_metrics, _total)

# TODO: write a function that stores posts in a postgresql database in a 
# seperate file , import and call 
