# Friday-Project-9
# Simple ChatGPT GUI (Python + Tkinter)

This is a GUI app that connects to OpenAI's ChatGPT model. Type in a prompt, click submit, and get a response!

---

## 🚀 How to Run

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

### 2. Install Required Python Packages
Make sure Python 3.10+ is installed on your system. Then install the required libraries using pip:

pip install -r requirements.txt

### 3. Set Up Your OpenAI API Key
Create a file named .env in the root folder of the project. Paste your OpenAI API key like this:

OPENAI_API_KEY=your-api-key-here

⚠️ Important: Do not share this API key. It links to your personal OpenAI account and usage/credits.

### 4. Run the Application
After setting everything up, launch the app using:

python main.py

A window will open where you can type in a prompt, click Submit, and receive a response from ChatGPT.

📦 Dependencies

This project uses:

openai – to access the ChatGPT API
python-dotenv – to load environment variables securely
tkinter – for the graphical user interface (built into Python)
All dependencies (except Tkinter) are listed in requirements.txt.

🔒 .gitignore Reminder

This project ignores the .env file to protect your API key. Be sure not to commit it!

