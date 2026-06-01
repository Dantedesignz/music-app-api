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
    action = job_input.get('action', 'swap') # 'swap' or 'split'
    audio_base64 = job_input.get('audio_base64')
    model_name = job_input.get('model_name', 'jamaican_artist.pth')
    
    if not audio_base64:
        return {"error": "Missing audio_base64 in input"}
    
    job_id = job.get('id', 'default_job')
    
    # 1. Decode the MP3 from Base64
    print(f"Executing action: {action} for job {job_id}")
    os.makedirs("/tmp/audio", exist_ok=True)
    source_path = f"/tmp/audio/{job_id}.mp3"
    
    with open(source_path, "wb") as f:
        f.write(base64.b64decode(audio_base64))
    
    # 2. Split Vocals and Beat using Demucs
    print("Splitting audio with Demucs...")
    # Demucs output will go to /tmp/audio/htdemucs/{job_id}/
    subprocess.run(["demucs", "--two-stems", "vocals", "-n", "htdemucs", "-o", "/tmp/audio", source_path], check=True)
    
    vocals_path = f"/tmp/audio/htdemucs/{job_id}/vocals.wav"
    beat_path = f"/tmp/audio/htdemucs/{job_id}/no_vocals.wav"
    
    if action == "split":
        print("Action is SPLIT. Converting to MP3 and returning isolated tracks...")
        vocals_mp3 = f"/tmp/audio/htdemucs/{job_id}/vocals.mp3"
        beat_mp3 = f"/tmp/audio/htdemucs/{job_id}/no_vocals.mp3"
        
        # Compress to MP3
        AudioSegment.from_file(vocals_path).export(vocals_mp3, format="mp3", bitrate="192k")
        AudioSegment.from_file(beat_path).export(beat_mp3, format="mp3", bitrate="192k")
        
        with open(vocals_mp3, "rb") as fv:
            vocals_b64 = base64.b64encode(fv.read()).decode('utf-8')
        with open(beat_mp3, "rb") as fb:
            beat_b64 = base64.b64encode(fb.read()).decode('utf-8')
            
        return {
            "status": "SUCCESS",
            "vocals_base64": vocals_b64,
            "beat_base64": beat_b64
        }
        
    # 3. Swap Voice using RVC (If action is swap)
    print(f"Applying RVC Voice Model: {model_name}...")
    cloned_vocals_path = f"/tmp/audio/cloned_vocals_{job_id}.wav"
    
    # --- RVC INFERENCE SCRIPT WOULD RUN HERE ---
    # Example: subprocess.run(["python", "rvc/infer_cli.py", "--input", vocals_path, "--model", model_name, "--output", cloned_vocals_path])
    # For now, we simulate the swap pipeline
    cloned_vocals_path = vocals_path 
    
    # 4. Merge New Vocals with Original Beat
    print("Mixing final track...")
    final_output_path = f"/tmp/audio/final_song_{job_id}.mp3"
    
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
