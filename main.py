from typing import List, Tuple
import math
import requests
import urllib3
import tkinter as tk
from PIL import ImageGrab

# Ignore insercure SSL ceritifcate warning since it is not relevant here
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SimpleOCR:
    """ Class to convert image captured from the game to text """
    def __init__(self):
        # An array of size 11 (digits 0-9 and no digit) x 120 (10 x 12 pixels) target grayscale data of the digits
        # The array at i-th index corresponds to the grayscale values of digit i (eg: target_digits[3] are the grayscale values for 3)
        # except for 10th index where the grayscale value is for blank (no digit)
        self.target_digits = [[25, 24, 51, 163, 217, 204, 140, 29, 23, 24, 24, 50, 212, 236, 192, 231, 238, 175, 23, 23, 25, 152, 238, 114, 0, 58, 235, 238, 75, 21, 35, 229, 238, 22, 13, 24, 184, 238, 165, 15, 68, 238, 230, 0, 22, 24, 134, 238, 201, 7, 93, 238, 220, 1, 25, 25, 115, 238, 228, 3, 104, 238, 233, 2, 22, 23, 101, 238, 218, 1, 80, 238, 238, 15, 23, 23, 111, 238, 192, 2, 51, 238, 238, 69, 22, 25, 137, 238, 147, 4, 24, 185, 238, 172, 18, 32, 206, 238, 51, 9, 25, 76, 229, 238, 200, 208, 238, 150, 0, 19, 25, 24, 65, 173, 222, 194, 119, 2, 9, 24], [21, 21, 21, 46, 213, 238, 81, 21, 21, 21, 21, 21, 39, 205, 238, 238, 66, 15, 21, 21, 22, 35, 198, 233, 238, 238, 66, 15, 21, 21, 22, 57, 222, 87, 238, 238, 66, 15, 21, 21, 22, 22, 35, 2, 238, 238, 66, 15, 21, 21, 22, 22, 22, 20, 238, 238, 66, 15, 21, 21, 22, 22, 22, 22, 238, 238, 66, 15, 21, 21, 22, 22, 22, 22, 238, 238, 66, 15, 21, 21, 22, 22, 22, 22, 238, 238, 66, 15, 21, 21, 22, 22, 22, 24, 238, 238, 69, 15, 21, 21, 22, 22, 22, 45, 238, 238, 92, 15, 21, 21, 22, 22, 22, 138, 238, 238, 188, 23, 21, 21], [22, 23, 106, 188, 222, 219, 170, 60, 21, 22, 22, 156, 238, 223, 172, 224, 238, 224, 48, 22, 63, 238, 221, 12, 2, 39, 230, 238, 126, 19, 96, 238, 218, 22, 21, 22, 192, 238, 157, 10, 45, 237, 238, 99, 20, 22, 214, 238, 114, 7, 24, 91, 118, 0, 13, 86, 238, 225, 19, 11, 23, 23, 15, 12, 34, 209, 238, 97, 1, 19, 23, 23, 23, 24, 167, 238, 155, 0, 13, 22, 23, 23, 24, 136, 238, 189, 8, 8, 23, 21, 25, 25, 111, 238, 210, 21, 6, 24, 55, 44, 25, 92, 235, 238, 211, 190, 194, 209, 238, 30, 74, 231, 238, 238, 238, 238, 238, 238, 215, 0], [20, 184, 238, 238, 238, 238, 238, 238, 148, 21, 21, 217, 209, 194, 193, 212, 238, 191, 7, 9, 27, 70, 2, 2, 9, 194, 224, 33, 4, 19, 21, 20, 16, 21, 140, 238, 79, 1, 17, 20, 22, 22, 21, 78, 237, 146, 0, 14, 20, 21, 22, 22, 38, 216, 238, 235, 181, 65, 20, 20, 21, 22, 45, 96, 134, 218, 238, 233, 57, 20, 21, 22, 21, 19, 14, 32, 217, 238, 149, 16, 21, 49, 78, 22, 22, 22, 167, 238, 168, 8, 84, 225, 213, 29, 22, 31, 222, 238, 119, 6, 74, 233, 238, 217, 172, 212, 238, 204, 13, 10, 22, 61, 163, 217, 229, 199, 131, 17, 3, 20], [22, 21, 21, 21, 160, 238, 238, 132, 21, 21, 22, 22, 21, 58, 236, 238, 238, 122, 10, 21, 23, 22, 21, 172, 233, 188, 238, 122, 10, 21, 23, 22, 69, 238, 139, 160, 238, 122, 10, 21, 23, 22, 183, 229, 22, 163, 238, 122, 10, 22, 23, 82, 238, 130, 1, 166, 238, 122, 10, 21, 22, 194, 226, 17, 10, 167, 238, 122, 10, 21, 93, 238, 213, 160, 166, 215, 238, 200, 163, 23, 188, 238, 238, 238, 238, 238, 238, 238, 238, 10, 23, 5, 0, 0, 0, 160, 238, 122, 0, 0, 23, 23, 23, 22, 22, 179, 238, 132, 10, 21, 22, 22, 22, 22, 38, 223, 238, 194, 16, 22], [22, 65, 238, 238, 238, 238, 238, 238, 69, 19, 21, 86, 238, 218, 189, 189, 189, 189, 17, 16, 23, 106, 238, 119, 2, 5, 4, 4, 4, 19, 22, 127, 238, 95, 10, 22, 22, 21, 21, 21, 23, 147, 238, 195, 154, 129, 51, 21, 21, 21, 23, 168, 238, 238, 238, 238, 235, 133, 21, 21, 22, 22, 8, 19, 60, 172, 238, 238, 83, 21, 22, 23, 22, 22, 20, 20, 202, 238, 147, 14, 22, 59, 79, 22, 22, 23, 170, 238, 159, 8, 93, 229, 202, 29, 22, 34, 226, 238, 109, 7, 78, 233, 238, 217, 172, 215, 238, 198, 9, 11, 22, 61, 163, 213, 229, 200, 126, 15, 4, 20], [22, 21, 21, 26, 143, 228, 208, 142, 37, 21, 21, 21, 29, 189, 238, 217, 74, 3, 10, 19, 23, 22, 155, 238, 203, 22, 2, 15, 21, 21, 22, 79, 238, 221, 27, 3, 19, 21, 21, 21, 23, 171, 238, 136, 176, 226, 195, 96, 21, 21, 32, 235, 238, 228, 188, 212, 238, 238, 88, 21, 62, 238, 238, 108, 1, 10, 166, 238, 194, 14, 85, 238, 237, 19, 12, 22, 67, 238, 234, 7, 64, 238, 238, 17, 21, 23, 59, 238, 220, 0, 30, 221, 238, 128, 21, 23, 134, 238, 156, 2, 22, 110, 238, 238, 189, 177, 237, 220, 31, 7, 22, 22, 85, 182, 224, 207, 155, 25, 2, 18], [56, 238, 238, 238, 238, 238, 238, 238, 238, 73, 83, 228, 184, 174, 174, 174, 210, 238, 189, 0, 81, 37, 1, 5, 6, 6, 197, 238, 82, 4, 22, 16, 19, 22, 22, 82, 238, 210, 4, 13, 23, 22, 21, 21, 21, 179, 238, 106, 2, 21, 23, 23, 22, 22, 58, 238, 230, 16, 11, 21, 22, 23, 22, 22, 150, 238, 152, 1, 19, 21, 22, 23, 22, 34, 228, 238, 60, 8, 21, 20, 22, 22, 22, 113, 238, 213, 1, 16, 21, 21, 23, 23, 22, 201, 238, 152, 2, 22, 21, 21, 23, 23, 67, 238, 238, 112, 8, 22, 21, 21, 22, 22, 147, 238, 238, 91, 12, 22, 21, 21], [21, 21, 81, 182, 224, 221, 173, 66, 20, 21, 21, 97, 237, 227, 158, 192, 238, 228, 53, 20, 23, 201, 238, 83, 1, 9, 208, 238, 119, 18, 22, 228, 238, 67, 14, 21, 162, 238, 117, 10, 23, 166, 238, 177, 37, 69, 220, 221, 27, 11, 23, 38, 178, 238, 238, 238, 220, 43, 2, 19, 22, 53, 172, 238, 215, 231, 238, 211, 54, 21, 36, 219, 238, 81, 0, 17, 178, 238, 191, 17, 103, 238, 220, 0, 15, 23, 86, 238, 237, 9, 89, 238, 237, 55, 23, 23, 137, 238, 199, 0, 33, 204, 238, 232, 177, 196, 238, 235, 74, 3, 22, 40, 135, 206, 230, 213, 164, 52, 0, 15], [21, 21, 88, 181, 223, 209, 161, 42, 20, 21, 21, 113, 238, 222, 172, 221, 238, 219, 37, 20, 38, 227, 238, 37, 2, 27, 209, 238, 135, 19, 86, 238, 194, 0, 19, 21, 122, 238, 191, 9, 103, 238, 199, 4, 21, 21, 119, 238, 218, 4, 66, 238, 238, 75, 22, 25, 192, 238, 193, 2, 22, 177, 238, 234, 180, 203, 232, 238, 158, 4, 22, 32, 142, 210, 216, 141, 191, 238, 77, 7, 22, 22, 21, 9, 2, 96, 238, 211, 4, 14, 23, 23, 22, 23, 89, 235, 236, 63, 2, 21, 23, 23, 29, 137, 235, 238, 108, 0, 16, 21, 22, 70, 179, 218, 219, 71, 0, 12, 21, 21], [23, 22, 23, 23, 22, 22, 22, 22, 22, 22, 23, 23, 22, 22, 22, 22, 22, 22, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 23, 23, 22, 22, 22, 23, 23, 24, 24, 24, 23, 23, 22, 22, 22, 23, 23, 24, 24, 24, 24, 24, 23, 22, 22, 24, 24, 24, 24, 24, 24, 24, 24, 23, 22, 24, 24, 24, 24, 24, 24, 24, 24, 24, 23, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24]]

    def get_sample(self) -> Tuple[List[int], List[int], List[int]]:
        """ Returns the observed grayscale data of each digit from the screenshot taken """
        # Takes a screenshot of the in game creep score counter region 
        sample_im = ImageGrab.grab(bbox=(1920 - 138, 5, 1920 - 108, 25)).convert('L')
        
        # Crops the screenshot to 3 regions each representing one digit of 0-9 or blank
        return \
            list(sample_im.crop((0, 3, 10, 15)).getdata()), \
            list(sample_im.crop((10, 3, 20, 15)).getdata()), \
            list(sample_im.crop((20, 3, 30, 15)).getdata())

    def compute_mse(self, observed_data: List[int], predicted_data: List[int]) -> float:
        """ Returns the mean squared error (MSE) between the observed values and predicted values """
        mse: float = 0.0
        num_points: int = len(observed_data)

        for i in range(num_points):
            mse += math.pow(observed_data[i] - predicted_data[i], 2)
            
        return math.sqrt(mse / num_points)

    def most_similar_digit(self, digit_data: List[int]) -> str:
        """ Returns the most similar digit by finding a target digit with smallest MSE with the digit given """
        computed_mse: List[float] = [0.0] * len(self.target_digits)

        # Calcuate the MSE between the digit given and each of the possible target digits
        for i in range(len(self.target_digits)):
            computed_mse[i] = self.compute_mse(digit_data, self.target_digits[i])
        
        # Find the target digit with smallest MSE
        most_similar_digit = str(computed_mse.index(min(computed_mse)))
        
        return most_similar_digit if most_similar_digit != '10' else ''

class Overlay:
    """ Class to create and handle the Tkinter overlay """
    def __init__(self):
        self.root = tk.Tk()
        self.ocr = SimpleOCR()

        self.cs_per_minute_text = tk.StringVar()
        self.cs_per_minute_text.set("cs/min: 0.00")

        try:
            with open("font.cfg", "r") as f:
                self.font_size = int(f.read())
        except FileNotFoundError or ValueError:
            self.font_size = 11
    
    def set_attributes(self):
        """ Set the attributes of the overlay """
        self.root.wm_attributes("-fullscreen", True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.8)
        self.root.wm_attributes("-transparentcolor", "#f0f0f0")

    def build(self):
        """ Add the widgets to the overlay """
        frame = tk.Frame(width=160, height=60, pady=60, padx=10)
        frame.pack(side=tk.TOP, anchor=tk.NE)
        label = tk.Label(frame, textvariable=self.cs_per_minute_text, fg="white", font=("Terminal", self.font_size))
        label.pack()

    def update_counter(self):
        """ Updates the CS Per Minute counter text in the overlay """
        digit_1, digit_2, digit_3 = self.ocr.get_sample()
        total_cs: str = self.ocr.most_similar_digit(digit_1) + self.ocr.most_similar_digit(digit_2) + self.ocr.most_similar_digit(digit_3)

        try:
            # Fetch the game elapsed time in seconds from the game's LiveClientAPI
            game_time: float = requests.get("https://127.0.0.1:2999/liveclientdata/gamestats", verify=False).json()["gameTime"] / 60
            cs_per_min: float = int(total_cs) / game_time

            # Update the overlay text
            self.cs_per_minute_text.set("cs/min: " + format(cs_per_min, ".2f"))
        
        except Exception:
            # If failed to fetch game_time -> no game is in progress
            self.cs_per_minute_text.set("cs/min: 0.00")

        # Run again the next second
        self.root.after(1000, self.update_counter)

    def loop(self):
        """ Starts the Tkinter main loop """
        self.root.after(1000, self.update_counter)
        self.root.mainloop()

if __name__ == "__main__":
    overlay = Overlay()
    overlay.set_attributes()
    overlay.build()
    overlay.loop()