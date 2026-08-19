# How to Deploy to PythonAnywhere (100% Free 24/7 Hosting)

Follow these step-by-step instructions to host your Flask AI agent on PythonAnywhere for free:

---

### Step 1: Push Your Latest Code to GitHub
Ensure all your project files (including templates and static files) are updated on GitHub. In your local terminal, run:
```bash
python push.py
```

---

### Step 2: Set Up Your PythonAnywhere Account
1. Sign up for a free account at [PythonAnywhere.com](https://www.pythonanywhere.com/).
2. Once logged in, go to your **Dashboard**.

---

### Step 3: Clone the Repository
1. On the PythonAnywhere Dashboard, click the **Consoles** tab and open a new **Bash** console.
2. Run the following commands to clone your repository and navigate into it:
   ```bash
   git clone https://github.com/nathanni2024-svg/accesability-agent.git
   cd accesability-agent
   ```
3. Install the required Python packages:
   ```bash
   pip3 install --user -r requirements.txt
   ```
   *(This will install Flask, OpenAI, and other packages directly to your user environment).*

---

### Step 4: Configure the Web App
1. Open a new browser tab, go back to the PythonAnywhere Dashboard, and click the **Web** tab.
2. Click **Add a new web app**.
3. Follow the wizard:
   * **Domain name**: Keep the default free domain (`username.pythonanywhere.com`).
   * **Select a Python Web Framework**: Choose **Manual Configuration** (do NOT choose Flask here, as manual configuration gives us cleaner control).
   * **Select a Python version**: Choose **Python 3.9** or **Python 3.10**.
   * Click **Next** to finish the wizard.

---

### Step 5: Edit the WSGI Configuration
1. On the **Web** tab, scroll down to the **Code** section.
2. Click the link next to **WSGI configuration file** (it looks like `/var/www/yourusername_pythonanywhere_com_wsgi.py`).
3. Delete all the existing code in that file and paste the following configuration:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/accesability-agent'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables (FLASK_SECRET_KEY, etc.)
os.environ['NODE_ENV'] = 'production'
os.environ['GEMINI_API_KEY'] = 'YOUR_GEMINI_API_KEY_HERE'

# Import the Flask app from server.py as 'application'
from server import app as application
```

4. **CRITICAL**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username, and `YOUR_GEMINI_API_KEY_HERE` with your Google Gemini API Key.
5. Click the green **Save** button at the top-right.

---

### Step 6: Reload and Access
1. Go back to the **Web** tab on the PythonAnywhere dashboard.
2. Click the green **Reload** button at the top.
3. Your site is now live! Click your site link:
   👉 `https://yourusername.pythonanywhere.com`
