import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from deep_translator import GoogleTranslator
import re
import subprocess

class SubtitleTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitle Translator")

        self.fileName = ""
        self.subtitles = []
        self.subtitle_language = ""

        
        self.selectFileBtn = ttk.Button(root, text="Select Video File", command=self.selectFile)
        self.selectFileBtn.grid(row=0, column=0, padx=10, pady=10)

        self.videoNameLabel = ttk.Label(root, text="Selected Video: None")
        self.videoNameLabel.grid(row=0, column=1, padx=10, pady=10)

        self.subtitleTrackComboBox = ttk.Combobox(root, values=["Select Subtitle Track"])
        self.subtitleTrackComboBox.grid(row=1, column=0, padx=10, pady=10)

        self.targetLanguageComboBox = ttk.Combobox(root, values=["Select Target Language", "en", "fr", "es", "hi", "te", "ta"])
        self.targetLanguageComboBox.grid(row=1, column=1, padx=10, pady=10)

        self.translateBtn = ttk.Button(root, text="Translate Subtitles", command=self.translateSubtitles)
        self.translateBtn.grid(row=2, column=0, padx=10, pady=10)

        self.addSubtitlesBtn = ttk.Button(root, text="Add Translated Subtitles to Video", command=self.addSubtitlesToVideo)
        self.addSubtitlesBtn.grid(row=2, column=1, padx=10, pady=10)

        self.outputTextEdit = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
        self.outputTextEdit.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def selectFile(self):
        fileName = filedialog.askopenfilename(title="Select Video File")
        if fileName:
            self.fileName = fileName
            self.videoNameLabel.config(text=f"Selected Video: {self.fileName}")
            self.loadSubtitleTracks()

    def loadSubtitleTracks(self):
        
        probe_result = subprocess.run([
            r'C:\ffmpeg\bin\ffprobe',
            '-v', 'error',
            '-select_streams', 's',
            '-show_entries', 'stream_tags=language,title',
            '-of', 'csv=p=0',
            self.fileName
        ], capture_output=True, text=True)

        subtitle_tracks = probe_result.stdout.strip().split('\n')
        self.subtitleTrackComboBox['values'] = ["Select Subtitle Track"] + subtitle_tracks
        self.outputTextEdit.insert(tk.END, 'Subtitle tracks loaded.\n')

    def extractSubtitles(self):
        selected_track = self.subtitleTrackComboBox.get()

        if selected_track != "Select Subtitle Track":
            track_index = self.subtitleTrackComboBox.current() - 1

            
            output_subtitle = 'selected_subtitle.srt'

            subprocess.run([
                r'C:\ffmpeg\bin\ffmpeg',
                '-y',
                '-i', self.fileName,
                '-map', f'0:s:{track_index}',
                output_subtitle
            ])

            
            with open(output_subtitle, 'r', encoding='utf-8') as f:
                self.subtitles = f.read().split('\n\n')

            self.outputTextEdit.insert(tk.END, f'Subtitle segments extracted from {selected_track}.\n')

    def clean_subtitle_text(self, text):
        
        return text

    def translateSubtitles(self):
        self.extractSubtitles()
        targetLanguage = self.targetLanguageComboBox.get()

        if targetLanguage != "Select Target Language":
            translator = GoogleTranslator(target=targetLanguage)
            translated_subtitles = []

            for subtitle in self.subtitles:
                lines = subtitle.strip().split('\n')
                if len(lines) >= 3:
                    subtitle_number = lines[0]
                    timestamp = lines[1]
                    subtitle_text = '\n'.join(lines[2:])

                    cleaned_text = self.clean_subtitle_text(subtitle_text)
                    try:
                        translated_text = translator.translate(cleaned_text)
                    except Exception as e:
                        self.outputTextEdit.insert(tk.END, f"Translation error: {e}\n")
                        continue

                    cleaned_translated_text = self.clean_subtitle_text(translated_text)
                    translated_subtitles.append(f'{subtitle_number}\n{timestamp}\n{cleaned_translated_text}\n')
                    translated_subtitles.append('\n')

            with open('translated_subtitles.srt', 'w', encoding='utf-8') as f:
                f.writelines(translated_subtitles)

            self.outputTextEdit.insert(tk.END, f'Translated subtitles to {targetLanguage} and saved as translated_subtitles.srt\n')

    def addSubtitlesToVideo(self):
        file_extension = self.fileName.split('.')[-1]
        output_video = f'output.{file_extension}'

        subprocess.run([
            r'C:\ffmpeg\bin\ffmpeg',
            '-i', self.fileName,
            '-i', 'translated_subtitles.srt',
            '-c', 'copy',
            '-scodec', 'srt',
            '-metadata:s:s:1', f'title={self.subtitle_language}',
            '-disposition:s:1', 'default',
            '-map', '0',
            '-map', '1',
            '-y', output_video
        ])

        self.outputTextEdit.insert(tk.END, f'Added translated subtitles to video and saved as {output_video}\n')


def main():
    root = tk.Tk()
    app = SubtitleTranslator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
