import json
import sys
import threading
import easyocr
import dxcam
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
import keyboard, time
import win32.win32api as win32api
import cv2
import pytesseract
import customtkinter as ctk
import tkinter as tk
import threading




class ScreenCapture:
    def __init__(self):
        
        self.camera = dxcam.create(output_color="GRAY")
        self.reader = easyocr.Reader(['en'])
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True, '-topmost', True)
        self.window.overrideredirect(1)
        self.window.attributes("-alpha", 0.3)

        self.canvas = tk.Canvas(self.window, bg='white')
        self.canvas.pack(fill='both', expand=True)
        

        self.window.attributes('-transparentcolor', 'white')
        

        
        self.test_drawing()

        keyboard.on_press_key('x', self.on_x_pressed)
        keyboard.on_release_key('x', self.on_x_released)


        self.window.mainloop()


    def test_drawing(self):
        # Draw a red rectangle to test
        self.canvas.create_rectangle(50, 50, 100, 100, fill='red')
        self.canvas.update()
        print("Test drawing executed")

    def draw_point(self, aim_x, aim_y):
        
        # Clear the canvas
        self.canvas.delete('all')
    
        # Draw the aim point
        radius = 2
        self.canvas.create_oval(aim_x - radius, aim_y - radius, aim_x + radius, aim_y + radius, fill='#00ffff', width=0)
        self.canvas.update()

    def calculate_offset(self, distance):
        velocity = 900
        optics = 6

        gravity = 9.80665
        k1 = 14090 
        character_height = 1.75

        opx = ((gravity * ((distance/velocity) ** 2)) / 2) * ((k1 / distance) * (1 / character_height)) * (optics / 8)
        return opx

    def on_x_pressed(self, e):
        global is_x_pressed
        is_x_pressed = True
        print("'x' key pressed")  # Debug print
        threading.Thread(target=self.capture_screen).start()

    def on_x_released(self, e):
        global is_x_pressed
        is_x_pressed = False
        print("'x' key released")  # Debug print

    def capture_screen(self, filename="screenshot.jpg"):
        global is_x_pressed

        while is_x_pressed:
            # print("Capture screen running")  # Debug print
            # Add your screen capture and processing logic here
            time.sleep(0.05)

            # Capture full screen
            # Capture a frame within a certain region
            left, top = (1920 - 10) // 2 + 70, (1080 - 250) // 2
            right, bottom = left + 50 + 20, top + 50
            region = (left, top, right, bottom)
            frame = self.camera.grab(region=region)

            if frame is None:
                print("Failed to capture frame. Check region or camera setup.")
                return
            
            # Debug: Print frame shape and dtype
            print(f"Frame shape: {frame.shape}, Frame dtype: {frame.dtype}")
            
            # frame = self.preprocess_image(frame)

            # Convert to uint8 and ensure correct shape
            frame = frame.astype(np.uint8)
            if len(frame.shape) == 2:  # If grayscale, add a channel dimension
                frame = np.expand_dims(frame, axis=-1)
            if frame.shape[2] == 1:  # Single channel grayscale
                frame = np.repeat(frame, 3, axis=2)  # Repeat grayscale values across 3 channels
            
            # Create PIL Image
            try:
                # image = Image.fromarray(frame, mode='L')
                image = Image.fromarray(frame, mode='RGB')
                draw = ImageDraw.Draw(image)
                draw.rectangle([left-region[0], top-region[1], 
                                right-region[0], bottom-region[1]], 
                            outline="white", width=2)
                

                # image.save(filename)

                image_np = np.array(image)
                result = self.reader.readtext(image_np, detail = 0, allowlist="0123456789")
                print(f"Parsed text as {result}")
                extracted_number = int(result[0])
                if extracted_number > 0:
                    
                    opx = self.calculate_offset(extracted_number)
                    print(opx)
                    center_x = self.window.winfo_screenwidth() // 2
                    center_y = self.window.winfo_screenheight() // 2

                    if opx is not None and opx > 0:
                        aim_x = center_x
                        aim_y = center_y + int(opx)
                        print(f"Aim X: {aim_x}, Aim Y: {aim_y}")

                        self.draw_point(aim_x, aim_y)

                # print(f"Saved screenshot as {filename}")
            except Exception as e:
                print(f"Error creating/saving image: {e}")
            
        # # Convert to image and save
        # image = Image.fromarray(frame)

        # draw = ImageDraw.Draw(image)
        # draw.rectangle([left, top, right, bottom], outline="red", width=2)
        # image.save(filename)
        
        # # image_np = np.array(image)
        # # result = self.reader.readtext(image_np, detail = 0)
        # print(f"Parsed text as {filename}")

    def start_capture_listener(self, hotkey="t"):
        keyboard.add_hotkey(hotkey, self.capture_screen)
        keyboard.wait()  # Keep the script running

        

is_x_pressed = False

# Usage
capture = ScreenCapture()
capture.start_capture_listener()
