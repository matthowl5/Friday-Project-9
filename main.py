import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Prompt user
prompt = input("Ask something: ")

# Send chat completion request
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Print the response
print("Response:", response.choices[0].message.content.strip())
