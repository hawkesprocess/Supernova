"""
Handles audio/video transcription and analysis using OpenAI APIs.
"""

import os
import tempfile
import shutil
import re
import openai

class TranscriptionService:
    """
    Handles audio/video transcription and content analysis using OpenAI APIs
    """
    
    @staticmethod
    def transcribe(file_path):
        """
        Transcribe an audio/video file using OpenAI's Whisper API
        
        Args:
            file_path (str): Path to the audio/video file
            
        Returns:
            tuple: (transcript_text, error_message)
        """
        try:
            # Create a temporary file copy in case the original has a non-standard extension
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "temp_audio.mp3")
            shutil.copy2(file_path, temp_file)

            # Call OpenAI API for transcription
            with open(temp_file, 'rb') as audio_file:
                result = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Return the transcript text
            return result.text, ""
            
        except Exception as e:
            return None, str(e)
        
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    @staticmethod
    def analyze(transcript, prompt_file):
        """
        Analyze a transcript using OpenAI's GPT model
        
        Args:
            transcript (str): The transcript text to analyze
            prompt_file (str): Path to the analysis prompt template file
            
        Returns:
            tuple: (analysis_results, error_message)
        """
        try:
            # Read the analysis prompt template
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            else:
                return None, "Analysis prompt file not found!"
            
            # Format the prompt with the transcript
            prompt_text = prompt_template.format(transcript=transcript)
            
            # Call OpenAI ChatCompletion API
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer."},
                    {"role": "user", "content": prompt_text}
                ]
            )
            
            # Extract the analysis from the response
            analysis = completion.choices[0].message.content
            
            # Prepare results object
            results = {'full_analysis': analysis}
            
            # Try to extract specific sections if they exist in standard format
            try:
                learning_points = TranscriptionService._extract_section(analysis, r'## KEY LEARNING POINTS\s*([\s\S]*?)(?=##|$)')
                qa_pairs = TranscriptionService._extract_section(analysis, r'## QUESTIONS & ANSWERS\s*([\s\S]*?)(?=$)')
                
                if learning_points:
                    results['learning_points'] = learning_points.strip()
                if qa_pairs:
                    results['qa_pairs'] = qa_pairs.strip()
            except:
                # If extraction fails, just continue with full analysis
                pass
                
            return results, ""
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def _extract_section(text, pattern):
        """
        Extract a section from text using a regex pattern
        
        Args:
            text (str): The source text
            pattern (str): The regex pattern to match
            
        Returns:
            str: The extracted section or empty string if not found
        """
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return "" 