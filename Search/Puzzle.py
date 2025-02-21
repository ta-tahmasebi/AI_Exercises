import math
import random
import tkinter as tk
from itertools import chain
from collections import deque
from tkinter import messagebox, ttk


class PuzzleSolver:
    DIRECTIONS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    SHUFFLE_FACTOR = 50

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.total_tiles = rows * cols
        self.GOAL = self._create_goal_state()

    def _create_goal_state(self):
        nums = list(range(1, self.total_tiles)) + [0]
        return tuple(
            tuple(nums[i * self.cols:(i + 1) * self.cols])
            for i in range(self.rows)
        )

    def get_neighbors(self, state):
        try:
            blank = next((i, j) for i, row in enumerate(state)
                         for j, val in enumerate(row) if val == 0)
        except StopIteration:
            raise ValueError("Invalid state - no blank tile (0) found")

        neighbors = []
        for move, (di, dj) in self.DIRECTIONS.items():
            new_i, new_j = blank[0] + di, blank[1] + dj
            if 0 <= new_i < self.rows and 0 <= new_j < self.cols:
                new_state = [list(row) for row in state]
                new_state[blank[0]][blank[1]], new_state[new_i][new_j] = \
                    new_state[new_i][new_j], new_state[blank[0]][blank[1]]
                neighbors.append((tuple(map(tuple, new_state)), move))
        return neighbors

    def _solve(self, initial, ds_type):
        if initial == self.GOAL:
            return []

        visited = {initial}
        parent = {initial: (None, None)}
        ds = deque([initial]) if ds_type == 'bfs' else [initial]

        while ds:
            current = ds.popleft() if ds_type == 'bfs' else ds.pop()
            for neighbor, move in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = (current, move)
                    if neighbor == self.GOAL:
                        path = []
                        while neighbor in parent:
                            neighbor, move = parent[neighbor]
                            if move: path.append(move)
                        return path[::-1]
                    ds.append(neighbor)
        return None

    def solve_bfs(self, initial):
        return self._solve(initial, 'bfs')

    def solve_dfs(self, initial):
        return self._solve(initial, 'dfs')

    def generate_random_state(self):
        state = self.GOAL
        for _ in range(self.SHUFFLE_FACTOR * max(self.rows, self.cols)):
            neighbors = self.get_neighbors(state)
            state, _ = random.choice(neighbors)
        return state


class PuzzleApp(tk.Tk):
    COLORS = {
        'bg': "#2C3E50",
        'tile': "#1ABC9C",
        'text': "#ECF0F1",
        'button': {"solve": "#1ABC9C", "random": "#3498DB", "stop": "#E74C3C"}
    }
    MAX_TILE_SIZE = 80
    MIN_TILE_SIZE = 40

    def __init__(self, rows=3, cols=3):
        super().__init__()
        self.is_solving = None
        self.current_state = None
        self.solution = None
        self.rows = rows
        self.cols = cols
        self.solver = PuzzleSolver(rows, cols)
        self._configure_window()
        self._init_ui()

    def _configure_window(self):
        width_tiles = self.cols
        height_tiles = self.rows
        self.tile_size = min(
            self.MAX_TILE_SIZE,
            max(self.MIN_TILE_SIZE,
                math.floor(800 / max(width_tiles, height_tiles))
                ))

        self.geometry("1280x720")
        self.title(f"{self.rows}x{self.cols} Puzzle Solver")
        self.configure(bg=self.COLORS['bg'])

    def _init_ui(self):
        self.solution = None
        self.current_state = None
        self.is_solving = False
        self._create_input_grid()
        self._create_controls()
        self._create_canvas()
        self._create_status_label()

    def _create_input_grid(self):
        frame = tk.Frame(self, bg=self.COLORS['bg'])
        frame.pack(pady=10)
        self.entries = [
            [self._create_entry(frame, i, j)
             for j in range(self.cols)]
            for i in range(self.rows)
        ]

    def _create_entry(self, parent, row, col):
        entry = tk.Entry(parent, width=2,
                         font=('Helvetica', self._calculate_font_size()),
                         justify='center', bg="#ECF0F1", fg=self.COLORS['bg'])
        entry.grid(row=row, column=col, padx=2, pady=2)
        return entry

    def _calculate_font_size(self):
        base_size = min(24, math.floor(self.tile_size * 0.3))
        return max(12, base_size)

    def _create_controls(self):
        frame = tk.Frame(self, bg=self.COLORS['bg'])
        frame.pack(pady=10)

        self.solve_btn = self._create_button(frame, "Solve", self.solve_puzzle, "solve", 0, 0)
        self.random_btn = self._create_button(frame, "Random", self.fill_random, "random", 0, 1)
        self.stop_btn = self._create_button(frame, "Stop", self.stop_solving, "stop", 0, 2)

        tk.Label(frame, text="Algorithm:", bg=self.COLORS['bg'], fg=self.COLORS['text'],
                 font=('Helvetica', 12)).grid(row=1, column=0, pady=5)

        self.algorithm = ttk.Combobox(frame, values=["BFS", "DFS"], state="readonly")
        self.algorithm.set("BFS")
        self.algorithm.grid(row=1, column=1, columnspan=2, pady=5)

    def _create_button(self, parent, text, command, color_key, row, col):
        btn = tk.Button(parent, text=text, command=command,
                        bg=self.COLORS['button'][color_key], fg=self.COLORS['text'],
                        font=('Helvetica', 12, 'bold'))
        btn.grid(row=row, column=col, padx=5)
        return btn

    def _create_canvas(self):
        self.canvas = tk.Canvas(self, width=self.tile_size * self.cols,
                                height=self.tile_size * self.rows,
                                bg="#34495E", highlightthickness=0)
        self.canvas.pack(pady=10)

    def _create_status_label(self):
        self.status = tk.Label(self, text="Steps: ---", bg=self.COLORS['bg'],
                               fg=self.COLORS['text'], font=('Helvetica', 12))
        self.status.pack()

    def fill_random(self):
        state = self.solver.generate_random_state()
        for i, row in enumerate(state):
            for j, val in enumerate(row):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, val)

    def solve_puzzle(self):
        try:
            initial = tuple(
                tuple(int(self.entries[i][j].get())
                      for j in range(self.cols))
                for i in range(self.rows)
            )
            all_numbers = set(chain.from_iterable(initial))
            expected_numbers = set(range(self.rows * self.cols))
            if all_numbers != expected_numbers:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error",
                                 f"Use numbers 0-{self.rows * self.cols - 1} exactly once")
            return

        self._toggle_controls(False)
        solver = self.solver.solve_bfs if self.algorithm.get() == "BFS" else self.solver.solve_dfs
        self.solution = solver(initial)

        if self.solution is None:
            messagebox.showinfo("No Solution", "Puzzle cannot be solved")
            self._toggle_controls(True)
            return

        self.status.config(text=f"Steps: {len(self.solution)}")
        self.current_state, self.is_solving = initial, True
        self.draw_state(initial)
        self.after(1000, self._animate)

    def _animate(self):
        if not self.is_solving or not self.solution:
            return self._toggle_controls(True)

        move = self.solution.pop(0)
        blank = next(
            (i, j) for i, row in enumerate(self.current_state)
            for j, val in enumerate(row) if val == 0
        )
        di, dj = self.solver.DIRECTIONS[move]
        i, j = blank[0] + di, blank[1] + dj

        new_state = [list(row) for row in self.current_state]
        new_state[blank[0]][blank[1]], new_state[i][j] = new_state[i][j], new_state[blank[0]][blank[1]]
        self.current_state = tuple(map(tuple, new_state))

        self.draw_state(self.current_state)
        self.after(500 if self.algorithm.get() == "BFS" else 5, self._animate)

    def draw_state(self, state):
        self.canvas.delete("all")
        ts_w = self.tile_size
        ts_h = self.tile_size

        for i, row in enumerate(state):
            for j, num in enumerate(row):
                if num == 0:
                    continue
                x = j * ts_w
                y = i * ts_h
                self.canvas.create_rectangle(
                    x, y, x + ts_w, y + ts_h,
                    fill=self.COLORS['tile'], outline="#ECF0F1"
                )
                font_size = self._calculate_font_size()
                self.canvas.create_text(
                    x + ts_w // 2, y + ts_h // 2,
                    text=str(num),
                    font=("Helvetica", font_size, "bold"),
                    fill="#ECF0F1"
                )

    def _toggle_controls(self, enable):
        normal_state = tk.NORMAL if enable else tk.DISABLED
        stop_state = tk.NORMAL if not enable else tk.DISABLED

        for row in self.entries:
            for entry in row:
                entry.config(state=normal_state)
        self.solve_btn.config(state=normal_state)
        self.random_btn.config(state=normal_state)
        self.algorithm.config(state=normal_state)
        self.stop_btn.config(state=stop_state)
        self.is_solving = not enable

    def stop_solving(self):
        self.is_solving = False
        self._toggle_controls(True)


if __name__ == "__main__":
    PuzzleApp(rows=3, cols=3).mainloop()
