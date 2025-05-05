"""
Supernova - GUI for transcribing and analyzing audio/video files.

Setup instructions:
1. Set OPENAI_API_KEY in config.py.
2. Edit prompts/analysis_prompt.txt to refine how the transcript is analyzed.
3. Run `python app.py`.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import openai
import re

# Import utility modules
from file_utils import (
    validate_file, setup_prompt_files, 
    get_supported_filetypes, PROMPT_FILE
)
from transcription_service import TranscriptionService
from document_service import DocumentService

# Configure OpenAI API
def setup_api():
    """Configure OpenAI API and return success status"""
    try:
        from config import OPENAI_API_KEY
        if not OPENAI_API_KEY:
            raise ValueError("API key not set")
        openai.api_key = OPENAI_API_KEY
        return True
    except (ImportError, ValueError):
        # If config.py doesn't exist or key is not set, create a template
        with open("config.py", "w") as f:
            f.write("# Replace with your actual OpenAI API key\nOPENAI_API_KEY = \"\"")
        messagebox.showerror("API Key Missing", "OpenAI API key not found! Please set your API key in config.py and restart the application.")
        return False

class Supernova:
    """Main application class for Supernova"""
    
    def __init__(self, root):
        """Initialize the application UI and state"""
        # Store the root window
        self.root = root
        self.root.title("Supernova")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Configure base styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=('Helvetica', 10))
        self.style.configure("TButton", font=('Helvetica', 10))
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
        self.style.configure("Status.TLabel", font=('Helvetica', 10))
        
        # Initialize state variables
        self.current_file = None
        self.current_transcript = None
        self.analysis_results = None
        self.is_transcribing = False
        self.is_analyzing = False
        
        # Set up UI
        self._create_ui()
    
    def _create_ui(self):
        """Create all UI components"""
        # Create main notebook for tabs
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create transcription tab
        self.transcription_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.transcription_frame, text="Transcription")
        
        # Create analysis tab
        self.analysis_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.analysis_frame, text="Analysis")
        
        # Build the tabs UI
        self._build_transcription_tab()
        self._build_analysis_tab()
        
        # Add a file menu
        self._add_file_menu()
    
    def _add_file_menu(self):
        """Add a file menu to the application"""
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        
        self.root.config(menu=menubar)
    
    def _build_transcription_tab(self):
        """Build the transcription tab UI"""
        frame = self.transcription_frame
        
        # Instruction label
        ttk.Label(frame, text="Use File > Open to select an audio or video file", style="Header.TLabel").pack(pady=(15,5))
        
        # File label
        self.file_label = ttk.Label(frame, text="", foreground="blue")
        self.file_label.pack(pady=(0, 10))
        
        # Transcript text area
        self.transcript_text = scrolledtext.ScrolledText(frame, height=20, width=80, wrap=tk.WORD)
        self.transcript_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status frame
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(status_frame, text="Status:", style="Status.TLabel").pack(side=tk.LEFT, padx=(0,5))
        self.status_label = ttk.Label(status_frame, text="Idle", foreground="blue")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 15))
        
        self.save_btn = ttk.Button(button_frame, text="Save Transcript", command=self.save_transcript, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.analyze_btn = ttk.Button(button_frame, text="Analyze Transcript", command=self.analyze_transcript, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_ui)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
    
    def _build_analysis_tab(self):
        """Build the analysis tab UI"""
        frame = self.analysis_frame
        
        # Analysis text area
        self.analysis_text = scrolledtext.ScrolledText(frame, height=20, width=80, wrap=tk.WORD, font=('Helvetica', 10))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export buttons frame
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill=tk.X, padx=10, pady=(5, 15))
        
        self.export_word_btn = ttk.Button(export_frame, text="Export to Word", command=self.export_to_word, state=tk.DISABLED)
        self.export_word_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_pdf_btn = ttk.Button(export_frame, text="Export to PDF", command=self.export_to_pdf, state=tk.DISABLED)
        self.export_pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Add an edit prompt button
        self.edit_prompt_btn = ttk.Button(export_frame, text="Edit Analysis Prompt", command=self.edit_analysis_prompt)
        self.edit_prompt_btn.pack(side=tk.RIGHT, padx=5)
    
    def open_file(self):
        """Open a file dialog to select an audio/video file"""
        file_path = filedialog.askopenfilename(filetypes=get_supported_filetypes())
        if file_path and validate_file(file_path):
            self.process_file(file_path)
        elif file_path:
            messagebox.showerror("Unsupported Format", "Please select an audio or video file (mp3, wav, mp4, etc.)")
    
    def process_file(self, file_path):
        """Process a file and start transcription"""
        if not self.is_transcribing:
            self.current_file = file_path
            self.file_label.config(text=f"File: {os.path.basename(file_path)}")
            self.status_label.config(text="Starting transcription...", foreground="blue")
            
            # Start transcription in a separate thread
            self.is_transcribing = True
            threading.Thread(target=self._transcribe_thread, args=(file_path,), daemon=True).start()
    
    def _transcribe_thread(self, file_path):
        """Run transcription in a background thread"""
        transcript, error = TranscriptionService.transcribe(file_path)
        
        if transcript:
            self.current_transcript = transcript
            self.root.after(0, lambda: self.transcript_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.transcript_text.insert(tk.END, transcript))
            self.root.after(0, lambda: self.status_label.config(text="Transcription complete!", foreground="green"))
            self.root.after(0, lambda: self.save_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
        else:
            error_message = f"Error: {error}"
            self.root.after(0, lambda: self.status_label.config(text=error_message, foreground="red"))
            self.root.after(0, lambda: self.transcript_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.transcript_text.insert(tk.END, f"Failed to transcribe file.\nError: {error}"))
        
        self.is_transcribing = False
    
    def analyze_transcript(self):
        """Analyze the transcript using OpenAI ChatCompletion API"""
        if not self.current_transcript:
            messagebox.showerror("No Transcript", "No transcript to analyze. Please transcribe a file first.")
            return
        
        self.is_analyzing = True
        self.status_label.config(text="Analyzing transcript...", foreground="orange")
        self.analyze_btn.config(state=tk.DISABLED)
        self.export_word_btn.config(state=tk.DISABLED)
        self.export_pdf_btn.config(state=tk.DISABLED)
        
        # Create a thread for analysis
        threading.Thread(target=self._analyze_thread, daemon=True).start()
    
    def _analyze_thread(self):
        """Run analysis in a background thread"""
        results, error = TranscriptionService.analyze(self.current_transcript, PROMPT_FILE)
        
        if results:
            self.analysis_results = results
            self.root.after(0, lambda: self._update_analysis_ui())
        else:
            error_message = f"Analysis error: {error}"
            self.root.after(0, lambda: self.status_label.config(text=error_message, foreground="red"))
        
        self.is_analyzing = False
        self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
    
    def _update_analysis_ui(self):
        """Update UI with analysis results"""
        # Update analysis text
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, self.analysis_results.get('full_analysis', ''))
        
        # Apply formatting
        self._apply_text_formatting()
        
        # Update status and enable export buttons
        self.status_label.config(text="Analysis complete!", foreground="green")
        self.export_word_btn.config(state=tk.NORMAL)
        self.export_pdf_btn.config(state=tk.NORMAL)
        
        # Switch to Analysis tab
        self.main_notebook.select(1)
    
    def _apply_text_formatting(self):
        """Apply basic formatting to the analysis text"""
        # Define tags
        self.analysis_text.tag_configure("h1", font=("Helvetica", 14, "bold"))
        self.analysis_text.tag_configure("h2", font=("Helvetica", 12, "bold"))
        
        # Apply formatting to headings
        content = self.analysis_text.get(1.0, tk.END)
        
        # Find all occurrences of h1 headings (##)
        for match in re.finditer(r'^## (.+)$', content, re.MULTILINE):
            start_idx = f"1.0 + {match.start()} chars"
            end_idx = f"1.0 + {match.end()} chars"
            self.analysis_text.tag_add("h1", start_idx, end_idx)
        
        # Find all occurrences of h2 headings (###)
        for match in re.finditer(r'^### (.+)$', content, re.MULTILINE):
            start_idx = f"1.0 + {match.start()} chars"
            end_idx = f"1.0 + {match.end()} chars"
            self.analysis_text.tag_add("h2", start_idx, end_idx)
    
    def save_transcript(self):
        """Save the transcript to a text file"""
        if not self.current_file or not self.current_transcript:
            return
            
        # Generate output file path
        default_path = os.path.splitext(self.current_file)[0] + '.txt'
        
        # Ask user for save location
        output_path = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.current_file),
            initialfile=os.path.basename(default_path),
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not output_path:
            return  # User cancelled
        
        success, error = DocumentService.save_text(self.current_transcript, output_path)
        
        if success:
            self.status_label.config(text=f'Transcript saved to: {output_path}', foreground="green")
            messagebox.showinfo("Success", f'Transcript saved successfully to:\n{output_path}')
        else:
            self.status_label.config(text=f'Error saving file: {error}', foreground="red")
            messagebox.showerror("Error", f'Failed to save transcript:\n{error}')
    
    def export_to_word(self):
        """Export transcript and analysis to a Word document"""
        if not self.current_file or not self.current_transcript or not self.analysis_results:
            messagebox.showerror("Error", "Nothing to export. Please complete transcription and analysis first.")
            return
        
        # Generate output file path
        base_output_path = os.path.splitext(self.current_file)[0]
        default_filename = f"{os.path.basename(base_output_path)}_analysis.docx"
        
        # Ask user for output file location
        output_path = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.current_file),
            initialfile=default_filename,
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        
        if not output_path:
            return  # User cancelled
        
        success, error = DocumentService.export_word(
            self.current_transcript, 
            self.analysis_results.get('full_analysis', ''),
            output_path
        )
        
        if success:
            self.status_label.config(text=f'Word document saved to: {output_path}', foreground="green")
            messagebox.showinfo("Success", f'Word document saved successfully to:\n{output_path}')
        else:
            self.status_label.config(text=f'Error exporting to Word: {error}', foreground="red")
            messagebox.showerror("Error", f'Failed to export to Word:\n{error}')
    
    def export_to_pdf(self):
        """Export transcript and analysis to a PDF document"""
        if not self.current_file or not self.current_transcript or not self.analysis_results:
            messagebox.showerror("Error", "Nothing to export. Please complete transcription and analysis first.")
            return
        
        # Generate output file path
        base_output_path = os.path.splitext(self.current_file)[0]
        default_filename = f"{os.path.basename(base_output_path)}_analysis.pdf"
        
        # Ask user for output file location
        output_path = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.current_file),
            initialfile=default_filename,
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not output_path:
            return  # User cancelled
        
        success, error = DocumentService.export_pdf(
            self.current_transcript, 
            self.analysis_results.get('full_analysis', ''),
            output_path
        )
        
        if success:
            self.status_label.config(text=f'PDF document saved to: {output_path}', foreground="green")
            messagebox.showinfo("Success", f'PDF document saved successfully to:\n{output_path}')
        else:
            self.status_label.config(text=f'Error exporting to PDF: {error}', foreground="red")
            messagebox.showerror("Error", f'Failed to export to PDF:\n{error}')
    
    def edit_analysis_prompt(self):
        """Open the analysis prompt file in the default text editor"""
        try:
            if sys.platform == 'win32':
                os.startfile(PROMPT_FILE)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{PROMPT_FILE}"')
            else:  # Linux
                os.system(f'xdg-open "{PROMPT_FILE}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open prompt file: {str(e)}")
    
    def clear_ui(self):
        """Clear the UI elements and reset state variables"""
        # Clear transcription tab
        self.file_label.config(text="")
        self.transcript_text.delete(1.0, tk.END)
        self.status_label.config(text="Idle", foreground="blue")
        self.save_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)
        
        # Clear analysis tab
        self.analysis_text.delete(1.0, tk.END)
        
        # Disable export buttons
        self.export_word_btn.config(state=tk.DISABLED)
        self.export_pdf_btn.config(state=tk.DISABLED)
        
        # Reset state variables
        self.current_file = None
        self.current_transcript = None
        self.analysis_results = None

def setup_dragdrop(root, app):
    """Set up drag and drop support if available"""
    try:
        # Try with TkDnD
        root.tk.eval('package require tkdnd')
        root.tk.call('tkdnd::drop_target', root, {
            'DND_Files': lambda e, data: app.process_file(data),
            'DND_Text': lambda e, data: None  # Not handling text drops
        })
        return True
    except:
        # Try with windnd for Windows
        try:
            import windnd
            windnd.hook_dropfiles(root, func=lambda files: app.process_file(files[0].decode('utf-8')))
            return True
        except:
            return False

def main():
    """Run the Supernova application"""
    # Setup API
    if not setup_api():
        sys.exit(1)
    
    # Setup prompt files
    setup_prompt_files()
    
    # Initialize the app
    root = tk.Tk()
    app = Supernova(root)
    
    # Try to set up drag-and-drop
    try:
        setup_dragdrop(root, app)
    except Exception as e:
        print(f"Drag and drop not available: {e}")
    
    # Start the app
    root.mainloop()

if __name__ == "__main__":
    main() 