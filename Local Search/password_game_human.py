import tkinter as tk
from tkinter import messagebox
import random
import string

class PasswordGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Guessing Game")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")  # Dark blue background

        # Generate a random 6-character password
        self.password = ''.join(random.choices(string.ascii_lowercase, k=6))
        print(self.password)
        self.best_guess = 0  # Track the best guess number

        # Custom font
        self.custom_font = ("Arial", 12)

        # GUI Elements
        self.label = tk.Label(
            root,
            text="Guess the 6-character password:",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.label.pack(pady=20)

        # Frame for guesses and vertical bar
        self.main_frame = tk.Frame(root, bg="#2c3e50")
        self.main_frame.pack()

        # Frame for guesses
        self.guess_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.guess_frame.pack(side=tk.LEFT, padx=20)

        self.entries = []
        self.results = []
        for i in range(7):
            frame = tk.Frame(self.guess_frame, bg="#2c3e50")
            frame.pack(pady=5)

            # Normal rectangle for text box
            entry = tk.Entry(
                frame,
                font=self.custom_font,
                width=10,
                bg="#ecf0f1",
                fg="#2c3e50",
                bd=2,
                relief=tk.FLAT
            )
            entry.pack(side=tk.LEFT, padx=5)

            self.entries.append(entry)

            result_label = tk.Label(
                frame,
                text="",
                font=self.custom_font,
                bg="#2c3e50",
                fg="white"
            )
            result_label.pack(side=tk.LEFT, padx=10)
            self.results.append(result_label)

        # Frame for vertical bar
        self.bar_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.bar_frame.pack(side=tk.LEFT, padx=20)

        # Vertical bar (initially empty)
        self.bar_canvas = tk.Canvas(self.bar_frame, width=30, height=300, bg="#34495e", highlightthickness=0)
        self.bar_canvas.pack()
        self.bar = self.bar_canvas.create_rectangle(5, 300, 25, 300, fill="#e74c3c", outline="")  # Initial height is 0

        # Submit button
        self.submit_button = tk.Button(
            root,
            text="Submit",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            bd=0,
            activebackground="#27ae60",
            activeforeground="white",
            command=self.check_guesses
        )
        self.submit_button.pack(pady=20)

        # Excellent label
        self.excellent_label = tk.Label(
            root,
            text="",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="#2ecc71"
        )
        self.excellent_label.pack(pady=10)

    def check_guesses(self):
        # Reset the excellent label
        self.excellent_label.config(text="")

        # Check each guess
        for i in range(7):
            guess = self.entries[i].get().strip()
            if len(guess) != 6:
                self.results[i].config(text="Invalid", fg="#e74c3c")
                continue

            # Count correct characters in the correct position
            correct = 0
            for j in range(6):
                if guess[j] == self.password[j]:
                    correct += 1

            self.results[i].config(text=f"{correct}/6", fg="white")

            # Update the best guess
            if correct > self.best_guess:
                self.best_guess = correct
                self.update_bar()

            # Check if the guess is correct
            if guess == self.password:
                self.excellent_label.config(text="Excellent!", fg="#2ecc71")
                self.submit_button.config(state=tk.DISABLED)
                return

    def update_bar(self):
        # Calculate the height of the bar based on the best guess
        bar_height = (self.best_guess / 6) * 300  # Scale to canvas height
        self.bar_canvas.coords(self.bar, 5, 300 - bar_height, 25, 300)

        # Calculate the color based on the best guess (red to green)
        red = int(255 * (1 - self.best_guess / 6))
        green = int(255 * (self.best_guess / 6))
        color = f"#{red:02x}{green:02x}00"  # RGB format (no blue component)
        self.bar_canvas.itemconfig(self.bar, fill=color)

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = PasswordGame(root)
    root.mainloop()