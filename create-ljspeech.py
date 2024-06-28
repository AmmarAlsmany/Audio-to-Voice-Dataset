import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence
import pandas as pd
import os

# Initialize Whisper model
model = whisper.load_model("base")

# Load audio file
audio_path = "./test-data/thorsten-voice_en.wav"
audio = AudioSegment.from_wav(audio_path)

# Parameters for splitting on silence
min_silence_len = 500  # minimum length of silence (in ms) to be used for a split
silence_thresh = audio.dBFS - 14  # silence threshold (14 dB below the average dBFS)
keep_silence = 200  # amount of silence (in ms) to leave at the beginning and end of each chunk

# Split the audio into chunks based on silence
audio_chunks = split_on_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh, keep_silence=keep_silence)

# Create directories to save the split audio files and metadata
output_dir = "output"
audio_dir = os.path.join(output_dir, "audio")
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

metadata = []

# Transcribe each chunk and save with metadata
for i, chunk in enumerate(audio_chunks):
    # Export chunk as temporary wav file
    chunk_path = os.path.join(output_dir, f"chunk_{i}.wav")
    chunk.export(chunk_path, format="wav")
    
    # Transcribe chunk
    result = model.transcribe(chunk_path)
    
    # Get the transcribed text
    text = result['text'].strip()
    
    # Save chunk with unique ID
    sentence_id = f"LJ{str(i+1).zfill(4)}"
    sentence_path = os.path.join(audio_dir, f"{sentence_id}.wav")
    chunk.export(sentence_path, format="wav")
    
    metadata.append({
        "ID": sentence_id,
        "text": text
    })
    
    # Remove the temporary chunk file
    os.remove(chunk_path)

# Create a metadata.csv file with sentences and corresponding audio file IDs
metadata_df = pd.DataFrame(metadata)
metadata_csv_path = os.path.join(output_dir, "metadata.csv")
metadata_df.to_csv(metadata_csv_path, sep="|", header=False, index=False)

print(f"Processed {len(audio_chunks)} sentences.")
print(f"CSV file saved to {metadata_csv_path}")