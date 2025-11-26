import asyncio
import pygame

async def initWindow(title, width, height, fullscreen, fps_limit, piano=None):
    print("Activating main_window.py component")
    pygame.init()
    print("Pygame is succesfully init")

    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption(title)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    isRunning = True

    while isRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
                print("Program is closed")
            elif event.type == pygame.KEYDOWN and piano:
                try:
                    piano.handle_key(event.key)
                except Exception as e:
                    print(f"Error handling key event: {e}")

        # Czyszczenie ekranu
        screen.fill((30, 30, 30))

        # Wyświetlanie stanu metronomu, BPM, metrum, pitch shift
        if piano:
            info_texts = [
                f"Metronome: {'ON' if piano.isMetronome else 'OFF'}",
                f"BPM: {piano.currentbpm}",
                f"Metrum: {piano.beats_per_bar}/4",
                f"Pitch shift: {piano.currentShiftSemitones} semitones"
            ]
            for i, text in enumerate(info_texts):
                label = font.render(text, True, (255, 255, 255))
                screen.blit(label, (10, 10 + i * 30))

        # Rysowanie prostych "klawiszy" pianina
        key_order = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t,
                     pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p,
                     pygame.K_a, pygame.K_s]
        key_labels = ['Q','W','E','R','T','Y','U','I','O','P','A','S']
        key_width = width // len(key_order)
        for i, key in enumerate(key_order):
            rect = pygame.Rect(i*key_width, height-120, key_width-2, 100)
            pygame.draw.rect(screen, (200, 200, 200), rect)
            # jeśli klawisz jest wciśnięty, zmieniamy kolor
            pressed = pygame.key.get_pressed()
            if pressed[key]:
                pygame.draw.rect(screen, (255, 100, 100), rect)
            label = font.render(key_labels[i], True, (0,0,0))
            screen.blit(label, (i*key_width + key_width//4, height-90))

        pygame.display.flip()
        clock.tick(fps_limit)
        await asyncio.sleep(0)
