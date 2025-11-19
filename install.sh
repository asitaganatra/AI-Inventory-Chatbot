#!/bin/bash
# Post-install script for Streamlit Cloud
# This installs system dependencies needed for audio processing

pip install --no-cache-dir pyaudio 2>/dev/null || echo "PyAudio installation skipped (not available in this environment)"
