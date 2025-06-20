# Audio Transcription and Analysis Tool

This console application transcribes a given audio file, summarizes the content, and provides analytics on the transcription.

## Features

- Transcribes audio files using OpenAI's Whisper API. Handles various formats (e.g., MP3, WAV, M4A, FLAC).
- Summarizes the transcription using a GPT model (`gpt-4.1-mini`).
- Extracts and displays analytics:
  - Total word count
  - Speaking speed (words per minute)
  - Top 3+ most frequently mentioned topics
- Saves the full transcription to a timestamped `.md` file.
- Saves the summary to a timestamped `.md` file.
- Saves the analysis to a timestamped `.json` file.

## Prerequisites

- Python 3.7+
- An OpenAI API key.

## Installation

1.  **Clone the repository or download the files.**

2.  **Navigate to the project directory:**
    ```bash
    cd /path/to/your/project
    ```

3.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file** in the root of the project directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
    Replace `your_openai_api_key_here` with your actual key.

## Usage

Execute the script from your terminal, providing the path to your audio file as an argument.

```bash
python audio_analyzer.py "path/to/your/audio.mp3"
```

### Example

```bash
python audio_analyzer.py CAR0004.mp3
```

## Outputs

For each audio file processed, the application generates three unique output files in the same directory:

1.  **Transcription**: `[original_filename]_transcription_[timestamp].md`
    *   A markdown file containing the full, verbatim transcript of the audio.

2.  **Summary**: `[original_filename]_summary_[timestamp].md`
    *   A markdown file containing a concise summary of the transcript, including the main purpose, key points, and action items.

3.  **Analysis**: `[original_filename]_analysis_[timestamp].json`
    *   A JSON file with a detailed analysis of the transcript, including:
        *   `word_count`: The total number of words spoken.
        *   `speaking_speed_wpm`: The average speaking speed in words per minute.
        *   `frequently_mentioned_topics`: A list of the most significant semantic topics (at least 3) and how often they were mentioned.

The summary and analysis are also printed to the console upon completion. 