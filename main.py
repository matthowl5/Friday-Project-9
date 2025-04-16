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

# --- Color Palette ---
#BG_COLOR = "#2d3436"         # Dark Grey/Blue
FRAME_COLOR = "#3b4a54"       # Slightly Lighter Grey/Blue for frames
TEXT_AREA_BG = "#4a6572"     # Medium Grey/Blue for text input/output
TEXT_COLOR = "#dfe6e9"         # Light Grey/White Text
BUTTON_COLOR = "#ff7f50"      # Coral / Orange
BUTTON_ACTIVE_COLOR = "#e57340" # Darker Coral
BUTTON_TEXT_COLOR = "#ffffff"   # White
USER_TEXT_COLOR = "#81ecec"     # Bright Cyan/Teal
GPT_TEXT_COLOR = "#dfe6e9"     # Light Grey/White (Same as default text)
ERROR_TEXT_COLOR = "#e17055"    # Soft Red/Orange
CURSOR_COLOR = "#dfe6e9"      # Cursor color in Entry/Text
BG_COLOR = "#81ecec"
class ChatGPT_GUI:
    def __init__(self, master):
        self.master = master
        master.title("Colorful ChatGPT GUI ✨")
        # Set a minimum size and allow resizing
        master.minsize(550, 450)
        master.geometry("750x600") # Start with a slightly larger default size

        # Set main window background color
        master.config(bg=BG_COLOR)

        # --- Style Configuration ---
        self.style = ttk.Style(master)
        # Choose a theme - 'clam' is often good for custom colors
        self.style.theme_use('clam')

        # Configure custom styles with our fun palette
        self.style.configure("TFrame", background=FRAME_COLOR)
        self.style.configure("TButton", padding=8, relief="flat",
                           background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR,
                           font=('Helvetica', 10, 'bold'),
                           borderwidth=0) # Flat look
        self.style.map("TButton",
                       background=[('active', BUTTON_ACTIVE_COLOR), ('disabled', '#7f8c8d')]) # Grey out when disabled
        # Style Entry AFTER configuring TFrame as it might inherit background otherwise
        self.style.configure("TEntry",
                             fieldbackground=TEXT_AREA_BG,
                             foreground=TEXT_COLOR,
                             insertcolor=CURSOR_COLOR, # Cursor color
                             padding=7, relief="flat", borderwidth=0)
        self.style.configure("TLabel", background=FRAME_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 10))

        # Make the main window grid expandable
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # --- Main Frame ---
        # Add more padding around the main content
        self.main_frame = ttk.Frame(master, padding="15 15 15 15", style="TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) # Add outer padding
        self.main_frame.grid_rowconfigure(0, weight=1) # Output area expands
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- Output Box (Scrollable Text Area) ---
        # ScrolledText is not a ttk widget, so style it directly + use a Frame for border
        output_frame = tk.Frame(self.main_frame, background=FRAME_COLOR, bd=1, relief="sunken") # Use tk.Frame for border control
        output_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15)) # Increased padding below
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_box = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=('Helvetica', 11), # Slightly larger font in output
            background=TEXT_AREA_BG,
            foreground=TEXT_COLOR,
            insertbackground=CURSOR_COLOR, # Cursor color (though usually disabled)
            state='disabled', # Start read-only
            relief="flat",
            borderwidth=0,
            padx=10, # Internal padding
            pady=10
        )
        self.output_box.grid(row=0, column=0, sticky="nsew")

        # Configure tags for styling conversation parts
        self.output_box.tag_configure('user_tag', foreground=USER_TEXT_COLOR, font=('Helvetica', 11, 'bold'))
        self.output_box.tag_configure('gpt_tag', foreground=GPT_TEXT_COLOR, font=('Helvetica', 11))
        self.output_box.tag_configure('error_tag', foreground=ERROR_TEXT_COLOR, font=('Helvetica', 11, 'italic', 'bold'))
        self.output_box.tag_configure('info_tag', foreground=USER_TEXT_COLOR, font=('Helvetica', 9, 'italic')) # For status messages

        # --- Input Frame (Entry + Button) ---
        input_frame = ttk.Frame(self.main_frame, style="TFrame")
        input_frame.grid(row=1, column=0, sticky="ew") # Expand horizontally
        input_frame.grid_columnconfigure(0, weight=1) # Make entry expand

        # --- Entry field for user prompt ---
        self.prompt_entry = ttk.Entry(input_frame, font=('Helvetica', 11), style="TEntry") # Match output font size
        self.prompt_entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 10)) # Internal padding Y, margin right
        self.prompt_entry.bind("<Return>", self.submit_prompt_event) # Bind Enter key

        # --- Submit button ---
        self.submit_button = ttk.Button(input_frame, text="Send 🚀", command=self.submit_prompt, style="TButton", width=10) # Added emoji, fixed width
        self.submit_button.grid(row=0, column=1, sticky="e", ipady=3) # Internal padding Y

        # --- Load API Key and Initialize Client ---
        self.client = self.load_api_key()
        if not self.client:
             # Show error in message box AND output area
             error_msg = "Could not load OPENAI_API_KEY from .env file.\nPlease check instructions and ensure the .env file is correctly set up."
             self.show_error("API Key Error", error_msg)
             self._insert_text(f"CRITICAL ERROR: {error_msg}\n\n", 'error_tag')
             self.prompt_entry.config(state='disabled')
             self.submit_button.config(state='disabled')
        else:
             self._insert_text("API Key loaded successfully. Ready for prompts!\n", 'info_tag')


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
        messagebox.showerror(title, message, parent=self.master) # Make messagebox child of main window

    def _insert_text(self, text, tags=None):
        """Helper function to insert text into the output box, making it writable first."""
        try:
            self.output_box.config(state='normal')
            if tags:
                self.output_box.insert(tk.END, text, tags)
            else:
                self.output_box.insert(tk.END, text)
            self.output_box.see(tk.END) # Scroll to the end
        except Exception as e:
            print(f"Error inserting text: {e}") # Log potential errors during text insertion
        finally:
            self.output_box.config(state='disabled')


    def get_response_thread(self, user_input):
        """Handles the API call in a separate thread."""
        try:
            # Add a "typing" indicator (optional)
            self.master.after(0, self._insert_text, "ChatGPT is thinking...\n", ('info_tag',))

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Or choose another model like gpt-4 if available
                messages=[
                    {"role": "system", "content": "You are a helpful and slightly creative assistant."}, # System prompt
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content.strip()

            # Remove the "typing" indicator - tricky to do cleanly, let's just insert the answer
            # A better way would involve finding the start index of "thinking..." and deleting
            # For simplicity, we'll just let it stay or insert normally.

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
        # Check if button is enabled before submitting via Enter key
        if self.submit_button['state'] == 'normal':
            self.submit_prompt()

    def disable_input(self):
        """Disables the entry field and submit button."""
        self.prompt_entry.config(state='disabled')
        self.submit_button.config(state='disabled')

    def enable_input(self):
        """Enables the entry field and submit button."""
        self.prompt_entry.config(state='normal')
        self.submit_button.config(state='normal')
        # Set focus back to entry field for quick typing
        self.prompt_entry.focus()


if __name__ == "__main__":
    root = tk.Tk()
    # No need for root.option_add("*Font", ...) if configuring widgets individually or via style

    app = ChatGPT_GUI(root)
    root.mainloop()