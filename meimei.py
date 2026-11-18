from pathlib import Path 
import tkinter as tk
import math 
import random 

from PIL import (Image, ImageDraw, ImageFont, ImageSequence, ImageTk, ImageEnhance)

ROOT = Path(__file__).resolve().parent 
GIF_PATH = ROOT / 'meimei-snow-leopard-meimei.gif'
COLS, ROWS = 100, 60 
CELL_W, CELL_H = 10, 12 
BG = (9, 12, 22)
CHARS = '@%#*+=-:. '

EXPLOSION_FRAMES = 20 
EXPLOSION_DELAY = 55 
STATIC_HOLD = 1800

def find_font(): 
    candidates = [
        '/System/Library/Fonts/Menlo.ttc', '/System/Library/Fonts/Monaco.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 
        'C:/Windows/Fonts/consola.ttf'
    ]
    for candidate in candidates: 
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, 12)
    return ImageFont.load_default()

def get_ascii_data(original): 
    source = original.convert('RGB')
    source = source.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    source = ImageEnhance.Brightness(source).enhance(1.25)
    source = ImageEnhance.Contrast(source).enhance(1.3)
    source = ImageEnhance.Color(source).enhance(1.25)

    pixels = source.load()
    ascii_data = []
    for y in range(ROWS): 
        for x in range(COLS): 
            r,g,b = pixels[x,y]
            brightness = (0.2126 * r + 0.7152 * g + 0.0722 * b)/255
            index = min(len(CHARS)-1, int((1-brightness) * len(CHARS)))
            symbol = CHARS[index]
            ascii_data.append((x, y, symbol, (r,g,b)))
    return ascii_data

def draw_ascii_frame(ascii_data, font): 
    picture = Image.new('RGB', (COLS * CELL_W, ROWS * CELL_H), BG)
    draw = ImageDraw.Draw(picture)
    for x, y, symbol, colour in ascii_data: 
        draw.text((x * CELL_W, y * CELL_H), symbol, font=font, fill=colour) 
    return picture 

def make_explosion(ascii_data, font): 
    rng = random.Random(42)
    centre_x = COLS * 0.53 
    centre_y = ROWS * 0.55 
    particles = []

    for x,y, symbol, colour in ascii_data: 
            if symbol ==' ': 
                continue 
            if rng.random() < 0.20: 
                continue 
            dx = x - centre_x 
            dy = y - centre_y 
            distance = math.hypot(dx, dy)
            if distance == 0: 
                distance = 1
            speed = rng.uniform(1.5, 5.0)
            vx = dx/distance * speed 
            vy = dy/distance * speed 
            vx += rng.uniform(-1.0, 1.0)
            vy += rng.uniform(-1.0, 1.0)
            particles.append((x, y, symbol, colour, vx, vy))
    explosion_images = []

    for frame_number in range(EXPLOSION_FRAMES): 
        picture = Image.new('RGB', (COLS * CELL_W, ROWS * CELL_H), BG)
        draw = ImageDraw.Draw(picture)
        progress = frame_number/(EXPLOSION_FRAMES -1)
        FADE = (1-progress) ** 1.5 
        for x,y, symbol, colour, vx, vy in particles: 
            new_x = x + vx * progress * 18 
            new_y = y + vy * progress * 18 
            new_y += 6 * progress ** 2 
            faded_colour = tuple(
                int(BG[i] + (colour[i] - BG[i]) * FADE)
            for i in range(3)
            )
        if (
            0 <= new_x < COLS and 0 <= new_y < ROWS): 
            draw.text(
                (new_x * CELL_W, new_y * CELL_H), 
                symbol, 
                font=font, 
                fill=faded_colour)
        explosion_images.append(picture)
    return explosion_images

def make_fire(ascii_data, font): 
    fire_frames = []
    rng = random.Random(25)

    for frame_number in range(12): 
        picture = Image.new(
            'RGB', 
            (COLS * CELL_W, ROWS * CELL_H), 
            BG
        )
        draw = ImageDraw.Draw(picture)
        progress = frame_number/11

        for x,y, symbol, colour in ascii_data: 
            if symbol == ' ' :
                continue 
            
            r, g, b = colour 

            fire_colour = (
                min(255, int(r + 130 * progress)), 
                min(255, int(g * (1-0.25 * progress) + 45 * progress)), 
                max(0, int(b * (1 - 0.85 * progress)))
            )

            draw.text(
                (x * CELL_W, y * CELL_H), 
                symbol, 
                font=font, 
                fill=fire_colour
            )

        if progress > 0.3:
            for _ in range(int(90 * progress)): 
                sx = rng.randrange(COLS * CELL_W)
                sy = rng.randrange(ROWS * CELL_H)
                draw.text(
                    (sx,sy), 
                    rng.choice('*+.'), 
                    font=font, 
                    fill=rng.choice([
                        (255, 70, 10), 
                        (255, 210, 60)
                    ])
                )
        fire_frames.append(picture)

    return fire_frames
def make_meme_explosion(ascii_data, font):
    rng = random.Random(42)
    pictures = []

    bowl = []
    cat = []
    background = []

    for x, y, symbol, colour in ascii_data: 
        if symbol == ' ': 
            continue 
        if 0.47 < x / COLS < 0.74 and y / ROWS > 0.73: 
            bowl.append((x, y, symbol, colour))
        elif 0.42 < x / COLS < 0.70 and 0.27 < y / ROWS < 0.87: 
            cat.append((x, y, symbol, colour))
        else: 
            background.append((x, y, symbol, colour))
    debris = []
        
    for x, y, symbol, colour in background: 
        angle = math.atan2(y - ROWS * 0.5, x - COLS * 0.53)
        speed = rng.uniform(5, 24)

        debris.append(( 
            x, y, symbol, colour, 
            math.cos(angle) * speed, 
            math.sin(angle) * speed
        ))

    for frame_number in range(36): 
        progress = frame_number/35

        picture = Image.new(
            'RGB', 
            (COLS * CELL_W, ROWS * CELL_H), 
            BG
        )
        draw = ImageDraw.Draw(picture)
        blast = max(0, (progress - 0.16) / 0.84)
        for x, y, symbol, colour, vx, vy in debris: 
            if blast > 0: 
                new_x = x + vx * blast 
                new_y = y + vy * blast 

                colour = (
                    min(255, int(colour[0] + 150 * blast)), 
                    min(255, int(colour[1] + 50 * blast)), 
                    max (0, int(colour[2] * (1-blast)))
                )
            else: 
                new_x, new_y = x, y
            if 0 <= new_x < COLS and 0 <= new_y < ROWS: 
                draw.text(
                    (new_x * CELL_W, new_y * CELL_H), 
                    symbol, font=font, fill=colour
                    )
            if blast > 0: 
                for _ in range(int(350 * (1 - blast * 0.7))): 
                    sx = rng.uniform(COLS * 0.20, COLS * 0.85)
                    sy = rng.uniform(ROWS * 0.15, ROWS * 0.90)
                    sx += rng.uniform(-20, 20) * blast
                    sy -= rng.uniform(0, 25) * blast 

                    if 0 <= sx < COLS and 0 <= sy < ROWS: 
                        draw.text(
                            (sx * CELL_W, sy * CELL_H), 
                            rng.choice('@#*+.'), 
                            font=font, 
                            fill=rng.choice([
                                (255, 60, 10), 
                                (255, 130, 20), 
                                (255, 210, 50)
                            ])
                        )
            shake = 0 
            if blast > 0: 
                shake = rng.uniform(-2.5, 2.5) * (1 - blast)
            for x, y, symbol, colour in cat: 
                draw.text(
                    ((x + shake) * CELL_W, y * CELL_H), 
                    symbol, font=font, fill=colour
                )
            throw = min(1, progress / 0.48)
            bowl_x = -40 * throw 
            bowl_y = -38 * math.sin(throw * math.pi / 2)
            for x, y, symbol, colour in bowl: 
                new_x = x + bowl_x 
                new_y = y + bowl_y 

                if 0 <= new_x < COLS and 0 <= new_y < ROWS: 
                    draw.text(
                        (new_x * CELL_W, new_y * CELL_H), 
                        symbol, font=font, fill=colour
                    )
            pictures.append(picture)
    return pictures 

def main(): 
    if not GIF_PATH.exists(): 
        raise SystemExit(
            'GIF not found! Put the GIF in the same folder as this python script.'
            ) 
    window = tk.Tk()
    window.title('MEIMEI FOREVER!')
    window.configure(bg='#090c16')
    window.geometry('1100x950')
    window.resizable(True, True)

    header = tk.Label(
        window, text='MEIMEI',
        font=('Menlo', 22, 'bold'), 
        fg='#a7ff82', 
        bg='#090c16'
    )
    header.pack(pady=(15,10))
    label = tk.Label(
        window, bg='#090c16', bd=0
    )
    label.pack(padx=12)

    footer = tk.Label(
        window, text='Space = Pause/Play R = Restart', 
        font=('Menlo', 11), fg='#adb5c6', bg='#090c16'
    )

    footer.pack(pady=(10,15))
    font = find_font()
    gif = Image.open(GIF_PATH)
    frames = []
    durations = []
    ascii_frames = []

    for frame in ImageSequence.Iterator(gif): 
        ascii_data = get_ascii_data(frame.copy())
        ascii_frames.append(ascii_data)
        ascii_image = draw_ascii_frame(ascii_data, font)
        frames.append(
            ImageTk.PhotoImage(ascii_image, master=window)
        )

        durations.append(
            max(40, frame.info.get('duration', 100))
        )

    if not frames: 
        raise SystemExit('No GIF frames found')
    meme_pictures = make_meme_explosion(
        ascii_frames[-1], font
    )

    meme_frames = [
        ImageTk.PhotoImage(picture, master=window)
        for picture in meme_pictures
    ]

    all_frames = frames + meme_frames
    if len(frames) == 1: 
        durations[0] = STATIC_HOLD

    all_durations = (
        durations + [45] * len(meme_frames)
    )

    state = {'index': 0, 'paused': False}
    def toggle_pause(event=None): 
        state['paused']=not state['paused']
    def restart(event=None): 
        state['index'] = 0 
        state['paused'] = False 

    window.bind('<space>', toggle_pause)
    window.bind('r', restart)

    def tick(): 
        if not state['paused']: 
            index = state['index']
            label.configure(image=all_frames[index])
            delay = all_durations[index]
            state['index']=(index + 1) %len(all_frames)
        else: 
            delay = 80
        window.after(delay, tick)
    tick()
    window.mainloop()

if __name__ == '__main__':
    main()


