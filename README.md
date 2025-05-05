# Supernova

Audio/video transcription and analysis tool built with OpenAI's Whisper and GPT model. 

## Overview

Supernova is a comprehensive desktop application that enables you to:
- Transcribe audio and video files with high accuracy
- Analyze content to extract key learning points
- Identify question-answer pairs within transcripts
- Export results in multiple formats 

## Features

- **Transcription Engine**: Powered by OpenAI's Whisper model
- **Content Analysis**: Automated extraction of insights using GPT model
- **Multiple Export Options**: Save your work in Word/PDF
- **Customizable Prompts**: Tailor the analysis to your specific needs
- **Responsive Design**: Background processing keeps the UI responsive

## Architecture

Supernova uses a modular architecture with several key components:

- **app.py**: Main application entry point and GUI implementation
- **transcription_service.py**: Handles audio transcription and content analysis
- **document_service.py**: Manages document generation and export
- **file_utils.py**: Provides file validation and utility functions

## Installation

### Prerequisites
- Python 
- An OpenAI API key

### Step 1: Clone or Download
```bash
git clone https://github.com/hawkesprocess/supernova.git
cd supernova
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key
Open `config.py` and add your OpenAI API key:
```python
OPENAI_API_KEY = "your-api-key-here"
```

## Usage Workflow

### Basic Workflow
1. Launch the application: `python app.py`
2. Open an audio/video file through the File menu
3. Wait for transcription to complete
4. Click "Analyze Transcript" to generate insights
5. Review the analysis in the dedicated tab
6. Export your results as needed

### Detailed Steps

#### Transcription
1. Start Supernova application
2. Use File > Open to select your audio/video file
3. The transcription process will begin automatically
4. Once complete, you can review and edit the transcript if needed
5. Save the raw transcript using the "Save Transcript" button

#### Analysis
1. After transcription, click the "Analyze Transcript" button
2. The application will process the transcript using GPT models
3. Results are displayed in the Analysis tab
4. Review the content which typically includes:
   - Key Learning Points
   - Questions & Answers

#### Exporting
1. Use the export buttons to save your work
2. Choose between:
   - Word Document (.docx): Creates a formatted document with all content
   - PDF Document (.pdf): Creates a professional PDF with all content
   - Text (via Save Transcript): Saves only the raw transcript

## Customization

### Analysis Prompts
You can customize how Supernova analyzes your transcripts:

1. Click the "Edit Analysis Prompt" button in the Analysis tab
2. Modify the prompt template to fit your needs
3. Save the file and run your next analysis

Example prompt structure:
```
Please analyze the following transcript and extract:

1. KEY LEARNING POINTS: Identify the main educational concepts or insights.
2. QUESTIONS & ANSWERS: Extract significant Q&A pairs.

Format your response as follows:

## KEY LEARNING POINTS
- Point 1
- Point 2
...

## QUESTIONS & ANSWERS
### Question 1
[The question text]

### Answer 1
[The answer text]
...

TRANSCRIPT:
{transcript}
```

## File Format Support

Supernova supports common audio and video formats:

**Audio:**
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- MPGA (.mpga)

**Video:**
- MP4 (.mp4)
- MPEG (.mpeg)

## Extending Supernova

The modular architecture makes it easy to extend Supernova's functionality:

1. **Add New Export Formats**: Extend the DocumentService class
2. **Support More File Types**: Update the SUPPORTED_EXTENSIONS in file_utils.py
3. **Use Different AI Models**: Modify the TranscriptionService class

## Troubleshooting

### Common Issues

**API Key Problems:**
- Ensure your OpenAI API key is correctly set in `config.py`
- Check that your API key has sufficient credits/permissions

**File Format Errors:**
- Verify that your media file is in a supported format
- Try converting problematic files to MP3 or MP4

**Analysis Not Working:**
- Check your internet connection
- Make sure the transcript was successfully generated first
