from tkinter import *

import pygame

import MusicPlayerModel
import MusicPlayerView

pygame.init()

window = Tk()
window.geometry("500x500")
window.title("MP3 Music Player")
model = MusicPlayerModel()
app = MusicPlayerView(window, model)

while True:
    model.check_music()
    app.update()