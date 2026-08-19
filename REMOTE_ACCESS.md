# 📱 24/7 Private Remote Access Guide

You can now access your AI Hub securely from your phone, tablet, or another computer, no matter where you are.

---

## ☁️ Option 1: Cloud Deployment (Always On)
*Use this if you want a website that works 24/7 without your Mac needing to be plugged in.*

### 1. Create a Repository
Push your code to **GitHub** (keep it as a **Private** repository!).

### 2. Deploy to Render.com
1. Go to [Render.com](https://render.com) and sign up with GitHub.
2. Click **New +** -> **Blueprint**.
3. Select your repository. It will automatically detect the `render.yaml` file I created.
4. **Environment Variables**: You will need to add your `GEMINI_API_KEY` and `APP_PASSWORD` in the Render dashboard.

### 3. Persistent Memory
Your "AI Brain" will be stored on a **1GB Persistent Disk** (configured in `render.yaml`), so it won't forget anything when you redeploy.

---

## 💻 Option 2: Always-On Mac M5 (Stay Local)
*Use this to keep the M5 Neural Engine power and Ollama local models.*

### 1. Keep the Mac Awake
Download the free tool [Amphetamine](https://apps.apple.com/us/app/amphetamine/id937984704?mt=12).
- Configure it to **Allow system sleep when display is closed** = `OFF`.
- Start a session "Indefinitely."

### 2. Access via Tailscale (Secure VPN)
1. Install [Tailscale](https://tailscale.com/) on your Mac and your Phone.
2. Log in with the same account.
3. On your phone, open your browser and type the **Tailscale IP** of your Mac (e.g., `http://100.x.y.z:8080`).
4. **Result**: You now have a 100% private, encrypted tunnel directly to your M5 chip.

---

## 🔒 Security Best Practices

> [!IMPORTANT]
> **Check your .env!**
> Ensure `APP_PASSWORD` is set to a strong, unique password.
> If you are on a public server, I have configured `server.py` to **refuse to start** unless a password is set.

> [!TIP]
> **Session Persistence**: I have configured the login to last for **30 days**. Once you log in on your phone, you won't need to enter the password again for a month!

---

## What was changed today?
- **server.py**: Added strict production security and 30-day session memory.
- **render.yaml**: Added configuration for one-click cloud deployment with persistent storage.
- **requirements.txt**: Verified all cloud-ready dependencies are present.
