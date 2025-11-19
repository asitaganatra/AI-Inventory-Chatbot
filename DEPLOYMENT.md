# Deployment Guide - Streamlit Cloud

## Prerequisites

- GitHub account with your repo pushed (done ✓)
- Streamlit Cloud account (https://share.streamlit.io/)
- Google Gemini API key

## Step-by-Step Deployment

### 1. Prepare Secrets

Create `.streamlit/secrets.toml` in your local repo:
```toml
GEMINI_API_KEY = "your-google-api-key-here"
```

### 2. Update requirements.txt

Make sure your `requirements.txt` is optimal for Streamlit Cloud:
```
streamlit>=1.28.0
pandas>=1.5.0
langchain==0.1.20
langchain-google-genai==0.1.2
google-generativeai>=0.4.0
gTTS>=2.3.0
SpeechRecognition>=3.10.0
faker>=18.0.0
scikit-learn>=1.3.0
scipy>=1.11.0
```

**Note**: PyAudio is NOT included because Streamlit Cloud cannot install it. Users on deployment will see a helpful message to use text input instead of microphone.

### 3. Add packages.txt (Optional)

For system-level dependencies:
```
portaudio19-dev
```

This file tells Streamlit Cloud to install system packages via apt-get.

### 4. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repo
4. Choose the branch: `main`
5. Set main file: `app.py`
6. Click "Deploy"

### 5. Add Secrets on Streamlit Cloud

1. After deployment, go to app settings (gear icon)
2. Click "Secrets"
3. Paste your secrets:
```toml
GEMINI_API_KEY = "your-api-key-here"
```
4. Save

### 6. Verify Deployment

The app should now be live! Features available:
- ✓ Text chat with LLM
- ✓ Audio file upload & transcription
- ✓ Text-to-speech output
- ✓ Owner Tools (with password)
- ✓ Dashboard & analytics
- Note: Microphone input disabled (requires PyAudio, unavailable on Streamlit Cloud)

## Handling Microphone Unavailability

The app is configured to gracefully handle missing PyAudio:
- Shows helpful error message
- Provides alternative input methods:
  - Text input
  - Audio file upload
- Full functionality otherwise

## Environment Variables

Streamlit Cloud automatically uses `.streamlit/secrets.toml` from your repo, so no additional setup needed for API keys.

## Redeploying After Changes

```bash
git add .
git commit -m "Update: describe your changes"
git push origin main
```

Streamlit Cloud automatically redeploys when you push to GitHub!

## Troubleshooting Deployment

### Error: "Error installing requirements"
- Remove problematic packages (like PyAudio)
- Check `requirements.txt` syntax
- Ensure package versions are available

### Error: "API Key not found"
- Go to app settings
- Add secrets in the Secrets section
- Ensure exact key name: `GEMINI_API_KEY`

### Microphone not working
- This is expected on Streamlit Cloud
- Users should use text input or upload audio files
- The app provides helpful guidance

## Files Needed for Deployment

```
.streamlit/
├── config.toml          # Configuration
├── secrets.toml         # API keys (auto-managed by Streamlit Cloud)
└── secrets.example.toml # Template for users

requirements.txt         # Python packages (NO PyAudio)
packages.txt            # System packages (optional)
README.md               # Documentation
DEPLOYMENT.md           # This file

app.py                  # Main application
analytics.py            # Database functions
inventory.db            # SQLite database (included)
```

## Local Development vs Deployment

| Feature | Local | Streamlit Cloud |
|---------|-------|-----------------|
| Text Chat | ✓ | ✓ |
| Microphone Input | ✓ | ✗ (no PyAudio) |
| Audio Upload | ✓ | ✓ |
| Text-to-Speech | ✓ | ✓ |
| Database | ✓ | ✓ |
| Owner Tools | ✓ | ✓ |
| Dashboard | ✓ | ✓ |

## Support

For Streamlit Cloud issues: https://docs.streamlit.io/
For LangChain issues: https://python.langchain.com/
For app issues: Check GitHub repo

---

**Last Updated**: November 19, 2025
**Status**: Ready for Streamlit Cloud Deployment
