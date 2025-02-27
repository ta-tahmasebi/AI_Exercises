import tkinter as tk
import random
import string


class PasswordGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Guessing Game")
        self.root.geometry("600x550")
        self.root.configure(bg="#2c3e50")

        self.play_again_button = tk.Button(root, text="Play Again", font=("Arial", 10, "bold"), bg="#e74c3c", fg="white",
                                           command=self.reset_game)
        self.play_again_button.place(x=500, y=10)

        self.initialize_game()

    def initialize_game(self):
        self.password = ''.join(random.choices(string.ascii_lowercase, k=6))
        print(self.password)  # Debugging
        self.best_guess = 0
        self.submission_count = 0
        self.auto_running = False

        self.custom_font = ("Arial", 12)

        # Header
        tk.Label(self.root, text="Guess the 6-character password:", font=("Arial", 14, "bold"),
                 bg="#2c3e50", fg="white").pack(pady=20)

        # Frames for layout
        self.main_frame = tk.Frame(self.root, bg="#2c3e50")
        self.main_frame.pack()

        self.guess_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.guess_frame.pack(side=tk.LEFT, padx=20)

        self.entries, self.results = [], []
        for _ in range(7):
            frame = tk.Frame(self.guess_frame, bg="#2c3e50")
            frame.pack(pady=5)

            entry = tk.Entry(frame, font=self.custom_font, width=10, bg="#ecf0f1", fg="#2c3e50", bd=2, relief=tk.FLAT)
            entry.pack(side=tk.LEFT, padx=5)
            self.entries.append(entry)

            result_label = tk.Label(frame, text="", font=self.custom_font, bg="#2c3e50", fg="white")
            result_label.pack(side=tk.LEFT, padx=10)
            self.results.append(result_label)

        # Progress Bar
        self.bar_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.bar_frame.pack(side=tk.LEFT, padx=20)

        self.bar_canvas = tk.Canvas(self.bar_frame, width=30, height=300, bg="#34495e", highlightthickness=0)
        self.bar_canvas.pack()
        self.bar = self.bar_canvas.create_rectangle(5, 300, 25, 300, fill="#e74c3c", outline="")

        self.submission_label = tk.Label(self.bar_frame, text="Submissions: 0", font=self.custom_font, bg="#2c3e50", fg="white")
        self.submission_label.pack(pady=10)

        # Buttons
        self.submit_frame = tk.Frame(self.root, bg="#2c3e50")
        self.submit_frame.pack(pady=10)

        self.submit_button = tk.Button(self.submit_frame, text="Submit", font=("Arial", 12, "bold"), bg="#2ecc71",
                                       fg="white", bd=0, activebackground="#27ae60", command=self.submit)
        self.submit_button.pack(side=tk.LEFT, padx=10)

        self.next_population_button = tk.Button(self.submit_frame , text="Generate", font=("Arial", 12, "bold"), bg="#2ecc71",
                                       fg="white", bd=0, activebackground="#27ae60", command=self.genetic_algorithm)
        self.next_population_button.pack(side=tk.LEFT, padx=10)

        self.auto_var = tk.BooleanVar()
        self.auto_check = tk.Checkbutton(self.submit_frame, text="Auto", font=self.custom_font, bg="#2c3e50",
                                         fg="white", selectcolor="#2c3e50", variable=self.auto_var, command=self.toggle_auto)
        self.auto_check.pack(side=tk.LEFT)

        # Mutation Rate Slider
        self.mutation_rate_slider = tk.Scale(self.root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                             label="Mutation Rate", font=self.custom_font, length=300, bg="#34495e",
                                             fg="white", troughcolor="#2ecc71", sliderlength=20,
                                             command=self.update_mutation_label)
        self.mutation_rate_slider.pack(pady=10)

        self.mutation_label = tk.Label(self.root, text=f"Mutation Rate: {self.mutation_rate_slider.get():.2f}",
                                       font=self.custom_font, bg="#2c3e50", fg="white")
        self.mutation_label.pack(pady=10)

        self.excellent_label = tk.Label(self.root, text="", font=("Arial", 16, "bold"), bg="#2c3e50", fg="#2ecc71")
        self.excellent_label.pack(pady=10)
        
        self.random_population()

    def submit(self):
        self.check_guesses()
        if self.auto_running:
            self.genetic_algorithm()
        if self.auto_running:
            self.root.after(40, self.submit)  # Auto-submit every 0.04 sec

    def check_guesses(self):
        self.submission_label.config(text=f"Submissions: {self.submission_count}")
        self.excellent_label.config(text="")

        for i, entry in enumerate(self.entries):
            guess = entry.get().strip()
            if len(guess) != 6:
                self.results[i].config(text="Invalid", fg="#e74c3c")
                continue

            correct = sum(1 for j in range(6) if guess[j] == self.password[j])
            self.results[i].config(text=f"{correct}/6", fg="white")

            if correct > self.best_guess:
                self.best_guess = correct
                self.update_bar()

            if guess == self.password:
                self.excellent_label.config(text="Excellent!", fg="#2ecc71")
                self.submit_button.config(state=tk.DISABLED)
                self.auto_running = False
                return

    def random_population(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
            entry.insert(0, ''.join(random.choices(string.ascii_lowercase, k=6)))

    def genetic_algorithm(self):
        population = [entry.get().strip() for entry in self.entries]
        fitness = [int(result.cget("text").split('/')[0]) for result in self.results]
        if all(fit == 0 for fit in fitness):
            self.random_population()
            return
        
        def select_parent():
            pick = max(fitness)
            parent = population[fitness.index(pick)]
            fitness[fitness.index(pick)] = 0
            return parent, pick

        new_population = []
        parent1, fit1 = select_parent()
        parent2, fit2 = select_parent()

        for _ in range(7):
            s = ""
            for i in range(6):
                if random.random() < fit1 / (fit1 + fit2):
                    s += parent1[i]
                else:
                    s += parent2[i]
            new_population.append(s)

        mutation_rate = self.mutation_rate_slider.get()
        for i in range(len(new_population)):
            if random.random() < mutation_rate:
                mutate_point = random.randint(0, 5)
                new_population[i] = new_population[i][:mutate_point] + random.choice(string.ascii_lowercase) + new_population[i][mutate_point + 1:]

        for entry, new_individual in zip(self.entries, new_population):
            entry.delete(0, tk.END)
            entry.insert(0, new_individual)

    def update_bar(self):
        bar_height = (self.best_guess / 6) * 300
        self.bar_canvas.coords(self.bar, 5, 300 - bar_height, 25, 300)

        red, green = int(255 * (1 - self.best_guess / 6)), int(255 * (self.best_guess / 6))
        self.bar_canvas.itemconfig(self.bar, fill=f"#{red:02x}{green:02x}00")

    def update_mutation_label(self, _=None):
        self.mutation_label.config(text=f"Mutation Rate: {self.mutation_rate_slider.get():.2f}")

    def toggle_auto(self):
        self.auto_running = self.auto_var.get()
        if self.auto_running:
            self.submit()

    def reset_game(self):
        self.root.destroy()  # Close the current window
        root = tk.Tk()  # Create a new instance
        PasswordGame(root)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    game = PasswordGame(root)
    root.mainloop()