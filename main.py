import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import ttk  # Import themed widgets
from dotenv import load_dotenv
from openai import OpenAI
import threading # To keep the GUI responsive during API calls

# --- Instructions for Testing ---
# 1. Make sure you have Python installed (version 3.6 or higher recommended).
# 2. Install required libraries:
#    pip install python-dotenv openai tk
# 3. Create a file named '.env' in the SAME directory as this script.
# 4. Inside the '.env' file, add your OpenAI API key like this:
#    OPENAI_API_KEY='your_actual_api_key_here'
#    (Replace 'your_actual_api_key_here' with your real key)
# 5. Save the '.env' file.
# 6. Run this Python script (e.g., python your_script_name.py).
# 7. The GUI should appear. Type your prompt and click "Submit" or press Enter.
# --- End Instructions ---

class ChatGPT_GUI:
    def __init__(self, master):
        self.master = master
        master.title("Professional ChatGPT GUI")
        # Set a minimum size and allow resizing
        master.minsize(500, 400)
        master.geometry("700x550") # Start with a slightly larger default size

        # --- Style Configuration ---
        self.style = ttk.Style(master)
        # Choose a theme (clam, alt, default, classic - 'clam' or 'alt' often look better)
        self.style.theme_use('clam')

        # Configure custom styles (optional - adjust colors as desired)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, relief="flat",
                           background="#007bff", foreground="white",
                           font=('Helvetica', 10, 'bold'))
        self.style.map("TButton",
                       background=[('active', '#0056b3'), ('disabled', '#c0c0c0')])
        self.style.configure("TEntry", padding=5, relief="flat")
        self.style.configure("TLabel", background="#f0f0f0", font=('Helvetica', 10))

        # Make the main window grid expandable
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # --- Main Frame ---
        self.main_frame = ttk.Frame(master, padding="10 10 10 10", style="TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew") # North, South, East, West
        self.main_frame.grid_rowconfigure(0, weight=1) # Output area expands
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- Output Box (Scrollable Text Area) ---
        # Wrap ScrolledText in a standard Frame for better border/padding control if needed
        output_frame = ttk.Frame(self.main_frame, relief="sunken", borderwidth=1)
        output_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_box = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=('Helvetica', 10),
            state='disabled', # Start read-only
            relief="flat",  # Let the containing frame handle relief
            borderwidth=0
        )
        self.output_box.grid(row=0, column=0, sticky="nsew")

        # Configure tags for styling conversation parts
        self.output_box.tag_configure('user_tag', foreground='#007bff', font=('Helvetica', 10, 'bold'))
        self.output_box.tag_configure('gpt_tag', foreground='#333333', font=('Helvetica', 10))
        self.output_box.tag_configure('error_tag', foreground='red', font=('Helvetica', 10, 'italic'))

        # --- Input Frame (Entry + Button) ---
        input_frame = ttk.Frame(self.main_frame, style="TFrame")
        input_frame.grid(row=1, column=0, sticky="ew") # Expand horizontally
        input_frame.grid_columnconfigure(0, weight=1) # Make entry expand

        # --- Entry field for user prompt ---
        self.prompt_entry = ttk.Entry(input_frame, font=('Helvetica', 10), style="TEntry")
        self.prompt_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.prompt_entry.bind("<Return>", self.submit_prompt_event) # Bind Enter key

        # --- Submit button ---
        self.submit_button = ttk.Button(input_frame, text="Submit", command=self.submit_prompt, style="TButton")
        self.submit_button.grid(row=0, column=1, sticky="e")

        # --- Load API Key and Initialize Client ---
        self.client = self.load_api_key()
        if not self.client:
             self.show_error("API Key Error", "Could not load OPENAI_API_KEY from .env file. Please check instructions and ensure the .env file is correctly set up.")
             self.prompt_entry.config(state='disabled')
             self.submit_button.config(state='disabled')

    def load_api_key(self):
        """Loads API key from .env and initializes OpenAI client."""
        try:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Error: OPENAI_API_KEY not found in .env file.")
                return None
            return OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Error loading .env or initializing OpenAI client: {e}")
            return None

    def show_error(self, title, message):
        """Displays an error message box."""
        messagebox.showerror(title, message)
        # Optionally log to output_box as well
        self._insert_text(f"Error: {message}\n\n", 'error_tag')


    def _insert_text(self, text, tags=None):
        """Helper function to insert text into the output box, making it writable first."""
        self.output_box.config(state='normal')
        if tags:
            self.output_box.insert(tk.END, text, tags)
        else:
            self.output_box.insert(tk.END, text)
        self.output_box.see(tk.END) # Scroll to the end
        self.output_box.config(state='disabled')


    def get_response_thread(self, user_input):
        """Handles the API call in a separate thread."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Or choose another model like gpt-4 if available
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."}, # Optional system message
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content.strip()

            # Schedule GUI updates to run in the main thread
            self.master.after(0, self._insert_text, f"ChatGPT: ", ('gpt_tag',))
            self.master.after(0, self._insert_text, f"{reply}\n\n")

        except Exception as e:
            error_message = f"API Error: {str(e)}\n\n"
            print(error_message) # Also print to console for debugging
            # Schedule GUI updates to run in the main thread
            self.master.after(0, self._insert_text, error_message, ('error_tag',))
        finally:
             # Re-enable input/button in the main thread
            self.master.after(0, self.enable_input)


    def submit_prompt(self):
        """Handles the submission of the prompt."""
        if not self.client:
             self.show_error("API Key Error", "OpenAI client not initialized. Please check your API key setup.")
             return

        user_input = self.prompt_entry.get().strip()
        if not user_input:
            return # Do nothing if input is empty

        # Display user input immediately
        self._insert_text(f"You: ", ('user_tag',))
        self._insert_text(f"{user_input}\n")

        # Clear the entry field
        self.prompt_entry.delete(0, tk.END)

        # Disable input and button while processing
        self.disable_input()

        # Start the API call in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self.get_response_thread, args=(user_input,))
        thread.daemon = True # Allows the program to exit even if this thread is running
        thread.start()


    def submit_prompt_event(self, event):
        """Callback for the Enter key binding."""
        self.submit_prompt()

    def disable_input(self):
        """Disables the entry field and submit button."""
        self.prompt_entry.config(state='disabled')
        self.submit_button.config(state='disabled')

    def enable_input(self):
        """Enables the entry field and submit button."""
        self.prompt_entry.config(state='normal')
        self.submit_button.config(state='normal')
        # Optionally, set focus back to entry field
        # self.prompt_entry.focus()


if __name__ == "__main__":
    root = tk.Tk()
    # Set a default font for the application (optional but good practice)
    default_font = ('Helvetica', 10)
    root.option_add("*Font", default_font)

    app = ChatGPT_GUI(root)
    root.mainloop()
