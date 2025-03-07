# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageEnhance, ImageTk, ImageDraw, ImageFont, ImageOps, ImageColor
import numpy as np
import random
import math
import tkinter.font as tkFont

# Y2K-styled ASCII characters
ASCII_CHARS = "@#MWNQBGFHKEPSAOZXafeowgp][}{?>=<+_;:~-,."
CURSOR = "pirate"  # Try 'spider', 'pirate', or 'trek' on Linux

class ASCIGEN:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCIGEN")
        # Use a maximized window (with native title bar)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.font_job_id = None  # Track scheduled font updates for letter resize 
       
        
        # Fixed dimensions for the neural preview area
        self.preview_width = 250
        self.preview_height = 250
        
        # Initialize image and effect parameters
        self.bg_color = "#000000"
        self.text_color = "#00ff00"
        self.highlight_color = "#00ff00"  # Default highlight color
        self.black_and_white = False
        self.original_image = None
        self.processed_image = None
        self.preview_image = None
        
        # Basic effect multipliers
        self.brightness = 1
        self.contrast = 1   
        self.exposure = 1   
        self.distortion = 0.0   # glitch effect multiplier
        self.noise = 0.0        # noise effect multiplier
        
        # ChatGPT Tricks flag (for animated chaos effect)
        self.chatgtp_tricks = tk.BooleanVar(value=False)
        
        # Experimental effect variables
        self.invert_ascii = tk.BooleanVar(value=False)
        self.wave_text = tk.DoubleVar(value=0)            # 0 to 20
        self.scramble_rows = tk.BooleanVar(value=False)
        self.rand_char_flip = tk.DoubleVar(value=0)         # 0 to 100
        self.glitch_delay = tk.DoubleVar(value=0)           # 0 to 50
        self.brightness_pulse = tk.BooleanVar(value=False)  # (stub)
        self.noise_ripple = tk.DoubleVar(value=0)           # 0 to 50
        self.highlight_effect = tk.DoubleVar(value=0)       # 0 to 100
                
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
        file_menu.add_command(label="Export to TXT", command=self.export_to_txt)
        file_menu.add_command(label="Export to PNG", command=self.export_to_png)
        file_menu.add_command(label="Export to JPG", command=self.export_to_jpg)
        file_menu.add_command(label="Export to GIF", command=self.export_to_gif)
        file_menu.add_command(label="About", command=self.about_section)
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
        
    def setup_ascii_output(self, parent):
        self.ascii_text = tk.Text(parent,
                                wrap=tk.NONE,
                                bg='#000000',
                                fg=self.text_color,
                                font=('Courier New', 12),
                                padx=10,  # Horizontal padding
                                pady=10)  # Vertical padding
        self.ascii_text.grid(row=0, column=0, sticky="nsew")

    def setup_preview(self, parent):
        self.preview_frame = ttk.Frame(parent)
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
        # Force fixed dimensions
        self.preview_frame.config(width=self.preview_width, 
                                height=self.preview_height)
        self.preview_frame.grid_propagate(False)  # Prevent size changes
        self.preview_frame.pack_propagate(False)
        
        self.image_preview = ttk.Label(self.preview_frame)
        self.image_preview.pack(expand=True, fill=tk.BOTH)
        
        # Replace the Configure binding with this
        self.preview_frame.bind("<Configure>", self.on_preview_resize)
    def on_preview_resize(self, event):
        # Maintain fixed size constraints
        if self.preview_frame.winfo_width() != self.preview_width or \
        self.preview_frame.winfo_height() != self.preview_height:
            
            self.preview_frame.config(width=self.preview_width,
                                    height=self.preview_height)
        self.show_preview()

    def setup_effect_controls(self, parent):
        effect_frame = ttk.LabelFrame(parent, text="DIGITAL MANIPULATION", padding=10)
        effect_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        effect_frame.columnconfigure(0, weight=1)
        
        row = 0
        # Text Color Button
        ttk.Button(effect_frame, text="Text Color", command=self.choose_text_color).grid(row=row, column=0, sticky="ew", pady=5)
        row += 1

        ttk.Button(effect_frame, text="Background Color", command=self.choose_background_color).grid(row=row, column=0, sticky="ew", pady=5)
        row += 1

        # Letter Size
        letter_frame = ttk.Frame(effect_frame)
        letter_frame.grid(row=row, column=0, sticky="ew", pady=5)
        ttk.Label(letter_frame, text="LETTER SIZE:").pack(side=tk.LEFT)
        self.letter_size = ttk.Scale(letter_frame, from_=6, to=24, orient=tk.HORIZONTAL,
                                    command=lambda v: self.adjust_font_size())
        self.letter_size.set(12)
        self.letter_size.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        row += 1
        
        # Brightness
        self.brightness_scale = self.create_effect_scale(effect_frame, "BRIGHTNESS", -50, 50, row, start_value=0)
        row += 1
        
        # Contrast
        self.contrast_scale = self.create_effect_scale(effect_frame, "CONTRAST", -50, 50, row, start_value=0)
        row += 1
        
        # Exposure
        self.exposure_scale = self.create_effect_scale(effect_frame, "EXPOSURE", -50, 50, row, start_value=0)
        row += 1
        
        # Glitch
        self.distortion_scale = self.create_effect_scale(effect_frame, "GLITCH", -50, 50, row)
        row += 1
        
        # Static
        self.noise_scale = self.create_effect_scale(effect_frame, "STATIC", -50, 50, row)
        row += 1
        
        # Black & White Checkbox
        self.bw_var = tk.BooleanVar(value=False)
        bw_check = ttk.Checkbutton(effect_frame, text="Black & White", variable=self.bw_var,
                                command=self.toggle_black_and_white)
        bw_check.grid(row=row, column=0, sticky="ew", pady=5)
        row += 1
        

        
        # Invert ASCII Checkbox
        ttk.Checkbutton(effect_frame, text="Invert ASCII", variable=self.invert_ascii,
                        command=self.generate_ascii).grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        
        # Wave Text
        wave_frame = ttk.Frame(effect_frame)
        wave_frame.grid(row=row, column=0, sticky="ew", pady=2)
        ttk.Label(wave_frame, text="Wave Text:").pack(side=tk.LEFT)
        ttk.Button(wave_frame, text="+", command=lambda: self.adjust_wave_text(1)).pack(side=tk.LEFT)
        ttk.Button(wave_frame, text="-", command=lambda: self.adjust_wave_text(-1)).pack(side=tk.LEFT)
        row += 1
        
        # Scramble Rows Checkbox
        ttk.Checkbutton(effect_frame, text="Scramble Rows", variable=self.scramble_rows,
                        command=self.generate_ascii).grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        
        # Random Character Flip
        rand_flip_frame = ttk.Frame(effect_frame)
        rand_flip_frame.grid(row=row, column=0, sticky="ew", pady=2)
        ttk.Label(rand_flip_frame, text="Rand Char Flip (%):").pack(side=tk.LEFT)
        flip_scale = ttk.Scale(rand_flip_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                            variable=self.rand_char_flip, command=lambda v: self.generate_ascii())
        flip_scale.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        row += 1
        
        # Glitch Delay
        glitch_delay_frame = ttk.Frame(effect_frame)
        glitch_delay_frame.grid(row=row, column=0, sticky="ew", pady=2)
        ttk.Label(glitch_delay_frame, text="Glitch Delay:").pack(side=tk.LEFT)
        glitch_scale = ttk.Scale(glitch_delay_frame, from_=0, to=50, orient=tk.HORIZONTAL,
                                variable=self.glitch_delay, command=lambda v: self.generate_ascii())
        glitch_scale.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        row += 1
        
        # Brightness Pulse Checkbox
        ttk.Checkbutton(effect_frame, text="Brightness Pulse", variable=self.brightness_pulse,
                        command=self.generate_ascii).grid(row=row, column=0, sticky="ew", pady=2)
        row += 1
        
        # Noise Ripple
        noise_ripple_frame = ttk.Frame(effect_frame)
        noise_ripple_frame.grid(row=row, column=0, sticky="ew", pady=2)
        ttk.Label(noise_ripple_frame, text="Noise Ripple:").pack(side=tk.LEFT)
        ripple_scale = ttk.Scale(noise_ripple_frame, from_=0, to=50, orient=tk.HORIZONTAL,
                                variable=self.noise_ripple, command=lambda v: self.generate_ascii())
        ripple_scale.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        row += 1
        
        # Highlight Effect
        highlight_frame = ttk.Frame(effect_frame)
        highlight_frame.grid(row=row, column=0, sticky="ew", pady=2)
        ttk.Label(highlight_frame, text="Highlight Effect (%):").pack(side=tk.LEFT)
        highlight_scale = ttk.Scale(highlight_frame, from_=0, to=5, orient=tk.HORIZONTAL,
                                    variable=self.highlight_effect, command=lambda v: self.generate_ascii())
        highlight_scale.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        row += 1
        
        # ChatGPT Tricks Checkbox
        ttk.Checkbutton(effect_frame, text="ChatGPT Tricks", variable=self.chatgtp_tricks,
                        command=self.start_chatgtp_tricks).grid(row=row, column=0, sticky="ew", pady=2)
        row += 1


    
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
   
        # Cancel any pending font updates
        if self.font_job_id is not None:
            self.root.after_cancel(self.font_job_id)
        
        # Schedule the actual update after 150ms of inactivity
        self.font_job_id = self.root.after(150, self._apply_font_size_update)

    def _apply_font_size_update(self):
        try:
            # Calculate new font size (75% of slider value)
            new_size = int(float(self.letter_size.get()) * 0.75)
            
            # Get current font settings
            current_font = tkFont.Font(font=self.ascii_text.cget("font"))
            current_size = current_font.actual()["size"]
            
            # Only update if size changed
            if new_size != current_size:
                self.ascii_text.configure(font=('Courier New', int(new_size)))
                self.generate_ascii()
        finally:
            self.font_job_id = None  # Reset job tracker  

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

    def choose_background_color(self):
        color = colorchooser.askcolor(title="Choose Background Color", initialcolor=self.bg_color)
        if color[1]:
            self.bg_color = color[1]
            self.ascii_text.configure(bg=self.bg_color)
            self.generate_ascii()
            
    def update_effect(self, effect_type, value):
        if effect_type == "brightness":
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
            if not self.original_image:  # Check if original_image is loaded
                return

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

            self.processed_image = img  # Update processed_image

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
            if not self.processed_image:  # Check if processed_image is None
                return  # Exit if no image is loaded

            # Get the dimensions of the preview frame
            preview_width = self.preview_frame.winfo_width()
            preview_height = self.preview_frame.winfo_height()

            # Get the dimensions of the original image
            orig_width, orig_height = self.processed_image.size

            # Calculate the scaling factor to fit the image within the preview area
            scale = min(
                preview_width / orig_width,
                preview_height / orig_height,
                1.0  # Prevent upscaling beyond original size
            )

            # Calculate new dimensions while maintaining aspect ratio
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)

            # Resize the image
            resized_image = self.processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create a blank image with the size of the preview area
            blank_image = Image.new("RGB", (preview_width, preview_height), "black")

            # Calculate the position to center the resized image
            x_offset = (preview_width - new_width) // 2
            y_offset = (preview_height - new_height) // 2

            # Paste the resized image onto the blank image at the calculated position
            blank_image.paste(resized_image, (x_offset, y_offset))

            # Convert to PhotoImage and display
            self.preview_image = ImageTk.PhotoImage(blank_image)
            self.image_preview.configure(image=self.preview_image)

        except Exception as e:
            self.show_error("PREVIEW ERROR", str(e))

    def generate_ascii(self, event=None):
        if not self.processed_image:  # Check if processed_image is None
            return  # Exit if no image is loaded

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

            # Apply effects (wave text, scramble rows, etc.)
            if self.wave_text.get() > 0:
                for i in range(len(ascii_lines)):
                    offset = int(self.wave_text.get() * math.sin(i / 2))
                    ascii_lines[i] = (" " * abs(offset) + ascii_lines[i]) if offset >= 0 else ascii_lines[i][abs(offset):]

            if self.scramble_rows.get():
                random.shuffle(ascii_lines)

            if self.rand_char_flip.get() > 0:
                new_lines = []
                for line in ascii_lines:
                    new_line = ""
                    for ch in line:
                        if ch != "\n" and random.random() < (self.rand_char_flip.get() / 100):
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
                    for i in range(len(line_list) - 1):
                        if random.random() < (self.noise_ripple.get() / 50):
                            line_list[i], line_list[i + 1] = line_list[i + 1], line_list[i]
                    new_lines.append("".join(line_list))
                ascii_lines = new_lines

            # Highlight Effect
            if self.highlight_effect.get() > 0:
                new_lines = []
                for line in ascii_lines:
                    new_line = ""
                    for ch in line:
                        if random.random() < (self.highlight_effect.get() / 100):
                            new_line += f"\033[7m{ch}\033[0m"  # Highlighted text
                        else:
                            new_line += ch
                    new_lines.append(new_line)
                ascii_lines = new_lines

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
                # Get font info from the text widget
                current_font = tkFont.Font(font=self.ascii_text.cget("font"))
                font_name = current_font.actual()["family"]
                font_size = current_font.actual()["size"]
                
                # Calculate metrics using Tkinter's font system
                char_width = current_font.measure("A")
                line_height = current_font.metrics("linespace")
                
                # Split ASCII art into lines
                lines = ascii_art.split("\n")
                
                # Calculate image dimensions
                max_width = max(current_font.measure(line) for line in lines) if lines else 0
                img_height = line_height * len(lines)

                # Export with right background color 
                color_tuple = ImageColor.getrgb(self.bg_color)
                
                # Create image with proper dimensions
                img = Image.new("RGB", (max_width, img_height), color=color_tuple)
                draw = ImageDraw.Draw(img)
                
                # Try to load matching font for Pillow
                try:
                    font = ImageFont.truetype(font_name.lower() + ".ttf", font_size)
                except IOError:
                    # Fallback to default font with Tkinter metrics
                    font = ImageFont.load_default()
                    # Use Tkinter's measurements for default font
                    char_width = current_font.measure("A")
                    line_height = current_font.metrics("linespace")

                # Draw text using calculated metrics
                for i, line in enumerate(lines):
                    draw.text(
                        (0, i * line_height),
                        line,
                        font=font,
                        fill=self.text_color
                    )

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
                # Get font metrics from Tkinter
                current_font = tkFont.Font(font=self.ascii_text.cget("font"))
                font_name = current_font.actual()["family"]
                font_size = current_font.actual()["size"]
                
                # Calculate dimensions using Tkinter's metrics
                char_width = current_font.measure("A")
                line_height = current_font.metrics("linespace")
                lines = ascii_art.split("\n")
                
                # Calculate image size
                max_width = max(current_font.measure(line) for line in lines) if lines else 0
                img_height = line_height * len(lines)

                # Export with right background color 
                color_tuple = ImageColor.getrgb(self.bg_color)
                
                # Create base image
                base_img = Image.new("RGB", (max_width, img_height), color=color_tuple)
                draw = ImageDraw.Draw(base_img)
                
                # Try to load matching font
                try:
                    font = ImageFont.truetype(font_name.lower() + ".ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()
                    # Use approximate measurements if default font
                    char_width = 8
                    line_height = 16

                # Create animated frames with glitch effect
                frames = []
                for frame_num in range(10):
                    img = base_img.copy()
                    draw = ImageDraw.Draw(img)
                    
                    # Add frame variation
                    for j, line in enumerate(lines):
                        x_offset = int(5 * math.sin(frame_num + j/2))  # Wave effect
                        y_pos = j * line_height
                        
                        # Add random glitch offset every 3 frames
                        if frame_num % 3 == 0 and random.random() > 0.7:
                            x_offset += random.randint(-3, 3)
                            
                        draw.text(
                            (x_offset, y_pos),
                            line,
                            font=font,
                            fill=self.text_color
                        )
                    
                    # Add subtle brightness variation
                    if self.brightness_pulse.get():
                        enhancer = ImageEnhance.Brightness(img)
                        img = enhancer.enhance(1 + 0.1 * math.sin(frame_num/2))
                    
                    frames.append(img)

                # Save animated GIF with optimization
                frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=100,
                    loop=0,
                    optimize=True,
                    quality=80
                )
                messagebox.showinfo("EXPORT COMPLETE", f"GIF SAVED TO:\n{gif_path}")
                
            except Exception as e:
                self.show_error("EXPORT ERROR", str(e))

    def export_to_png(self):
        ascii_art = self.ascii_text.get(1.0, tk.END)
        if not ascii_art.strip():
            self.show_warning("NO DATA", "Please generate ASCII art before exporting.")
            return
            
        png_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        
        if png_path:
            try:
                # Get font metrics from Tkinter
                current_font = tkFont.Font(font=self.ascii_text.cget("font"))
                font_name = current_font.actual()["family"]
                font_size = current_font.actual()["size"]
                
                # Calculate dimensions using Tkinter's metrics
                char_width = current_font.measure("A")
                line_height = current_font.metrics("linespace")
                lines = ascii_art.split("\n")
                
                # Calculate image size with padding
                max_width = max(current_font.measure(line) for line in lines) if lines else 0
                img_height = line_height * len(lines)
                
                # Add 10% padding
                padding = int(max_width * 0.1)
                img_width = max_width + 2 * padding
                img_height += 2 * padding
                
                # Export with right background color 
                color_tuple = ImageColor.getrgb(self.bg_color)
                
                # Create image with padding
                img = Image.new("RGB", (max_width, img_height), color=color_tuple)
                draw = ImageDraw.Draw(img)
                
                # Try to load matching font
                try:
                    font = ImageFont.truetype(font_name.lower() + ".ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()
                    # Use approximate measurements if default font
                    char_width = 8
                    line_height = 16

                # Draw text with padding
                for j, line in enumerate(lines):
                    draw.text(
                        (padding, padding + j * line_height),
                        line,
                        font=font,
                        fill=self.text_color
                    )
                
                # Add optional effects
                if self.highlight_effect.get() > 0:
                    # Add subtle highlight effect
                    highlight_img = img.copy()
                    highlight_draw = ImageDraw.Draw(highlight_img)
                    for j, line in enumerate(lines):
                        if random.random() < (self.highlight_effect.get()/100):
                            highlight_draw.rectangle(
                                [
                                    (padding, padding + j * line_height),
                                    (padding + max_width, padding + (j+1) * line_height)
                                ],
                                fill=self.highlight_color
                            )
                    # Blend highlight layer
                    img = Image.blend(img, highlight_img, alpha=0.3)
                
                # Save with maximum quality
                img.save(png_path, "PNG", compress_level=1)
                messagebox.showinfo("EXPORT COMPLETE", f"PNG SAVED TO:\n{png_path}")
                
            except Exception as e:
                self.show_error("EXPORT ERROR", str(e))

    def about_section(self):
        about = tk.Toplevel(self.root)
        about.title("About")
        
        # Set fixed window size
        window_width = 900
        window_height = 800
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate centered position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Apply geometry with calculated position
        about.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Rest of your About window code...
        about.resizable(False, False)
        about.configure(bg='#000000')
        
        # Content with ASCII art header
        content = [
            "▓█████▄  ██▀███   ▒█████   ▒█████   ██▓███  ",
            "▒██▀ ██▌▓██ ▒ ██▒▒██▒  ██▒▒██▒  ██▒▓██░  ██▒",
            "░██   █▌▓██ ░▄█ ▒▒██░  ██▒▒██░  ██▒▓██░ ██▓▒",
            "░▓█▄   ▌▒██▀▀█▄  ▒██   ██░▒██   ██░▒██▄█▓▒ ▒",
            "░▒████▓ ░██▓ ▒██▒░ ████▓▒░░ ████▓▒░▒██▒ ░  ░",
            " ▒▒▓  ▒ ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░▒░▒░ ▒▓▒░ ░  ░",
            " ░ ▒  ▒   ░▒ ░ ▒░  ░ ▒ ▒░   ░ ▒ ▒░ ░▒ ░     ",
            " ░ ░  ░   ░░   ░ ░ ░ ░ ▒  ░ ░ ░ ▒  ░░       ",
            "   ░       ░         ░ ░      ░ ░           ",
            "",
            "ASCII IMAGE MANIPULATOR GENERATOR ALPHA",
            "DEVELOPED UNDER NUCLEAR LICENSE 0X7E3",
            "",
            "",
            "" ,
            "-" ,
            "-" ,
            "",
            "",
            "COPYLEFT"
        ]

        # Create scrolling container
        canvas = tk.Canvas(about, bg='#000000', highlightthickness=0)
        scrollbar = ttk.Scrollbar(about, orient=tk.VERTICAL, command=canvas.yview)
        frame = ttk.Frame(canvas)
        
        # Configure grid
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        about.grid_columnconfigure(0, weight=1)
        about.grid_rowconfigure(0, weight=1)
        
        # Add content labels
        for idx, line in enumerate(content):
            lbl = ttk.Label(frame, 
                        text=line,
                        font=('OCR A Extended', 10),
                        foreground='#00ff00',
                        background='#000000')
            lbl.grid(row=idx, column=0, sticky="w", padx=10, pady=2)
        
        # Configure scrolling
        canvas.create_window((0,0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add close button
        btn = ttk.Button(about, 
                    text="ACKNOWLEDGE", 
                    command=about.destroy,
                    style='y2k.TButton')
        btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Maintain style consistency
        about.config(cursor=CURSOR)
        about.bind("<Escape>", lambda e: about.destroy())

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.root)

    def show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIGEN(root)
    root.mainloop()
