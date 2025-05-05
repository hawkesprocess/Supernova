"""
Utility functions for file validation and application setup.
"""

import os
import mimetypes

# Constants
SUPPORTED_MIMETYPES = [
    'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav', 
    'audio/x-m4a', 'audio/mp4', 'video/mp4', 'video/mpeg'
]
SUPPORTED_EXTENSIONS = ['.mp3', '.wav', '.mp4', '.m4a', '.mpeg', '.mpga']
PROMPT_DIR = "prompts"
PROMPT_FILE = os.path.join(PROMPT_DIR, "analysis_prompt.txt")

def validate_file(file_path):
    """
    Check if file is a supported audio/video format
    
    Args:
        file_path (str): Path to the file to validate
        
    Returns:
        bool: True if the file is supported, False otherwise
    """
    if not os.path.isfile(file_path):
        return False
        
    # Check extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext in SUPPORTED_EXTENSIONS:
        return True
        
    # Check mimetype
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and any(mime_type.startswith(t) for t in SUPPORTED_MIMETYPES):
        return True
        
    return False

def setup_prompt_files():
    """
    Create prompts directory and default prompt file if needed
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        if not os.path.exists(PROMPT_DIR):
            os.makedirs(PROMPT_DIR)

        if not os.path.exists(PROMPT_FILE):
            default_prompt = """Please analyze the following transcript and extract:

1. KEY LEARNING POINTS: Identify the main educational concepts, lessons, or insights presented in the content.
2. QUESTIONS & ANSWERS: For each significant question in the transcript, provide both the question and its corresponding answer.

Format your response as follows:

## KEY LEARNING POINTS
- Point 1
- Point 2
- Point 3
...

## QUESTIONS & ANSWERS

### Question 1
[The exact question from the transcript]

### Answer 1
[The answer provided to Question 1]

### Question 2
[The exact question from the transcript]

### Answer 2
[The answer provided to Question 2]

...and so on for all significant question-answer pairs.

TRANSCRIPT:
{transcript}"""
            with open(PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(default_prompt)
        
        return True
    except Exception:
        return False

def get_supported_filetypes():
    """
    Get a list of supported file types for file dialogs
    
    Returns:
        list: List of tuples (description, extensions)
    """
    return [
        ("Audio Files", "*.mp3 *.wav *.m4a *.mpga"),
        ("Video Files", "*.mp4 *.mpeg"),
        ("All Files", "*.*")
    ] 