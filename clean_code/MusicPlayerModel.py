import logging
import tkinter as tk
from tkinter import filedialog

from mutagen.easyid3 import EasyID3
import pygame

from Observer import Subject

class MusicPlayerModel(Subject):
    def __init__(self):
        super().__init__()

        self.current_song = ""
        self.play_list = []
        self.current_song_index = 0
        self.is_paused = True
        self.SONG_END = pygame.USEREVENT + 1

    def load_songs_into_playlist(self):
        try:
            directory = askopenfilenames()

            for song_dir in directory:
                logging.debug("Song directory being loaded: " + song_dir)
                self.play_list.append(song_dir)
            self.notify_observers()
        except Exception as e:
            logging.exception(f"Loading songs into playlist failed: {e}")

    def pause_or_unpause_song(self):
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
                pausing = False
            else:
                pygame.mixer.music.pause()
                pausing = True
        except Exception as e:
            logging.exception(f"Pausing/unpausing functionality failed: {e}")

    def song_data_for_text(self, key, item):
        try:
            song = EasyID3(item)
            song_data = f"{str(key + 1)} : {song['title'][0]} - {song['artist'][0]}"
            return song_data
        except Exception as e:
            logging.exception(f"Creation of song data for text failed: {e}")
            
    def song_data_for_label(self):
        try:
            song = EasyID3(self.play_list[self.current_song])
            song_data = f"Now playing: Nr: {str(self.play_list + 1)} \ {str(song['title'])} - {str(song['artist'])}"
            return song_data
        except Exception as e:
            logging.exception(f"Creation of song data for label failed: {e}")
    
    def load_and_play_song(self):
        try:
            directory = self.play_list[self.current_song_index]
            pygame.mixer.music.load(directory)
            pygame.mixer.music.play(1, 0.0)
            pygame.mixer.music.set_endevent(self.SONG_END)
            self.is_paused = False
            self.notify_observers()
        except Exception as e:
            logging.exception(f"Loading and playing song failed: {e}")

    def check_music(self):
        try:
            for event in pygame.event.get():
                if event.type == self.SONG_END:
                    self.next_song()
        except Exception as e:
            logging.exception(f"Checking music failed: {e}")

    def change_song(self, direction: int):
        try: 
            self.current_song_index = (self.current_song_index + direction) % len(self.play_list)
            self.load_and_play_song()
        except Exception as e:
            logging.exception(f"Changing song failed: {e}")

    def next_song(self):
        try: 
            self.change_song(1)
        except Exception as e:
            logging.exception(f"Loading next song failed: {e}")

    def previous_song(self):
        try: 
            self.change_song(-1)
        except Exception as e:
            logging.exception(f"Loading previous song failed: {e}")

