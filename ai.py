import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
import openai
import os,requests
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as tts
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

openai.api_type = os.getenv('OPENAI_API_TYPE')
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_endpoint = os.getenv('OPENAI_API_ENDPOINT')
openai.api_version = os.getenv('OPENAI_API_VERSION')

 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('GOOGLE_CREDENTIALS_PATH')
bucket_name = os.getenv('BUCKET_NAME')

if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    st.warning("Google credentials are not set correctly!")


st.title("AI-powered Video Audio Replacement")
st.write("Upload a video, and we'll replace its audio with corrected AI-generated voice!")


video_file = st.file_uploader("Upload a Video", type=["mp4", "mov", "avi"])

if video_file:
    
    with open("input_video.mp4", "wb") as f:
        f.write(video_file.read())

    st.video("input_video.mp4")

    
    st.write("Extracting audio...")
    video = VideoFileClip("input_video.mp4")
    audio = video.audio
    audio.write_audiofile("extracted_audio.wav")

    
    try:
        st.write("Converting audio to mono...")
        sound = AudioSegment.from_wav("extracted_audio.wav")
        sound = sound.set_channels(1)  # Convert to mono
        sound.export("mono_audio.wav", format="wav")
        st.success("Audio successfully converted.")
    except Exception as e:
        st.error(f"Error during audio conversion: {str(e)}")

    
    try:
        st.write("Uploading audio to GCS...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob("audio_for_transcription.wav")
        blob.upload_from_filename("mono_audio.wav")
        gcs_uri = f"gs://{bucket_name}/audio_for_transcription.wav"
        st.success(f"Audio uploaded to {gcs_uri}")
    except Exception as e:
        st.error(f"Error uploading audio: {str(e)}")

    
    transcription = ""
    try:
        st.write("Transcribing audio...")
        client = speech.SpeechClient()
        audio_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code="en-US"
        )
        audio = speech.RecognitionAudio(uri=gcs_uri)
        operation = client.long_running_recognize(config=audio_config, audio=audio)
        response = operation.result(timeout=300)

        for result in response.results:
            transcription += result.alternatives[0].transcript

        if transcription:
            st.write("Original Transcription:")
            st.text_area("Transcription", transcription, height=150)
        else:
            st.warning("Transcription was empty.")
    except Exception as e:
        st.error(f"Error during transcription: {str(e)}")

    
    corrected_text = ""
    if transcription:
        try:
            st.write("Correcting transcription with GPT-4o...")

            
            endpoint = f"{openai.api_endpoint}"

            
            headers = {
                "Content-Type": "application/json",
                "api-key": openai.api_key
            }
            payload = {
                "messages": [{"role": "user", "content": f"Correct this transcription:\n\n{transcription}"}],
                "max_tokens": 100
            }

            
            response = requests.post(endpoint, headers=headers, json=payload)

            
            if response.status_code == 200:
                result = response.json()
                corrected_text = result["choices"][0]["message"]["content"].strip()
                st.write("Corrected Transcription:")
                st.text_area("Corrected Transcription", corrected_text, height=150)
            else:
                st.error(f"Azure OpenAI API Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error during text correction: {str(e)}")


    if corrected_text:
        try:
            st.write("Generating new audio...")
            tts_client = tts.TextToSpeechClient()
            input_text = tts.SynthesisInput(text=corrected_text)
            voice = tts.VoiceSelectionParams(
                language_code="en-US", 
                ssml_gender=tts.SsmlVoiceGender.MALE
            )
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
            response = tts_client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )

            with open("new_audio.wav", "wb") as out:
                out.write(response.audio_content)
            st.success("New audio generated successfully.")
        except Exception as e:
            st.error(f"Error during audio synthesis: {str(e)}")


    if os.path.exists("new_audio.wav"):
        try:
            st.write("Replacing audio in the video...")
            new_audio = AudioFileClip("new_audio.wav")
            final_video = video.set_audio(new_audio)
            final_video.write_videofile("output_video.mp4", codec="libx264")

            st.write("Download your updated video:")
            with open("output_video.mp4", "rb") as f:
                st.download_button("Download Video", f, file_name="output_video.mp4", mime="video/mp4")
        except Exception as e:
            st.error(f"Error during video processing: {str(e)}")
    else:
        st.error("New audio file not found. Skipping video processing.")
