from Observer import Subject, Observer
from mutagen.easyid3 import EasyID3
import pygame
from tkinter.filedialog import *
from tkinter import *
import logging

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
        except:
            logging.exception("Loading songs into playlist failed")

    def pause_or_unpause_song(self):
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
                pausing = False
            elif not self.is_paused:
                pygame.mixer.music.pause()
                pausing = True
        except:
            logging.exception("Pausing/unpausing functionality failed")

    def song_data_for_text(self, key, item):
        try:
            song = EasyID3(item)
            song_data = f"{str(key + 1)} : {song['title'][0]} - {song['artist'][0]}"
            return song_data
        except:
            logging.exception("Creation of song data for text failed")
            
    def song_data_for_label(self):
        try:
            song = EasyID3(self.play_list[self.current_song])
            song_data = f"Now playing: Nr: {str(self.play_list + 1)} \ {str(song['title'])} - {str(song['artist'])}"
            return song_data
        except:
            logging.exception("Creation of song data for label failed")
    
    def load_and_play_song(self):
        try:
            directory = self.play_list[self.current_song_index]
            pygame.mixer.music.load(directory)
            pygame.mixer.music.play(1, 0.0)
            pygame.mixer.music.set_endevent(self.SONG_END)
            self.is_paused = False
            self.notify_observers()
        except:
            logging.exception("Loading and playing song failed")

    def check_music(self):
        try:
            for event in pygame.event.get():
                if event.type == self.SONG_END:
                    self.next_song()
        except:
            logging.exception("Checking music failed")

    def change_song(self, direction):
        try: 
            self.current_song_index = (self.current_song_index + direction) % len(self.play_list)
            self.load_and_play_song()
        except:
            logging.exception("Changing song failed")

    def next_song(self):
        try: 
            self.change_song(1)
        except:
            logging.exception("Loading next song failed")

    def previous_song(self):
        try: 
            self.change_song(-1)
        except:
            logging.exception("Loading previous song failed")


