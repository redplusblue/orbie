import os, requests, json
from secret_vals import get_config, get_secret

config = get_config()
secret = get_secret()

OLLAMA_API_URL = config["ollama"]["API"]
OLLAMA_MODEL = config["ollama"]["model"]

GROQ_API_URL = config["groq"]["API"]
GROQ_MODEL = config["groq"]["model"]
GROQ_SEARCH = config["groq"]["search"]
GROQ_API_KEY = secret["GROQ_API_KEY"]

def get_system_prompt(prompt):
    """
    Get the system prompt from the file system_prompts/<prompt>.txt
    :param prompt: The name of the prompt file
    :return: res: The system prompt text, or the default prompt if the file does not exist
    """
    # If file does not exist, return default prompt (in default file)
    if not os.path.exists('./system_prompts/' + prompt + '.txt'):
        prompt = "default"
    res = ""
    with open('./system_prompts/' + prompt + '.txt', 'r') as file:
        res = file.read()

    # Remove newlines & return
    res = res.replace('\n', '')
    return res


def chat_ollama(message, system_prompt="default"):
    """
    Request a response from the Ollama API and stream the response line by line.
    :param message: The user's message
    :param system_prompt: The system prompt to use for the conversation, default is 'default'
    :return: The response from the Ollama API line by line as a generator object
    """
    payload = {
        "model": OLLAMA_MODEL,
        "system": get_system_prompt(system_prompt),
        "prompt": f'role: user, content: "{message}"\n',
    }

    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        # Parse JSON line and extract the 'response' field
                        parsed_line = json.loads(line.decode("utf-8"))
                        if "response" in parsed_line:
                            yield parsed_line["response"]
            else:
                raise Exception(f"Error from Ollama API: {response.status_code}")
    except Exception as e:
        yield f"Sorry, I encountered an error: {e}"

def chat_groq(message, system_prompt="default", model=GROQ_MODEL):
    """
    Send a message to the Groq API and returns the response.
    :param model: The model to use for the conversation.
    :param message: The user's message to send to the API
    :param system_prompt: The system prompt to use for the conversation, default is 'default'
    :return: response: The response from the Groq API
    """
    # Construct the request payload and headers
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": get_system_prompt(system_prompt)
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    # Send the POST request
    response = requests.post(GROQ_API_URL, headers=headers, json=data)

    # Handle the response
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error from Groq API: {response.status_code}, {response.text}")

def search_groq(message, system_prompt="search", model=GROQ_SEARCH):
    """
    Send a message to the Groq API and returns the response (Suitable for web search).
    :param model: The model to use for the conversation.
    :param message: The user's message to send to the API
    :param system_prompt: The system prompt to use for the conversation, default is 'default'
    :return: response: The response from the Groq API
    """
    # Construct the request payload and headers
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": get_system_prompt(system_prompt) + " " + message
            }
        ]
    }

    # Send the POST request
    response = requests.post(GROQ_API_URL, headers=headers, json=data)

    # Handle the response
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error from Groq API: {response.status_code}, {response.text}")