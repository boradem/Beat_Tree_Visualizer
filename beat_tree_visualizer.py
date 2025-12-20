import librosa
import numpy as np
import warnings
import sys
import os
import re
import tempfile
import subprocess
import time
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

# Let's silence those annoying deprecation warnings from Pygame so our console stays clean.
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources.*')

import pygame

# --- Constants ---
WIDTH = 1200
HEIGHT = 800
FPS = 60

@dataclass
class Theme:
    name: str
    background: Tuple[int, int, int]
    branch_color_base: Tuple[int, int, int]
    leaf_color: Tuple[int, int, int]
    pulse_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]

THEMES = [
    Theme(
        name="Nature",
        background=(10, 15, 20),
        branch_color_base=(100, 200, 100),
        leaf_color=(50, 255, 50),
        pulse_color=(100, 255, 100),
        text_color=(255, 255, 255)
    ),
    Theme(
        name="Fire",
        background=(20, 5, 5),
        branch_color_base=(255, 100, 50),
        leaf_color=(255, 200, 50),
        pulse_color=(255, 50, 0),
        text_color=(255, 200, 200)
    ),
    Theme(
        name="Neon",
        background=(5, 5, 20),
        branch_color_base=(50, 100, 255),
        leaf_color=(255, 50, 255),
        pulse_color=(0, 255, 255),
        text_color=(200, 200, 255)
    )
]

class AudioAnalyzer:
    def __init__(self, audio_path: str):
        self.audio_path = audio_path
        print(f"Loading up the track: {audio_path}")
        self.y, self.sr = librosa.load(audio_path, sr=None)
        
        print("Listening to the rhythm to find the beats...")
        self.tempo, self.beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        self.beat_times = librosa.frames_to_time(self.beats, sr=self.sr)
        
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        
        # We need to make sure the tempo is a simple number we can use.
        if isinstance(self.tempo, np.ndarray):
            self.bpm = float(self.tempo.item())
        elif isinstance(self.tempo, (list, tuple)):
            self.bpm = float(self.tempo[0])
        else:
            self.bpm = float(self.tempo)
            
        print(f"BPM: {self.bpm:.2f}, Duration: {self.duration:.2f}s")

    def get_intensity(self, current_time: float, window_ms: int = 50) -> float:
        """Figure out how loud or intense the music is at this exact moment."""
        sample_index = int(current_time * self.sr)
        if sample_index >= len(self.y):
            return 0.0
            
        window_size = int((window_ms / 1000) * self.sr)
        end_index = min(sample_index + window_size, len(self.y))
        segment = self.y[sample_index:end_index]
        
        if len(segment) > 0:
            rms = np.sqrt(np.mean(segment ** 2))
            return min(1.0, rms * 15) # Normalize and boost
        return 0.0

class Player:
    def __init__(self, audio_path: str):
        self.audio_path = audio_path
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load(self.audio_path)
        self.playing = False
        self.paused = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        
        # Keep track of where we are in time.
        self.start_time = 0
        self.pause_start_time = 0
        self.total_pause_duration = 0
        self.offset = 0 # For seeking

    def play(self):
        if not self.playing:
            pygame.mixer.music.play(start=self.offset)
            self.start_time = time.time() - self.offset
            self.playing = True
            self.paused = False
        elif self.paused:
            pygame.mixer.music.unpause()
            self.total_pause_duration += time.time() - self.pause_start_time
            self.paused = False

    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.pause_start_time = time.time()
            self.paused = True

    def toggle(self):
        if self.paused or not self.playing:
            self.play()
        else:
            self.pause()

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.offset = 0
        self.total_pause_duration = 0

    def seek(self, time_pos: float):
        """Jump to a specific moment in the song."""
        if time_pos < 0: time_pos = 0
        self.offset = time_pos
        pygame.mixer.music.play(start=self.offset)
        self.start_time = time.time() - self.offset
        self.total_pause_duration = 0
        self.playing = True
        self.paused = False

    def get_time(self) -> float:
        if not self.playing:
            return self.offset
        if self.paused:
            return self.pause_start_time - self.start_time - self.total_pause_duration
        return time.time() - self.start_time - self.total_pause_duration

    def change_volume(self, delta: float):
        self.volume = max(0.0, min(1.0, self.volume + delta))
        pygame.mixer.music.set_volume(self.volume)

class Visualizer:
    def __init__(self, screen: pygame.Surface, analyzer: AudioAnalyzer):
        self.screen = screen
        self.analyzer = analyzer
        self.width, self.height = screen.get_size()
        self.theme_index = 0
        self.theme = THEMES[self.theme_index]
        
        # Variables to control the pulsing animation.
        self.beat_pulse = 0.0
        self.smoothed_intensity = 0.0
        self.last_beat_index = -1
        
        # Leaf Growth State
        self.target_leaf_count = int(self.analyzer.bpm)
        self.current_leaf_count = self.target_leaf_count # Start with a full tree
        self.max_possible_leaves = 512 # Lots of potential leaves for a rich tree
        
        # Theme State
        self.auto_theme = True
        
        # Tree params
        self.tree_center_x = self.width // 2
        self.tree_base_y = self.height - 20 # Lower base
        self.branch_length = 130 # Larger tree
        self.max_depth = 8 # More detail
        
        # Background Gradient
        self._create_background_gradient()

    def _create_background_gradient(self):
        self.bg_surface = pygame.Surface((self.width, self.height))
        # Radial gradient simulation
        center = (self.width // 2, self.height // 2)
        max_dist = np.sqrt(center[0]**2 + center[1]**2)
        
        # We'll draw a vignette to focus attention on the center.
        # It's a simple way to add some mood to the background.
        self.vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Create a radial gradient from transparent to black
        for r in range(int(max_dist), 0, -2):
            alpha = int(255 * (r / max_dist)**2) # Quadratic falloff
            if alpha > 255: alpha = 255
            pygame.draw.circle(self.vignette, (0, 0, 0, min(100, alpha)), center, r)

    def next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.theme = THEMES[self.theme_index]
        
    def toggle_auto_theme(self):
        self.auto_theme = not self.auto_theme

    def update(self, current_time: float):
        # Check how intense the music is right now.
        target_intensity = self.analyzer.get_intensity(current_time)
        self.smoothed_intensity += (target_intensity - self.smoothed_intensity) * 0.2
        
        # Check if we hit a beat.
        beat_indices = np.where(self.analyzer.beat_times <= current_time)[0]
        if len(beat_indices) > 0:
            current_beat_index = beat_indices[-1]
            if current_beat_index > self.last_beat_index:
                self.beat_pulse = 1.0
                self.last_beat_index = current_beat_index
                
                # If auto-theme is on, switch things up on the beat.
                if self.auto_theme:
                    self.next_theme()
        
        # Fade the pulse effect out smoothly.
        self.beat_pulse *= 0.9

    def _get_branch_random(self, branch_id: int) -> float:
        """Generate a consistent random number for a specific branch so it always looks the same."""
        # Simple hash function
        x = branch_id * 123456789 + 987654321
        x ^= (x << 13)
        x ^= (x >> 17)
        x ^= (x << 5)
        return (x & 0xFFFFFFFF) / 0xFFFFFFFF

    def draw_branch(self, x, y, angle, length, depth, intensity, branch_id: int = 1):
        if depth == 0: return

        # Make the tree breathe with the music.
        # Instead of swaying randomly, it expands and contracts based on volume.
        # Base spread is 25 degrees. Intensity adds up to 20 degrees.
        spread = 25 + 20 * intensity + 5 * self.beat_pulse
        
        # Calculate end point
        rad = np.radians(angle)
        x2 = x + length * np.cos(rad)
        y2 = y - length * np.sin(rad)
        
        # Color interpolation
        base_color = self.theme.branch_color_base
        r = min(255, base_color[0] + int(50 * intensity))
        g = min(255, base_color[1] + int(50 * intensity))
        b = min(255, base_color[2] + int(50 * intensity))
        color = (r, g, b)
        
        thickness = max(1, int(depth * 1.2))
        pygame.draw.line(self.screen, color, (x, y), (x2, y2), thickness)
        
        # Deciding if we should add a leaf here.
        if depth <= 5: 
            # Deterministic check
            activation_val = self._get_branch_random(branch_id + 999) 
            
            if activation_val < (self.current_leaf_count / self.max_possible_leaves):
                # Base size
                leaf_size = int(5 * intensity + 3)
                
                # Pulse effect on size
                leaf_size += int(self.beat_pulse * 10) 
                
                # Pulse effect on color (brighten)
                l_color = list(self.theme.leaf_color)
                brighten = int(100 * self.beat_pulse)
                l_color = (
                    min(255, l_color[0] + brighten),
                    min(255, l_color[1] + brighten),
                    min(255, l_color[2] + brighten)
                )
                
                # Draw leaf with glow
                if self.beat_pulse > 0.2:
                    glow_size = leaf_size + 4
                    glow_color = (*l_color, 100)
                    s = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, glow_color, (glow_size, glow_size), glow_size)
                    self.screen.blit(s, (int(x2)-glow_size, int(y2)-glow_size), special_flags=pygame.BLEND_ADD)

                pygame.draw.circle(self.screen, l_color, (int(x2), int(y2)), leaf_size)

        # Time to branch out!
        # reduce the branch length each time we go deeper.
        new_length = length * 0.7
        
        self.draw_branch(x2, y2, angle - spread, new_length, depth - 1, intensity, branch_id * 2)
        self.draw_branch(x2, y2, angle + spread, new_length, depth - 1, intensity, branch_id * 2 + 1)

    def draw(self, current_time: float):
        self.screen.fill(self.theme.background)
        
        # Draw the vignette overlay for atmosphere.
        self.screen.blit(self.vignette, (0,0))
        
        # Draw Tree
        combined_intensity = min(1.0, self.smoothed_intensity + self.beat_pulse * 0.3)
        self.draw_branch(self.tree_center_x, self.tree_base_y, 90, self.branch_length, self.max_depth, combined_intensity)

        # Draw UI
        self.draw_ui(current_time)

    def draw_ui(self, current_time: float):
        font = pygame.font.Font(None, 24)
        
        # Display the stats: Time, Leaf count, and Theme mode.
        time_str = f"{int(current_time // 60)}:{int(current_time % 60):02d} / {int(self.analyzer.duration // 60)}:{int(self.analyzer.duration % 60):02d}"
        leaf_str = f"Leaves: {self.current_leaf_count}/{self.target_leaf_count}"
        theme_str = f"Auto Theme: {'ON' if self.auto_theme else 'OFF'}"
        
        text = font.render(f"{time_str} | {leaf_str} | {theme_str}", True, self.theme.text_color)
        self.screen.blit(text, (10, 10))

        
        # Progress Bar
        bar_width = self.width - 40
        bar_height = 5
        progress = current_time / self.analyzer.duration if self.analyzer.duration > 0 else 0
        pygame.draw.rect(self.screen, (50, 50, 50), (20, 40, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.theme.text_color, (20, 40, int(bar_width * progress), bar_height))
        
        # Controls Help
        controls = [
            "SPACE: Play/Pause",
            "ARROWS: Seek / Volume",
            "T: Change Theme",
            "D: Toggle Auto Theme",
            "ESC: Quit"
        ]
        for i, ctrl in enumerate(controls):
            t = font.render(ctrl, True, (150, 150, 150))
            self.screen.blit(t, (10, self.height - 100 + i * 20))

class App:
    def __init__(self, audio_path: str):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Beat Tree Visualizer")
        self.clock = pygame.time.Clock()
        
        self.analyzer = AudioAnalyzer(audio_path)
        self.player = Player(audio_path)
        self.visualizer = Visualizer(self.screen, self.analyzer)
        
        self.running = True

    def run(self):
        self.player.play()
        
        while self.running:
            current_time = self.player.get_time()
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.player.toggle()
                    elif event.key == pygame.K_RIGHT:
                        self.player.seek(current_time + 5)
                    elif event.key == pygame.K_LEFT:
                        self.player.seek(current_time - 5)
                    elif event.key == pygame.K_UP:
                        self.player.change_volume(0.1)
                    elif event.key == pygame.K_DOWN:
                        self.player.change_volume(-0.1)
                    elif event.key == pygame.K_t:
                        self.visualizer.next_theme()
                    elif event.key == pygame.K_d:
                        self.visualizer.toggle_auto_theme()

            # Update & Draw
            self.visualizer.update(current_time)
            self.visualizer.draw(current_time)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
            # Check if song ended
            if current_time > self.analyzer.duration:
                self.running = False

        self.player.stop()
        pygame.quit()

# --- Helper Functions for Downloading ---
def is_url(path: str) -> bool:
    return path.startswith(('http://', 'https://'))

def download_audio(url: str) -> Optional[str]:
    print(f"Downloading from {url}...")
    temp_dir = tempfile.mkdtemp()
    
    try:
        import yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            return filename
    except ImportError:
        print("Error: yt-dlp not found. Please install it: pip install yt-dlp")
    except Exception as e:
        print(f"Download error: {e}")
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python beat_tree_visualizer.py <file_or_url>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    audio_path = input_path
    
    if is_url(input_path):
        downloaded = download_audio(input_path)
        if not downloaded:
            sys.exit(1)
        audio_path = downloaded
    elif not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        sys.exit(1)
        
    try:
        app = App(audio_path)
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup temp files if we downloaded
        if is_url(input_path) and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                os.rmdir(os.path.dirname(audio_path))
            except:
                pass

if __name__ == "__main__":
    main()
