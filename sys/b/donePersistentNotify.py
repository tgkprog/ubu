#!/usr/bin/env python3
"""
Persistent notification window with periodic sound alerts.
Starts minimized, plays sound periodically, can be opened to view message and exit.

Usage:
    donePersistentNotify.py [message] [interval_seconds] [sound_file]
    
Args:
    message: Text to display (default: "Done")
    interval_seconds: Seconds between sound plays (default: 200, range: 0-9999)
    sound_file: Path to audio file (default: /home/ubuntu/audio/bldDone.wav)
"""

import sys
import tkinter as tk
from tkinter import font
import subprocess
import threading
import time

def play_sound(sound_file):
    """Play sound file using aplay (non-blocking)"""
    try:
        subprocess.Popen(['aplay', '-q', sound_file], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error playing sound: {e}", file=sys.stderr)

def parse_interval(value):
    """Parse interval parameter with validation"""
    try:
        interval = int(value)
        if interval < 0 or interval > 9999:
            return 200
        return interval
    except (ValueError, TypeError):
        return 200

class PersistentNotifyWindow:
    def __init__(self, message, interval, sound_file):
        self.message = message
        self.interval = interval
        self.sound_file = sound_file
        self.running = True
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Notification")
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        
        # Withdraw window immediately to prevent flashing
        self.root.withdraw()
        
        # Center window on screen (while withdrawn)
        self.center_window()
        
        # Configure colors
        bg_color = "#2c3e50"
        fg_color = "#ecf0f1"
        btn_color = "#e74c3c"
        btn_hover = "#c0392b"
        
        self.root.configure(bg=bg_color)
        
        # Create message label
        message_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.label = tk.Label(
            self.root,
            text=self.message,
            font=message_font,
            bg=bg_color,
            fg=fg_color,
            wraplength=450,
            justify="center"
        )
        self.label.pack(expand=True, pady=20)
        
        # Create info label
        info_font = font.Font(family="Helvetica", size=10)
        info_text = f"Sound playing every {self.interval}s"
        self.info_label = tk.Label(
            self.root,
            text=info_text,
            font=info_font,
            bg=bg_color,
            fg="#95a5a6"
        )
        self.info_label.pack(pady=5)
        
        # Create exit button
        btn_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.exit_btn = tk.Button(
            self.root,
            text="EXIT",
            font=btn_font,
            bg=btn_color,
            fg="white",
            activebackground=btn_hover,
            activeforeground="white",
            command=self.exit_app,
            cursor="hand2",
            relief="flat",
            padx=30,
            pady=10
        )
        self.exit_btn.pack(pady=20)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
        # Start sound thread BEFORE minimizing
        self.sound_thread = threading.Thread(target=self.sound_loop, daemon=True)
        self.sound_thread.start()
        
        # Play sound immediately on start
        play_sound(self.sound_file)
        
        # Keep window withdrawn and iconified (already done in __init__)
        self.root.iconify()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def restore_window(self):
        """Restore window from minimized state"""
        self.root.deiconify()  # Restore from iconified state
    
    def sound_loop(self):
        """Background thread to play sound periodically"""
        next_play = time.time() + self.interval
        
        while self.running:
            current_time = time.time()
            
            if current_time >= next_play:
                play_sound(self.sound_file)
                next_play = current_time + self.interval
            
            # Sleep in small increments to allow quick exit
            time.sleep(0.5)
    
    def exit_app(self):
        """Exit application"""
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the GUI event loop"""
        self.root.mainloop()

def main():
    # Parse command line arguments
    message = sys.argv[1] if len(sys.argv) > 1 else "Done"
    interval = parse_interval(sys.argv[2]) if len(sys.argv) > 2 else 200
    sound_file = sys.argv[3] if len(sys.argv) > 3 else '/home/ubuntu/audio/bldDone.wav'
    
    # Create and run notification window
    app = PersistentNotifyWindow(message, interval, sound_file)
    app.run()

if __name__ == "__main__":
    main()
