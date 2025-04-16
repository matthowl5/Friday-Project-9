import os
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Function to handle submission
def get_response():
    user_input = prompt_entry.get()
    if user_input.strip() == "":
        return

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content.strip()
        output_box.insert(tk.END, f"You: {user_input}\nChatGPT: {reply}\n\n")
        prompt_entry.delete(0, tk.END)
        output_box.see(tk.END)
    except Exception as e:
        output_box.insert(tk.END, f"Error: {str(e)}\n\n")

# Create GUI window
root = tk.Tk()
root.title("Simple ChatGPT GUI")
root.geometry("600x400")

# Entry field for user prompt
prompt_entry = tk.Entry(root, width=80)
prompt_entry.pack(pady=10)

# Submit button
submit_button = tk.Button(root, text="Submit", command=get_response)
submit_button.pack()

# Output box (scrollable)
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
output_box.pack(padx=10, pady=10)

# Run the GUI loop
root.mainloop()
