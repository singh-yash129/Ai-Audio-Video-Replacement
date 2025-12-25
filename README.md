# AI-powered Video Audio Replacement

This project allows users to upload a video and replace its audio with a corrected, AI-generated voice using Streamlit.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
- [Dependencies](#dependencies)


## Overview

Upload a video, and we'll extract its audio, correct the transcription using OpenAI, and generate a new audio track to replace the original audio.

## Features

- Upload video files in MP4, MOV, and AVI formats.
- Extract audio from the uploaded video.
- Convert stereo audio to mono.
- Upload audio to Google Cloud Storage (GCS).
- Transcribe audio using Google Cloud Speech-to-Text.
- Correct transcription with OpenAI GPT-4.
- Synthesize new audio using Google Cloud Text-to-Speech.
- Replace the audio in the video with the new AI-generated audio.
- Download the updated video with the new audio.



## Usage

1. **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

2. **Upload a video**: Use the file uploader to select a video file.
3. **Follow the on-screen instructions**: The app will guide you through the process of extracting, transcribing, correcting, and replacing the audio in your video.
4. **Download the updated video**: Once processing is complete, download the video with the new audio.

## Dependencies

- `streamlit`
- `moviepy`
- `pydub`
- `openai`
- `google-cloud-speech`
- `google-cloud-texttospeech`
- `google-cloud-storage`
- `python-dotenv`
- `requests`

Ensure all dependencies are installed via the provided `requirements.txt` file.


