import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageEnhance, ImageTk, ImageDraw, ImageFont, ImageOps
import numpy as np
import random
import math
import tkinter.font as tkFont

# Y2K-styled ASCII characters
ASCII_CHARS = "@#MWNQBRDGFHKEPSAOZXCVJUYTIL][}{?>=<+_;:~-,. "
CURSOR = "spider"  # Try 'spider', 'pirate', or 'trek' on Linux

class ASCIGEN:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCIGEN")
        # Use a maximized window (with native title bar)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Fixed dimensions for the neural preview area
        self.preview_width = 300
        self.preview_height = 300
        
        # Initialize image and effect parameters
        self.text_color = "#00ff00"
        self.highlight_color = "#0000ff"  # Default highlight color
        self.black_and_white = False
        self.original_image = None
        self.processed_image = None
        self.preview_image = None
        
        # Basic effect multipliers
        self.brightness = 1.75  # Start at 75% position
        self.contrast = 1.75    # Start at 75% position
        self.exposure = 1.75    # Start at 75% position
        self.distortion = 0.0   # glitch effect multiplier
        self.noise = 0.0        # noise effect multiplier
        
        # ChatGPT Tricks flag (for animated chaos effect)
        self.chatgtp_tricks = tk.BooleanVar(value=False)
        
        # Experimental effect variables
        self.invert_ascii = tk.BooleanVar(value=False)
        self.wave_text = tk.DoubleVar(value=0)            # 0 to 20
        self.scramble_rows = tk.BooleanVar(value=False)
        self.rand_char_flip = tk.DoubleVar(value=0)         # 0 to 100
        self.pixelate_factor = tk.IntVar(value=1)           # 1 to 10
        self.glitch_delay = tk.DoubleVar(value=0)           # 0 to 50
        self.brightness_pulse = tk.BooleanVar(value=False)  # (stub)
        self.contrast_jitter = tk.DoubleVar(value=0)        # 0 to 50 (stub)
        self.noise_ripple = tk.DoubleVar(value=0)           # 0 to 50
        self.char_distortion = tk.DoubleVar(value=0)        # 0 to 50
        self.highlight_effect = tk.DoubleVar(value=0)       # 0 to 100
        self.invert_highlight = tk.BooleanVar(value=False)  # Invert all text to appear highlighted
        self.symbol_option = tk.StringVar(value="none")     # Symbols: "none", "squat", "anarchist"
        
        self.setup_y2k_style()
        self.setup_menu()
        self.setup_ui()

    def setup_y2k_style(self):
        self.root.configure(bg='#000000')
        self.root.option_add('*TCombobox*Listbox.font', 'Terminal 10')
        style = ttk.Style()
        style.theme_create('y2k', parent='alt', settings={
            'TFrame': {'configure': {'background': '#000000'}},
            'TLabel': {'configure': {
                'foreground': '#00ff00',
                'background': '#000000',
                'font': ('OCR A Extended', 10)}},
            'TButton': {'configure': {
                'foreground': '#00ff00',
                'background': '#222222',
                'font': ('OCR A Extended', 10, 'bold'),
                'borderwidth': 3},
                'map': {'background': [('active', '#333333')]}},
            'TScale': {'configure': {
                'sliderlength': 20,
                'troughcolor': '#111111'}},
            'TEntry': {'configure': {
                'fieldbackground': '#111111',
                'foreground': '#00ff00'}},
            'TCheckbutton': {'configure': {
                'background': '#000000',
                'foreground': '#00ff00',
                'font': ('OCR A Extended', 10)}},
            'Vertical.TScrollbar': {'configure': {
                'arrowcolor': '#00ff00',
                'troughcolor': '#000000',
                'background': '#222222'}}
        })
        style.theme_use('y2k')
        self.root.config(cursor=CURSOR)

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Image", command=self.load_image)
        file_menu.add_command(label="Export to JPG", command=self.export_to_jpg)
        file_menu.add_command(label="Export to TXT", command=self.export_to_txt)
        file_menu.add_command(label="Export to GIF", command=self.export_to_gif)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def setup_ui(self):
        # Main frame: left column for DIGITAL OUTPUT (ASCII art),
        # right column split vertically with NEURAL PREVIEW (top) and DIGITAL MANIPULATION (bottom)
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        self.setup_ascii_output(main_frame)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        self.setup_preview(right_frame)
        self.setup_effect_controls(right_frame)

    def setup_ascii_output(self, parent):
        self.output_frame = ttk.LabelFrame(parent, text="DIGITAL OUTPUT", padding=10)
        self.output_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.output_frame.rowconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)
        
        self.ascii_text = tk.Text(self.output_frame,
                                  wrap=tk.NONE,
                                  bg='#000000',
                                  fg=self.text_color,
                                  insertbackground='#00ff00',
                                  font=('Courier New', 12),
                                  undo=True)
        self.ascii_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.output_frame, orient=tk.VERTICAL, command=self.ascii_text.yview)
        self.ascii_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def setup_preview(self, parent):
        self.preview_frame = ttk.LabelFrame(parent, text="NEURAL PREVIEW", padding=10,
                                            width=self.preview_width, height=self.preview_height)
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.preview_frame.grid_propagate(False)
        self.image_preview = ttk.Label(self.preview_frame)
        self.image_preview.pack(expand=True, fill=tk.BOTH)

    def setup_effect_controls(self, parent):
        effect_frame = ttk.LabelFrame(parent, text="DIGITAL MANIPULATION", padding=10)
        effect_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        effect_frame.columnconfigure(0, weight=1)
        
        row = 0
        self.brightness_scale = self.create_effect_scale(effect_frame, "BRIGHT", -50, 50, row, start_value=25)
        row += 1
        self.contrast_scale = self.create_effect_scale(effect_frame, "CONTRAST", -50, 50, row, start_value=25)
        row += 1
        self.exposure_scale = self.create_effect_scale(effect_frame, "EXPOSURE", -50, 50, row, start_value=25)
        row += 1
        self.distortion_scale = self.create_effect_scale(effect_frame, "GLITCH", -50, 50, row)
        row += 1
        self.noise_scale = self.create_effect_scale(effect_frame, "STATIC", -50, 50, row)
        row += 1
        
        self.bw_var = tk.BooleanVar(value=False)
        bw_check = ttk.Checkbutton(effect_frame, text="Black & White", variable=self.bw_var,
                                   command=self.toggle_black_and_white)
        bw_check.grid(row=row, column=0, sticky="ew", pady=5)  # fill width
        row += 1
        
        letter_frame = ttk.Frame(effect_frame)
        letter_frame.grid(row=row, column=0, sticky="ew", pady=5)
        ttk.Label(letter_frame, text="LETTER SIZE:").pack(side=tk.LEFT)
        self.letter_size = ttk.Scale(letter_frame, from_=6, to=24, orient=tk.HORIZONTAL, length=200,
                                     command=lambda v: self.adjust_font_size())
        # QUICK FIX: effective letter size = slider value * 0.75 (25% lower)
        self.letter_size.set(12)
        self.letter_size.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        row += 1
        
        ttk.Button(effect_frame, text="Text Color", command=self.choose_text_color).grid(row=row, column=0, sticky="ew", pady=5)
        row += 1
        
        # Invert Highlight Checkbox
        ttk.Checkbutton(effect_frame, text="Invert Highlight", variable=self.invert_highlight,
                        command=self.generate_ascii).grid(row=row, column=0, sticky="ew", pady=5)
        row += 1
        
        # Experimental Effects Section
        exp_frame = ttk.LabelFrame(effect_frame, text="EXPERIMENTAL EFFECTS", padding=5)
        exp_frame.grid(row=row, column=0, sticky="ew", pady=5)
        exp_frame.columnconfigure(0, weight=1)
        row += 1
        
        # 1. Invert ASCII
        inv_check = ttk.Checkbutton(exp_frame, text="Invert ASCII", variable=self.invert_ascii,
                                    command=self.generate_ascii)
        inv_check.grid(row=0, column=0, sticky="ew", pady=2)
        # 2. Wave Text (0 to 20)
        wave_frame = ttk.Frame(exp_frame)
        wave_frame.grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Label(wave_frame, text="Wave Text:").pack(side=tk.LEFT)
        ttk.Button(wave_frame, text="+", command=lambda: self.adjust_wave_text(1)).pack(side=tk.LEFT)
        ttk.Button(wave_frame, text="-", command=lambda: self.adjust_wave_text(-1)).pack(side=tk.LEFT)
        # 3. Scramble Rows
        scramble_check = ttk.Checkbutton(exp_frame, text="Scramble Rows", variable=self.scramble_rows,
                                         command=self.generate_ascii)
        scramble_check.grid(row=2, column=0, sticky="ew", pady=2)
        # 4. Random Character Flip (0 to 100%)
        ttk.Label(exp_frame, text="Rand Char Flip (%):").grid(row=3, column=0, sticky="w")
        flip_scale = ttk.Scale(exp_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.rand_char_flip,
                               command=lambda v: self.generate_ascii())
        flip_scale.grid(row=3, column=1, sticky="ew", padx=5)
        # 5. Pixelate Factor (1 to 10)
        ttk.Label(exp_frame, text="Pixelate Factor:").grid(row=4, column=0, sticky="w")
        pixel_scale = ttk.Scale(exp_frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.pixelate_factor,
                                command=lambda v: self.generate_ascii())
        pixel_scale.grid(row=4, column=1, sticky="ew", padx=5)
        # 6. Glitch Delay (0 to 50)
        ttk.Label(exp_frame, text="Glitch Delay:").grid(row=5, column=0, sticky="w")
        glitch_scale = ttk.Scale(exp_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.glitch_delay,
                                 command=lambda v: self.generate_ascii())
        glitch_scale.grid(row=5, column=1, sticky="ew", padx=5)
        # 7. Brightness Pulse (stub)
        bp_check = ttk.Checkbutton(exp_frame, text="Brightness Pulse", variable=self.brightness_pulse,
                                   command=self.generate_ascii)
        bp_check.grid(row=6, column=0, sticky="ew", pady=2)
        # 8. Contrast Jitter (0 to 50)
        ttk.Label(exp_frame, text="Contrast Jitter:").grid(row=7, column=0, sticky="w")
        jitter_scale = ttk.Scale(exp_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.contrast_jitter,
                                 command=lambda v: self.generate_ascii())
        jitter_scale.grid(row=7, column=1, sticky="ew", padx=5)
        # 9. Noise Ripple (0 to 50)
        ttk.Label(exp_frame, text="Noise Ripple:").grid(row=8, column=0, sticky="w")
        ripple_scale = ttk.Scale(exp_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.noise_ripple,
                                 command=lambda v: self.generate_ascii())
        ripple_scale.grid(row=8, column=1, sticky="ew", padx=5)
        # 10. Character Distortion (0 to 50)
        ttk.Label(exp_frame, text="Char Distortion:").grid(row=9, column=0, sticky="w")
        distortion_scale = ttk.Scale(exp_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.char_distortion,
                                     command=lambda v: self.generate_ascii())
        distortion_scale.grid(row=9, column=1, sticky="ew", padx=5)
        # 11. Highlight Effect (0 to 100)
        ttk.Label(exp_frame, text="Highlight Effect (%):").grid(row=10, column=0, sticky="w")
        highlight_scale = ttk.Scale(exp_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.highlight_effect,
                                    command=lambda v: self.generate_ascii())
        highlight_scale.grid(row=10, column=1, sticky="ew", padx=5)
        # 12. ChatGPT Tricks
        chat_check = ttk.Checkbutton(exp_frame, text="chatgtp_tricks", variable=self.chatgtp_tricks,
                                     command=self.start_chatgtp_tricks)
        chat_check.grid(row=11, column=0, sticky="ew", pady=2)
        
        # Symbols Slider Box
        symbols_frame = ttk.LabelFrame(effect_frame, text="SYMBOLS", padding=5)
        symbols_frame.grid(row=row, column=0, sticky="ew", pady=5)
        symbols_frame.columnconfigure(0, weight=1)
        row += 1
        
        ttk.Radiobutton(symbols_frame, text="None", variable=self.symbol_option, value="none",
                        command=self.generate_ascii).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(symbols_frame, text="Squat Symbol", variable=self.symbol_option, value="squat",
                        command=self.generate_ascii).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(symbols_frame, text="Anarchist Symbol", variable=self.symbol_option, value="anarchist",
                        command=self.generate_ascii).grid(row=2, column=0, sticky="w")

    def adjust_wave_text(self, delta):
        new_value = self.wave_text.get() + delta
        if new_value < 0:
            new_value = 0
        elif new_value > 20:
            new_value = 20
        self.wave_text.set(new_value)
        self.generate_ascii()

    def start_chatgtp_tricks(self):
        if self.chatgtp_tricks.get():
            self.animate_chaos()
        else:
            # Reset the random flip value when turned off
            self.rand_char_flip.set(0)
            self.generate_ascii()

    def animate_chaos(self):
        # Animate chaos: cycle rand_char_flip from -50 to 50 slowly.
        if not self.chatgtp_tricks.get():
            self.rand_char_flip.set(0)
            self.generate_ascii()
            return
        current = self.rand_char_flip.get()
        if not hasattr(self, 'chaos_direction'):
            self.chaos_direction = 1  # start increasing
        if current <= -50:
            self.chaos_direction = 1
        elif current >= 50:
            self.chaos_direction = -1
        new_value = current + self.chaos_direction * 5
        self.rand_char_flip.set(new_value)
        self.generate_ascii()
        self.root.after(100, self.animate_chaos)

    def create_effect_scale(self, parent, label, from_, to, row, start_value=0):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=2)
        ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT)
        scale = ttk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, length=200,
                          command=lambda v, t=label.lower(): self.update_effect(t, float(v)))
        scale.set(start_value)
        scale.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        return scale

    def adjust_font_size(self, event=None):
        # QUICK FIX: effective letter size = slider value * 0.75 (i.e. 25% lower)
        new_font_size = int(float(self.letter_size.get()) * 0.75)
        self.ascii_text.configure(font=('Courier New', new_font_size))
        self.generate_ascii()

    def toggle_black_and_white(self):
        self.black_and_white = self.bw_var.get()
        if self.original_image:
            self.process_image()
            self.show_preview()
            self.generate_ascii()

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color", initialcolor=self.text_color)
        if color[1]:
            self.text_color = color[1]
            self.ascii_text.configure(fg=self.text_color)
            self.generate_ascii()

    def update_effect(self, effect_type, value):
        if effect_type == "bright":
            self.brightness = 1 + (value / 50.0)
        elif effect_type == "contrast":
            self.contrast = 1 + (value / 50.0)
        elif effect_type == "exposure":
            self.exposure = 1 + (value / 50.0)
        elif effect_type == "glitch":
            self.distortion = value / 50.0
        elif effect_type == "static":
            self.noise = abs(value) / 50.0
        if self.original_image:
            self.process_image()
            self.show_preview()
            self.generate_ascii()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[
            ("DIGITAL IMAGES", "*.jpg *.jpeg *.png *.bmp *.gif")
        ])
        if path:
            try:
                self.original_image = Image.open(path).convert("RGB")
                self.process_image()
                self.show_preview()
                self.generate_ascii()
            except Exception as e:
                self.show_error("LOAD ERROR", f"FAILED TO ACCESS:\n{str(e)}")

    def process_image(self):
        try:
            img = self.original_image.copy()
            img = ImageEnhance.Brightness(img).enhance(self.brightness)
            img = ImageEnhance.Contrast(img).enhance(self.contrast)
            img = ImageEnhance.Brightness(img).enhance(self.exposure)
            if self.distortion != 0:
                img = self.apply_distortion(img)
            if self.noise != 0:
                img = self.apply_noise(img)
            if self.black_and_white:
                img = img.convert("L")
            self.processed_image = img
        except Exception as e:
            self.show_error("PROCESSING ERROR", str(e))

    def apply_distortion(self, img):
        width, height = img.size
        pixels = np.array(img)
        for y in range(height):
            shift = int(self.distortion * 50 * math.sin(y / 10))
            pixels[y] = np.roll(pixels[y], shift, axis=0)
        if abs(self.distortion) > 0.5:
            offset = int(abs(self.distortion) * 20)
            r, g, b = pixels[..., 0], pixels[..., 1], pixels[..., 2]
            if self.distortion < 0:
                offset = -offset
            pixels[..., 0] = np.roll(r, offset)
            pixels[..., 2] = np.roll(b, -offset)
        return Image.fromarray(pixels)

    def apply_noise(self, img):
        pixels = np.array(img).astype(float)
        noise_level = self.noise * 50
        noise = np.random.normal(0, noise_level, pixels.shape)
        pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(pixels)

    def show_preview(self):
        try:
            # Scale image to fit maximally into the fixed preview box while preserving aspect ratio.
            img = self.processed_image.copy()
            orig_w, orig_h = img.size
            scale = min(self.preview_width / orig_w, self.preview_height / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            preview = img.resize((new_w, new_h))
            self.preview_image = ImageTk.PhotoImage(preview)
            self.image_preview.configure(image=self.preview_image)
        except Exception as e:
            self.show_error("PREVIEW ERROR", str(e))

    def generate_ascii(self, event=None):
        if not self.processed_image:
            return
        try:
            self.ascii_text.update_idletasks()
            widget_width = self.ascii_text.winfo_width()
            widget_height = self.ascii_text.winfo_height()
            if widget_width <= 0 or widget_height <= 0:
                return
            current_font = tkFont.Font(font=self.ascii_text.cget("font"))
            char_width = current_font.measure("A")
            line_height = current_font.metrics("linespace")
            num_cols = max(1, widget_width // char_width)
            num_rows = max(1, widget_height // line_height)
            img = self.processed_image.resize((num_cols, num_rows))
            img = img.convert("L")
            pixels = np.array(img)
            # Use inverted mapping if selected
            ascii_chars = ASCII_CHARS[::-1] if self.invert_ascii.get() else ASCII_CHARS
            ascii_lines = []
            for row_pixels in pixels:
                line = "".join([ascii_chars[min(int(p * (len(ascii_chars) - 1) / 255), len(ascii_chars) - 1)] for p in row_pixels])
                ascii_lines.append(line)
            # Experimental effects:
            if self.wave_text.get() > 0:
                for i in range(len(ascii_lines)):
                    offset = int(self.wave_text.get() * math.sin(i/2))
                    ascii_lines[i] = (" " * abs(offset) + ascii_lines[i]) if offset >= 0 else ascii_lines[i][abs(offset):]
            if self.scramble_rows.get():
                random.shuffle(ascii_lines)
            if self.rand_char_flip.get() > 0:
                new_lines = []
                for line in ascii_lines:
                    new_line = ""
                    for ch in line:
                        if ch != "\n" and random.random() < (self.rand_char_flip.get()/100):
                            new_line += random.choice(ascii_chars)
                        else:
                            new_line += ch
                    new_lines.append(new_line)
                ascii_lines = new_lines
            if self.glitch_delay.get() > 0:
                glitch_lines = []
                n = max(1, int(self.glitch_delay.get()))
                for i, line in enumerate(ascii_lines):
                    glitch_lines.append(line)
                    if i % n == 0:
                        glitch_lines.append(line)
                ascii_lines = glitch_lines
            if self.noise_ripple.get() > 0:
                new_lines = []
                for line in ascii_lines:
                    line_list = list(line)
                    for i in range(len(line_list)-1):
                        if random.random() < (self.noise_ripple.get()/50):
                            line_list[i], line_list[i+1] = line_list[i+1], line_list[i]
                    new_lines.append("".join(line_list))
                ascii_lines = new_lines
            if self.char_distortion.get() > 0:
                new_lines = []
                for line in ascii_lines:
                    new_line = ""
                    for ch in line:
                        new_line += ch
                        if random.random() < (self.char_distortion.get()/50):
                            new_line += " "
                    new_lines.append(new_line)
                ascii_lines = new_lines
            if self.pixelate_factor.get() > 1:
                factor = self.pixelate_factor.get()
                new_lines = []
                for line in ascii_lines:
                    new_lines.extend([line] * factor)
                ascii_lines = new_lines
            # Highlight Effect
            if self.highlight_effect.get() > 0:
                new_lines = []
                for line in ascii_lines:
                    new_line = ""
                    for ch in line:
                        if random.random() < (self.highlight_effect.get()/100):
                            new_line += f"\033[7m{ch}\033[0m"  # Highlighted text
                        else:
                            new_line += ch
                    new_lines.append(new_line)
                ascii_lines = new_lines
            # Invert Highlight
            if self.invert_highlight.get():
                ascii_lines = [f"\033[7m{line}\033[0m" for line in ascii_lines]
            # Symbols
            if self.symbol_option.get() == "squat":
                squat_symbol = [
                    "  ██████  ",
                    "██      ██",
                    "██  ██  ██",
                    "██  ██  ██",
                    "  ██████  "
                ]
                ascii_lines = squat_symbol + ascii_lines
            elif self.symbol_option.get() == "anarchist":
                anarchist_symbol = [
                    "  ██████  ",
                    "██  ██  ██",
                    "██  ██  ██",
                    "██  ██  ██",
                    "  ██████  "
                ]
                ascii_lines = anarchist_symbol + ascii_lines
            ascii_str = "\n".join(ascii_lines)
            self.ascii_text.delete(1.0, tk.END)
            self.ascii_text.insert(tk.END, ascii_str)
        except Exception as e:
            self.show_error("RENDER ERROR", str(e))

    def export_to_txt(self):
        ascii_art = self.ascii_text.get(1.0, tk.END)
        if not ascii_art.strip():
            self.show_warning("NO DATA", "Please generate ASCII art before exporting.")
            return
        text_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if text_path:
            try:
                with open(text_path, "w") as f:
                    f.write(ascii_art)
                messagebox.showinfo("EXPORT COMPLETE", f"ASCII ART SAVED TO:\n{text_path}")
            except Exception as e:
                self.show_error("EXPORT ERROR", str(e))

    def export_to_jpg(self):
        ascii_art = self.ascii_text.get(1.0, tk.END)
        if not ascii_art.strip():
            self.show_warning("NO DATA", "Please generate ASCII art before exporting.")
            return
        image_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )
        if image_path:
            try:
                font = ImageFont.load_default()
                lines = ascii_art.split("\n")
                line_height = font.getsize("A")[1]
                img_width = max(font.getsize(line)[0] for line in lines if line) if lines else 0
                img_height = line_height * len(lines)
                img = Image.new("RGB", (img_width, img_height), color="black")
                draw = ImageDraw.Draw(img)
                for i, line in enumerate(lines):
                    draw.text((0, i * line_height), line, font=font, fill=self.text_color)
                img.save(image_path)
                messagebox.showinfo("EXPORT COMPLETE", f"IMAGE SAVED TO:\n{image_path}")
            except Exception as e:
                self.show_error("EXPORT ERROR", str(e))

    def export_to_gif(self):
        ascii_art = self.ascii_text.get(1.0, tk.END)
        if not ascii_art.strip():
            self.show_warning("NO DATA", "Please generate ASCII art before exporting.")
            return
        gif_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF Files", "*.gif"), ("All Files", "*.*")]
        )
        if gif_path:
            try:
                font = ImageFont.load_default()
                lines = ascii_art.split("\n")
                line_height = font.getsize("A")[1]
                img_width = max(font.getsize(line)[0] for line in lines if line) if lines else 0
                img_height = line_height * len(lines)
                frames = []
                for i in range(10):  # Create 10 frames for the GIF
                    img = Image.new("RGB", (img_width, img_height), color="black")
                    draw = ImageDraw.Draw(img)
                    for j, line in enumerate(lines):
                        draw.text((0, j * line_height), line, font=font, fill=self.text_color)
                    frames.append(img)
                frames[0].save(gif_path, save_all=True, append_images=frames[1:], loop=0, duration=100)
                messagebox.showinfo("EXPORT COMPLETE", f"GIF SAVED TO:\n{gif_path}")
            except Exception as e:
                self.show_error("EXPORT ERROR", str(e))

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.root)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIGEN(root)
    root.mainloop()
