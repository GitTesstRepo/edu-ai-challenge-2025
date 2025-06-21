import os
import openai
from dotenv import load_dotenv
import argparse
from mutagen import File
import datetime
import json
import re

# --- Configuration ---
API_TIMEOUT = 60.0  # seconds
# ---------------------

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

def transcribe_audio(file_path, timeout=API_TIMEOUT):
    """
    Transcribes the given audio file using OpenAI's Whisper API.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                timeout=timeout,
                prompt="Spoken content only."
            )
        return transcript.text
    except Exception as e:
        return f"Error in transcription: {e}"

def get_audio_duration_ms(file_path):
    """
    Returns the duration of an audio file in milliseconds using mutagen.
    This function is format-agnostic.
    """
    try:
        audio = File(file_path)
        return audio.info.length * 1000 # convert to ms
    except Exception as e:
        print(f"Could not get audio duration: {e}")
        return None

def summarize_text(text, timeout=API_TIMEOUT):
    """
    Summarizes the given text using OpenAI's GPT model.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a highly skilled AI assistant specializing in summarizing audio transcripts. Your goal is to produce a concise, clear summary that captures the core intent, main topics, and key takeaways from the spoken content. Focus on extracting the most critical information and presenting it in an easy-to-read format."},
                {"role": "user", "content": f"Please summarize the following transcript from a spoken audio file. Identify the main purpose, the key points mentioned, and any significant conclusions or action items. Preserve the core intent and takeaways.\n\nTranscript:\n{text}"}
            ],
            timeout=timeout
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in summarization: {e}"

def extract_topics(text, timeout=API_TIMEOUT):
    """
    Extracts semantic topics from the text using a GPT model.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an AI expert in topic extraction. Your task is to identify the main topics from the provided transcript. Please identify at least 3 of the most significant topics, but include all major topics present in the text. For each topic, provide a short, keyword-style name (ideally 2-4 words). Return the output as a JSON array of objects, where each object has a 'topic' key (the short topic name) and a 'mentions' key (an estimated count of how many times the topic was discussed). Only return the JSON array and nothing else."},
                {"role": "user", "content": f"Please extract the main topics from the following transcript:\n\n{text}"}
            ],
            timeout=timeout
        )
        # The model should return a JSON string, so we parse it.
        topics_json = response.choices[0].message.content.strip()
        try:
            return json.loads(topics_json)
        except json.JSONDecodeError:
            error_message = f"Failed to decode JSON from API response. Response was: {topics_json}"
            print(error_message)
            return {"error": error_message}
            
    except Exception as e:
        # Return a dictionary with an error key to be distinguishable from a successful list of topics
        return {"error": f"An explicit error occurred during topic extraction: {e}"}

def analyze_transcript(transcript, duration_ms):
    """
    Analyzes the transcript for word count and speaking speed.
    """
    words = transcript.split()
    word_count = len(words)
    
    duration_minutes = duration_ms / 60000.0 if duration_ms else 0
    speaking_speed = word_count / duration_minutes if duration_minutes > 0 else 0

    return {
        "word_count": word_count,
        "speaking_speed_wpm": int(speaking_speed)
    }

def clean_transcription(transcript):
    """
    Cleans the transcription by removing minimal artifacts that indicate silence.
    Returns empty string if the transcript only contains silence indicators.
    """
    if not transcript:
        return ""
    
    # Remove common silence indicators
    cleaned = transcript.strip()
    
    # Remove patterns that indicate silence or minimal content
    silence_patterns = [
        r'^[.\s]+$',  # Only dots and spaces
        r'^\.+$',     # Only dots
        r'^[\s\.]+$', # Only spaces and dots
        r'^[^\w\s]*$', # No actual words, only punctuation/spaces
    ]
    
    for pattern in silence_patterns:
        if re.match(pattern, cleaned):
            return ""
    
    # If cleaned transcript is very short and contains mostly punctuation, treat as silence
    if len(cleaned) <= 10 and not any(word.isalpha() for word in cleaned.split()):
        return ""
    
    return cleaned

def process_audio_file(audio_path, timeout):
    """
    Runs the full analysis pipeline for a given audio file path.
    This function contains the core logic of the application.
    """
    if not os.path.exists(audio_path):
        print(f"Error: The file '{audio_path}' does not exist.")
        return

    # --- File Naming ---
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    transcription_filename = f"{base_name}_transcription_{timestamp}.md"
    summary_filename = f"{base_name}_summary_{timestamp}.md"
    analysis_filename = f"{base_name}_analysis_{timestamp}.json"
    
    # 1. Transcribe Audio
    print("Transcribing audio...")
    transcription = transcribe_audio(audio_path, timeout)
    if transcription.startswith("Error"):
        print(f"\n--- SCRIPT HALTED ---")
        print(f"An error occurred: {transcription}")
        return

    # Clean the transcription to remove silence artifacts
    cleaned_transcription = clean_transcription(transcription)
    
    # Check if the cleaned transcription is empty (silent file)
    if not cleaned_transcription:
        print("Detected silent or near-silent audio file.")
        print("Creating empty transcription file.")
        
        # Create empty files
        with open(transcription_filename, "w", encoding="utf-8") as f:
            f.write("")
        
        with open(summary_filename, "w", encoding="utf-8") as f:
            f.write("This audio file contains no detectable speech content.")
        
        with open(analysis_filename, "w", encoding="utf-8") as f:
            f.write('{\n  "word_count": 0,\n  "speaking_speed_wpm": 0,\n  "frequently_mentioned_topics": []\n}')
        
        print(f"Transcription saved to {transcription_filename}")
        print(f"Summary saved to {summary_filename}")
        print(f"Analysis saved to {analysis_filename}")
        
        print("\n--- Summary ---")
        print("This audio file contains no detectable speech content.")
        print("\n--- Analytics ---")
        print("Total Word Count: 0")
        print("Speaking Speed: 0 WPM")
        print("Frequently Mentioned Topics: None")
        print("\nProcessing complete.")
        return

    # Save combined transcription
    with open(transcription_filename, "w", encoding="utf-8") as f:
        f.write(cleaned_transcription)
    print(f"Transcription saved to {transcription_filename}")

    # 2. Summarize Transcription
    print("\nSummarizing transcription...")
    summary = summarize_text(cleaned_transcription, timeout)
    if summary.startswith("Error"):
        print(f"\n--- SCRIPT HALTED ---")
        print(f"An error occurred: {summary}")
        return
        
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Summary saved to {summary_filename}")

    # 3. Analyze Transcript
    print("\nAnalyzing transcript...")
    duration_ms = get_audio_duration_ms(audio_path)
    base_analytics = analyze_transcript(cleaned_transcription, duration_ms)
    topics = extract_topics(cleaned_transcription, timeout)
    if isinstance(topics, dict) and "error" in topics:
        print(f"\n--- SCRIPT HALTED ---")
        print(f"An error occurred: {topics['error']}")
        return

    analytics = {**base_analytics, "frequently_mentioned_topics": topics}

    # Manually format the 'frequently_mentioned_topics' part for specific layout
    topics_list = []
    if isinstance(analytics.get('frequently_mentioned_topics'), list):
        for item in analytics['frequently_mentioned_topics']:
            # Manually construct the string for each object to include inner spaces
            topic_str = f'{{ "topic": {json.dumps(item.get("topic", "N/A"))}, "mentions": {item.get("mentions", 0)} }}'
            topics_list.append("    " + topic_str)
    
    formatted_topics_str = ",\n".join(topics_list)

    # Manually construct the full JSON string to match the user's requested format
    analysis_json_string = f"""{{
  "word_count": {analytics['word_count']},
  "speaking_speed_wpm": {analytics['speaking_speed_wpm']},
  "frequently_mentioned_topics": [
{formatted_topics_str}
  ]
}}"""

    with open(analysis_filename, "w", encoding="utf-8") as f:
        f.write(analysis_json_string)
    print(f"Analysis saved to {analysis_filename}")

    # 4. Print Summary and Analysis to Console
    print("\n--- Summary ---")
    print(summary)
    print("\n--- Analytics ---")
    print(f"Total Word Count: {analytics['word_count']}")
    print(f"Speaking Speed: {analytics['speaking_speed_wpm']} WPM")
    print("Frequently Mentioned Topics:")
    # Ensure topics is a list before iterating
    if isinstance(analytics.get('frequently_mentioned_topics'), list):
        for item in analytics['frequently_mentioned_topics']:
            print(f"- {item.get('topic', 'N/A')}: {item.get('mentions', 'N/A')} mentions")

    print("\nProcessing complete.")

def main():
    parser = argparse.ArgumentParser(description="Transcribe, summarize, and analyze an audio file.")
    parser.add_argument("audio_file", help="Path to the audio file to process.")
    parser.add_argument("--timeout", type=float, default=API_TIMEOUT, help=f"API request timeout in seconds (default: {API_TIMEOUT})")
    args = parser.parse_args()
    process_audio_file(args.audio_file, args.timeout)

if __name__ == "__main__":
    main() 