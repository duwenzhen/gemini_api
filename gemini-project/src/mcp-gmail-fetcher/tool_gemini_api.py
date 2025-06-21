from google import genai
from google.genai import types
import wave
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

async def get_response_from_flash_model(prompt : str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
        ),
    )
    return response.text

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

async def get_response_from_text_to_voice_model(prompt : str, startdate  = str, enddate = str):
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",  # Your specified model
        contents=prompt,  # Pass the prepared content here
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                    )
                )
            ),
        ),
    )
    data = response.candidates[0].content.parts[0].inline_data.data

    file_name = 'email_summary_' + startdate + '_' + enddate + '.wav'
    wave_file(file_name, data)
    return file_name