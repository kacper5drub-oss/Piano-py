import asyncio
import os
import pygame
import numpy as np

class Piano:
    currentShiftSemitones = 0
    minShift = -36
    maxShift = 36

    currentbpm = 120
    maxBpm = 999
    minBpm = 10

    beats_per_bar = 4
    beat_counter = 0

    metronome_volume = 1.0
    accent_volume = 1.8

    isMetronome = False

    def __init__(self, sounds, arrays, samplerate):
        self.sounds = sounds
        self.arrays = arrays
        self.samplerate = samplerate
        self.cache = {}

        base = os.path.dirname(__file__)
        metro_path = os.path.join(base, '..', 'sounds', 'Metronome.mp3')
        self.metronome_sound = pygame.mixer.Sound(metro_path)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.set_num_channels(16)
        self.metro_channel = pygame.mixer.Channel(10)

    def change_semitone(self, delta):
        ns = max(self.minShift, min(self.maxShift, self.currentShiftSemitones + delta))
        self.currentShiftSemitones = ns

    def _get_sound_for_shift(self, keycode, semitones):
        if semitones == 0:
            return self.sounds.get(keycode)
        key = (keycode, semitones)
        if key in self.cache:
            return self.cache[key]
        arr = self.arrays.get(keycode)
        if arr is None:
            return self.sounds.get(keycode)
        factor = 2 ** (semitones / 12.0)
        n = arr.shape[0]
        new_n = max(1, int(n / factor))
        old = np.arange(n)
        new = np.linspace(0, n - 1, new_n)
        if arr.ndim == 1:
            out = np.interp(new, old, arr).astype(arr.dtype)
        else:
            out = np.stack([np.interp(new, old, arr[:, i]) for i in range(arr.shape[1])], axis=1).astype(arr.dtype)
        try:
            snd = pygame.sndarray.make_sound(out)
            self.cache[key] = snd
            return snd
        except:
            return self.sounds.get(keycode)

    async def metronome_loop(self):
        while self.isMetronome:
            interval = 60.0 / self.currentbpm
            if self.beat_counter == 0:
                self.metronome_sound.set_volume(self.accent_volume)
            else:
                self.metronome_sound.set_volume(self.metronome_volume)

            self.metro_channel.play(self.metronome_sound)
            self.beat_counter = (self.beat_counter + 1) % self.beats_per_bar
            await asyncio.sleep(interval)

    def handle_key(self, keycode):
        if keycode == pygame.K_LEFTBRACKET:
            self.change_semitone(-1)
            return
        if keycode == pygame.K_RIGHTBRACKET:
            self.change_semitone(1)
            return

        if keycode in (pygame.K_4, pygame.K_5, pygame.K_6):
            old = self.beats_per_bar
            if keycode == pygame.K_4: self.beats_per_bar = 4
            if keycode == pygame.K_5: self.beats_per_bar = 3
            if keycode == pygame.K_6: self.beats_per_bar = 6
            self.beat_counter = 0
            print(f"Metrum changed from {old} to {self.beats_per_bar} per bar")
            return

        snd = self._get_sound_for_shift(keycode, self.currentShiftSemitones)
        if snd:
            try:
                snd.play()
            except:
                pass

        if keycode == pygame.K_1:
            if self.isMetronome:
                self.isMetronome = False
                print("Metronome stopped")
            else:
                self.isMetronome = True
                try:
                    loop = asyncio.get_running_loop()
                except:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                loop.create_task(self.metronome_loop())
                print("Metronome started")
            return

        if keycode == pygame.K_2:
            old = self.currentbpm
            self.currentbpm = min(self.maxBpm, self.currentbpm + 1)
            print(f"BPM changed from {old} to {self.currentbpm}")
            return

        if keycode == pygame.K_3:
            old = self.currentbpm
            self.currentbpm = max(self.minBpm, self.currentbpm - 1)
            print(f"BPM changed from {old} to {self.currentbpm}")
            return

def initPianoApp():
    base = os.path.dirname(__file__)
    sounds_dir = os.path.join(base, '..', 'sounds')

    mapping = {
        pygame.K_q:'key01.mp3', pygame.K_w:'key02.mp3', pygame.K_e:'key03.mp3',
        pygame.K_r:'key04.mp3', pygame.K_t:'key05.mp3', pygame.K_y:'key06.mp3',
        pygame.K_u:'key07.mp3', pygame.K_i:'key08.mp3', pygame.K_o:'key09.mp3',
        pygame.K_p:'key10.mp3', pygame.K_a:'key11.mp3', pygame.K_s:'key12.mp3'
    }

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    sr = pygame.mixer.get_init()[0]

    sounds={}
    arrays={}

    for k,f in mapping.items():
        p=os.path.join(sounds_dir,f)
        if not os.path.exists(p):
            continue
        try:
            snd = pygame.mixer.Sound(p)
            sounds[k]=snd
            try:
                arrays[k]=pygame.sndarray.array(snd)
            except:
                arrays[k]=None
        except:
            pass

    return Piano(sounds, arrays, sr)
