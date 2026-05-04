import tkinter as tk
from weather_diary import WeatherDiary

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()