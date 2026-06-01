import runpod
import os
import subprocess
import requests
import base64
from pydub import AudioSegment

def download_file(url, local_path):
    response = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(response.content)

def handler(job):
    job_input = job['input']
    audio_url = job_input.get('audio_url')
    model_name = job_input.get('model_name', 'jamaican_artist.pth')
    
    if not audio_url:
        return {"error": "Missing audio_url in input"}
    
    # 1. Download the Suno MP3
    print("Downloading source audio...")
    os.makedirs("/tmp/audio", exist_ok=True)
    source_path = "/tmp/audio/source.mp3"
    download_file(audio_url, source_path)
    
    # 2. Split Vocals and Beat using Demucs
    print("Splitting audio with Demucs...")
    # Demucs output will go to /tmp/audio/separated/htdemucs/source/
    subprocess.run(["demucs", "-n", "htdemucs", "-o", "/tmp/audio", source_path], check=True)
    
    vocals_path = "/tmp/audio/htdemucs/source/vocals.wav"
    beat_path = "/tmp/audio/htdemucs/source/no_vocals.wav"
    
    # 3. Swap Voice using RVC (Placeholder logic)
    print(f"Applying RVC Voice Model: {model_name}...")
    cloned_vocals_path = "/tmp/audio/cloned_vocals.wav"
    
    # --- RVC INFERENCE SCRIPT WOULD RUN HERE ---
    # Example: subprocess.run(["python", "rvc/infer_cli.py", "--input", vocals_path, "--model", model_name, "--output", cloned_vocals_path])
    # For now, we will just pass through the vocals to simulate the pipeline
    cloned_vocals_path = vocals_path 
    
    # 4. Merge New Vocals with Original Beat
    print("Mixing final track...")
    final_output_path = "/tmp/audio/final_song.mp3"
    
    beat = AudioSegment.from_file(beat_path)
    vocals = AudioSegment.from_file(cloned_vocals_path)
    
    # Overlay vocals on beat
    mixed = beat.overlay(vocals)
    mixed.export(final_output_path, format="mp3")
    
    # 5. Return the Base64 Audio to the App
    print("Encoding response...")
    with open(final_output_path, "rb") as f:
        encoded_audio = base64.b64encode(f.read()).decode('utf-8')
        
    return {
        "status": "SUCCESS",
        "audio_base64": encoded_audio
    }

# Start the RunPod Serverless worker
runpod.serverless.start({"handler": handler})
