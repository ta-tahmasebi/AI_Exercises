import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from numpy.random import randint, shuffle


class SudokuGrid:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_cells = set()

    def clear(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_cells = set()

    def clear_non_initial(self):
        for i in range(9):
            for j in range(9):
                if (i, j) not in self.initial_cells:
                    self.grid[i][j] = 0

    def is_valid(self, row, col, num):
        if num in self.grid[row]:
            return False
        if num in [self.grid[i][col] for i in range(9)]:
            return False
        sub_r, sub_c = (row // 3) * 3, (col // 3) * 3
        return not any(self.grid[i][j] == num
                       for i in range(sub_r, sub_r + 3)
                       for j in range(sub_c, sub_c + 3))

    def is_valid_grid(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0:
                    num = self.grid[i][j]
                    self.grid[i][j] = 0
                    valid = self.is_valid(i, j, num)
                    self.grid[i][j] = num
                    if not valid:
                        return False
        return True


class SudokuSolver(ABC):
    def __init__(self, grid, update_callback):
        self.grid = grid
        self.update_callback = update_callback

    @abstractmethod
    def solve(self):
        pass


class BacktrackSolver(SudokuSolver):
    def solve(self):
        stack = []
        i = j = 0
        forward = True

        while i < 9:
            if j == 9:
                i, j = i + 1, 0
                continue
            if (i, j) in self.grid.initial_cells:
                j += 1
                continue

            if forward:
                current_val = self.grid.grid[i][j]
                nums = list(range(current_val + 1, 10)) if current_val != 0 else list(range(1, 10))
                valid_num = next((n for n in nums if self.grid.is_valid(i, j, n)), None)

                if valid_num is not None:
                    self.grid.grid[i][j] = valid_num
                    self.update_callback(i, j, valid_num, 'green')
                    stack.append((i, j))
                    j += 1
                    yield
                else:
                    self.grid.grid[i][j] = 0
                    self.update_callback(i, j, 0, 'red')
                    forward = False
                    yield
                    if stack:
                        i, j = stack.pop()
                        forward = True
                    else:
                        return
            else:
                self.grid.grid[i][j] = 0
                self.update_callback(i, j, 0, 'red')
                yield
                forward = True


class MVRSolver(SudokuSolver):
    def solve(self):
        empty = [(i, j) for i in range(9) for j in range(9) if self.grid.grid[i][j] == 0]
        stack = []

        while empty:
            mrv = min(empty, key=lambda cell: len(self.get_possible(*cell)))
            i, j = mrv

            possible = self.get_possible(i, j)
            if not possible:
                while stack:
                    back_i, back_j, back_val = stack.pop()
                    self.grid.grid[back_i][back_j] = 0
                    self.update_callback(back_i, back_j, 0, 'red')
                    yield

                    current_possible = self.get_possible(back_i, back_j)
                    remaining = [p for p in current_possible if p > back_val]

                    if remaining:
                        new_val = remaining[0]
                        self.grid.grid[back_i][back_j] = new_val
                        self.update_callback(back_i, back_j, new_val, 'green')
                        stack.append((back_i, back_j, new_val))
                        yield
                        break
                    else:
                        empty.append((back_i, back_j))
                else:
                    return
                continue

            chosen = possible[0]
            self.grid.grid[i][j] = chosen
            self.update_callback(i, j, chosen, 'green')
            stack.append((i, j, chosen))
            empty.remove((i, j))
            yield

    def get_possible(self, i, j):
        used = set(self.grid.grid[i]) | {self.grid.grid[x][j] for x in range(9)}
        sub_r, sub_c = (i // 3) * 3, (j // 3) * 3
        used |= {self.grid.grid[x][y] for x in range(sub_r, sub_r + 3) for y in range(sub_c, sub_c + 3)}
        return [n for n in range(1, 10) if n not in used]


class SudokuGUI:
    def __init__(self, root):
        self.solver = None
        self.clear_btn = None
        self.stop_btn = None
        self.solve_btn = None
        self.random_btn = None
        self.algorithm = None
        self.cells = None
        self.entries = None
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.geometry("1280x720")
        self.root.configure(bg='#2C3E50')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.grid = SudokuGrid()
        self.solving = False
        self.stop_solving = False
        self.delay = 50

        self.create_widgets()
        self.setup_controls()

    def create_widgets(self):
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.entries = [[None for _ in range(9)] for _ in range(9)]

        grid_frame = tk.Frame(self.root, bg='#34495E')
        grid_frame.place(relx=0.5, rely=0.45, anchor='center')

        for i in range(9):
            for j in range(9):
                frame = tk.Frame(grid_frame, bg='white', highlightbackground='#BDC3C7',
                                 highlightcolor='#BDC3C7', highlightthickness=1)
                frame.grid(row=i, column=j, padx=(7 if j % 3 == 0 else 2, 7 if j % 3 == 2 else 2),
                           pady=(7 if i % 3 == 0 else 2, 7 if i % 3 == 2 else 2))

                entry = tk.Entry(frame, width=2, font=('Arial', 16, 'bold'), justify='center',
                                 highlightthickness=0, bd=0, fg='#2C3E50')
                entry.pack()
                entry.bind('<KeyRelease>', lambda e, i=i, j=j: self.validate_input(i, j))

                self.cells[i][j] = frame
                self.entries[i][j] = entry

    def setup_controls(self):
        control_frame = tk.Frame(self.root, bg='#2C3E50')
        control_frame.place(relx=0.5, rely=0.85, anchor='center')

        self.algorithm = tk.StringVar(value='backtrack')
        algo_menu = ttk.Combobox(control_frame, textvariable=self.algorithm,
                                 values=['backtrack', 'mvr'], state='readonly', font=('Arial', 10))
        algo_menu.grid(row=0, column=0, padx=5, pady=5)

        button_styles = {
            'font': ('Arial', 10, 'bold'),
            'fg': 'white',
            'width': 8,
            'height': 1,
            'borderwidth': 1,
            'relief': 'flat',
            'highlightbackground': '#34495E',
            'highlightthickness': 1
        }

        controls = [
            ('Random', self.generate_random, '#2980B9'),
            ('Solve', self.start_solving, '#27AE60'),
            ('Clear', self.clear_grid, '#C0392B'),
            ('Stop', self.stop_solving_process, '#F39C12')
        ]

        for idx, (text, cmd, color) in enumerate(controls, 1):
            btn = tk.Button(control_frame, text=text, command=cmd, bg=color, **button_styles)
            btn.grid(row=0, column=idx, padx=3, pady=5)
            attr_name = f"{text.lower().replace(' ', '_')}_btn"
            setattr(self, attr_name, btn)

        self.toggle_controls(True)

    def toggle_controls(self, enable=True):
        state = 'normal' if enable else 'disabled'
        for btn in [self.random_btn, self.solve_btn, self.clear_btn]:
            btn['state'] = state
        self.stop_btn['state'] = 'disabled' if enable else 'normal'

    def validate_input(self, i, j):
        if self.solving:
            return
        entry = self.entries[i][j]
        val = entry.get()
        if not val.isdigit() or int(val) not in range(1, 10):
            entry.delete(0, tk.END)
            entry.insert(0, val[:-1] if val and val[:-1].isdigit() else '')

    def update_cell(self, i, j, value, color):
        self.cells[i][j].config(highlightbackground=color, highlightcolor=color, highlightthickness=2)
        self.entries[i][j].delete(0, tk.END)
        if value != 0:
            self.entries[i][j].insert(0, str(value))
        self.entries[i][j].config(fg='grey' if (i, j) in self.grid.initial_cells else 'black')

    def start_solving(self):
        if self.solving:
            return
        self.grid.clear()
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if val.isdigit() and val != '0':
                    self.grid.grid[i][j] = int(val)
                    self.grid.initial_cells.add((i, j))

        if not self.grid.is_valid_grid():
            messagebox.showerror("Invalid Puzzle", "The initial puzzle contains conflicts!")
            return

        self.solving = True
        self.stop_solving = False
        self.toggle_controls(False)

        for i, j in self.grid.initial_cells:
            self.entries[i][j].config(state='readonly', fg='grey')

        solver_class = BacktrackSolver if self.algorithm.get() == 'backtrack' else MVRSolver
        self.solver = solver_class(self.grid, self.update_cell).solve()
        self.root.after(self.delay, self.next_step)

    def next_step(self):
        if self.stop_solving:
            self.cleanup_solving()
            return

        try:
            next(self.solver)
            self.root.after(self.delay, self.next_step)
        except StopIteration:
            self.cleanup_solving()
            self.show_solution_status()

    def show_solution_status(self):
        solved = all(0 not in row for row in self.grid.grid)
        if solved:
            messagebox.showinfo("Solution Found", "Puzzle solved successfully!")
        else:
            messagebox.showwarning("No Solution", "No valid solution exists for this puzzle!")

    def cleanup_solving(self):
        self.solving = False
        self.toggle_controls(True)
        for i, j in self.grid.initial_cells:
            self.entries[i][j].config(state='readonly')

    def stop_solving_process(self):
        self.stop_solving = True
        self.show_solution_status()

    def clear_grid(self):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].config(state='normal', fg='black')
                self.cells[i][j].config(highlightbackground='#BDC3C7', highlightcolor='#BDC3C7')
        self.grid.clear()

    def clear_non_initial(self):
        for i in range(9):
            for j in range(9):
                if (i, j) not in self.grid.initial_cells:
                    self.entries[i][j].delete(0, tk.END)
                    self.cells[i][j].config(highlightbackground='#BDC3C7', highlightcolor='#BDC3C7')

    def generate_random(self):
        def valid(board, pos, num):
            for r in range(9):
                if board[r][pos[1]] == num:
                    return False
            for c in range(9):
                if board[pos[0]][c] == num:
                    return False
            start_i = pos[0] - pos[0] % 3
            start_j = pos[1] - pos[1] % 3
            for r in range(3):
                for c in range(3):
                    if board[start_i + r][start_j + c] == num:
                        return False
            return True

        def generate_board():
            board = [[0 for _ in range(9)] for _ in range(9)]
            for k in range(0, 9, 3):
                nums = list(range(1, 10))
                shuffle(nums)
                for row in range(3):
                    for col in range(3):
                        board[k + row][k + col] = nums.pop()

            def fill_cells(grid, r, c):
                if r == 9:
                    return True
                if c == 9:
                    return fill_cells(grid, r + 1, 0)
                if grid[r][c] != 0:
                    return fill_cells(grid, r, c + 1)
                for num in range(1, 10):
                    if valid(grid, (r, c), num):
                        grid[r][c] = num
                        if fill_cells(grid, r, c + 1):
                            return True
                grid[r][c] = 0
                return False

            fill_cells(board, 0, 0)
            for _ in range(randint(60, 80)):
                row, col = randint(0, 9), randint(0, 9)
                board[row][col] = 0

            return board

        self.clear_grid()
        self.grid.grid = generate_board()

        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                if self.grid.grid[i][j] != 0:
                    self.entries[i][j].insert(0, str(self.grid.grid[i][j]))
                self.grid.initial_cells.add((i, j))
                self.entries[i][j].config(fg='black')


if __name__ == "__main__":
    main_root = tk.Tk()
    app = SudokuGUI(main_root)
    main_root.mainloop()
