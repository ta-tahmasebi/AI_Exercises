import heapq
import random
import tkinter as tk
from tkinter import ttk
from collections import deque
import tkinter.messagebox as messagebox


class PathFinder:
    def __init__(self, grid, start, end, obstacle_color):
        self.grid = grid
        self.start = start
        self.end = end
        self.obstacle_color = obstacle_color
        self.n = len(grid)
        self.m = len(grid[0]) if self.n > 0 else 0

    def bfs_generator(self):
        queue = deque([[self.start]])
        visited = {self.start}
        while queue:
            path = queue.popleft()
            current = path[-1]
            yield path, current, visited.copy()
            if current == self.end:
                return path
            for neighbor in self.get_valid_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def dfs_generator(self):
        stack = [[self.start]]
        visited = {self.start}
        while stack:
            path = stack.pop()
            current = path[-1]
            yield path, current, visited.copy()
            if current == self.end:
                return path
            for neighbor in reversed(self.get_valid_neighbors(current)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(path + [neighbor])
        return None

    def heuristic(self, node):
        return abs(node[0] - self.end[0]) + abs(node[1] - self.end[1])

    def a_star_generator(self):
        pq = []
        heapq.heappush(pq, (0 + self.heuristic(self.start), 0, [self.start]))  # (f, g, path)
        visited = {}

        while pq:
            f, g, path = heapq.heappop(pq)
            current = path[-1]
            yield path, current, visited.copy()

            if current == self.end:
                return path

            for neighbor in self.get_valid_neighbors(current):
                new_g = g + 1
                if neighbor not in visited or new_g < visited[neighbor]:
                    visited[neighbor] = new_g
                    f_new = new_g + self.heuristic(neighbor)
                    heapq.heappush(pq, (f_new, new_g, path + [neighbor]))

        return None

    def get_valid_neighbors(self, pos):
        i, j = pos
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            x, y = i + dx, j + dy
            if 0 <= x < self.n and 0 <= y < self.m:
                if self.grid[x][y] != self.obstacle_color:
                    neighbors.append((x, y))
        return neighbors


# noinspection PyTypeChecker
class GridUI:
    def __init__(self, root):
        self.dfs_rb = None
        self.solve_btn = None
        self.clear_path_btn = None
        self.stop_btn = None
        self.algo_var = None
        self.random_btn = None
        self.bfs_rb = None
        self.a_star_rb = None
        self.clear_btn = None
        self.generate_btn = None
        self.m_entry = None
        self.n_entry = None
        self.obstacle_scale = None
        self.visited_toggle = None
        self.info_panel = None
        self.root = root
        self.root.title("Pathfinding Visualizer")
        self.root.geometry("1280x720")
        self.root.configure(bg='#2C3E50')

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.bg_color = '#2C3E50'
        self.button_bg = '#0984e3'
        self.button_fg = 'white'
        self.active_bg = '#0767b2'
        self.cell_color = '#dfe6e9'
        self.obstacle_color = '#2d3436'

        self.header_font = ('Arial', 12, 'bold')
        self.text_font = ('Arial', 10)

        self.pathfinder = None
        self.n = 0
        self.m = 0
        self.source_pos = None
        self.dest_pos = None
        self.cells = []
        self.algorithm = "BFS"
        self.searching = False
        self.step_delay = 5
        self.states_explored = 0
        self.stopped = False
        self.after_id = None
        self.show_visited = tk.BooleanVar(value=True)
        self.color_cycle = [self.cell_color, self.obstacle_color, '#ff7675', '#fd79a8']

        self.create_controls()
        self.create_info_panel()
        self.grid_frame = tk.Frame(self.root, bg=self.bg_color)
        self.grid_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.update_button_states()

    def create_controls(self):
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(pady=15)

        ttk.Label(control_frame, text="Rows:", background=self.bg_color,
                  font=self.text_font, foreground='white').grid(row=0, column=0, padx=5)
        self.n_entry = ttk.Entry(control_frame, width=5, font=self.text_font)
        self.n_entry.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="Columns:", background=self.bg_color,
                  font=self.text_font, foreground='white').grid(row=0, column=2, padx=5)
        self.m_entry = ttk.Entry(control_frame, width=5, font=self.text_font)
        self.m_entry.grid(row=0, column=3, padx=5)

        button_style = {
            'bg': self.button_bg,
            'fg': self.button_fg,
            'activebackground': self.active_bg,
            'font': self.text_font,
            'border': 0,
            'relief': 'flat',
            'padx': 15,
            'pady': 8
        }

        self.generate_btn = tk.Button(control_frame, text="Generate Grid", **button_style, command=self.generate_grid)
        self.generate_btn.grid(row=0, column=4, padx=5)

        self.clear_btn = tk.Button(control_frame, text="Clear All", **button_style, command=self.clear_grid)
        self.clear_btn.grid(row=0, column=5, padx=5)

        self.random_btn = tk.Button(control_frame, text="Randomize", **button_style, command=self.randomize_grid)
        self.random_btn.grid(row=0, column=6, padx=5)

        self.algo_var = tk.StringVar(value="BFS")
        radio_style = {'bg': self.bg_color, 'fg': 'white', 'font': self.text_font,
                       'selectcolor': self.button_bg, 'activebackground': self.bg_color}

        self.bfs_rb = tk.Radiobutton(control_frame, text="BFS", variable=self.algo_var,
                                     value="BFS", **radio_style)
        self.bfs_rb.grid(row=0, column=7, padx=5)
        self.dfs_rb = tk.Radiobutton(control_frame, text="DFS", variable=self.algo_var,
                                     value="DFS", **radio_style)
        self.dfs_rb.grid(row=0, column=8, padx=5)
        self.a_star_rb = tk.Radiobutton(control_frame, text="A*", variable=self.algo_var,
                                        value="A*", **radio_style)

        self.a_star_rb.grid(row=0, column=9, padx=5)

        action_style = {**button_style, 'bg': '#00b894', 'activebackground': '#00997b'}
        self.solve_btn = tk.Button(control_frame, text="Solve", **action_style, command=self.start_solving)
        self.solve_btn.grid(row=0, column=10, padx=5)

        self.stop_btn = tk.Button(control_frame, text="Stop",
                                  **{**button_style, 'bg': '#d63031', 'activebackground': '#b02323'},
                                  command=self.stop_animation, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=11, padx=5)

        self.clear_path_btn = tk.Button(control_frame, text="Clear Path", **button_style, command=self.clear_path)
        self.clear_path_btn.grid(row=0, column=12, padx=5)

        self.visited_toggle = tk.Checkbutton(
            control_frame, text="Show Visited",
            variable=self.show_visited,
            command=self.toggle_visited_display,
            bg=self.bg_color,
            fg='white',
            font=self.text_font,
            activebackground=self.bg_color,
            selectcolor=self.button_bg
        )
        self.visited_toggle.grid(row=0, column=13, padx=5)

        self.obstacle_scale = ttk.Scale(control_frame, from_=1, to=60, orient='horizontal',
                                        style='Custom.Horizontal.TScale')
        self.obstacle_scale.set(30)
        self.obstacle_scale.grid(row=0, column=14, padx=10)

        self.style.configure('Custom.Horizontal.TScale',
                             background=self.bg_color,
                             troughcolor='#636e72',
                             sliderthickness=15,
                             gripcount=0)

    def create_info_panel(self):
        self.info_panel = tk.Label(self.root, text="States Explored: 0", font=self.text_font,
                                   bg=self.bg_color, fg='white')
        self.info_panel.pack(side='bottom', pady=5)

    def generate_grid(self):
        try:
            new_n = int(self.n_entry.get())
            new_m = int(self.m_entry.get())
            if new_n <= 0 or new_m <= 0:
                raise ValueError
            if new_n > 50 or new_m > 50:
                messagebox.showwarning("Large Grid", "Grid dimensions over 50 may cause performance issues!")
                return
            self.n = new_n
            self.m = new_m
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter positive integer values for grid dimensions")
            return

        self.reset_grid()
        if hasattr(self, 'grid_frame') and self.grid_frame:
            self.grid_frame.destroy()
        self.grid_frame = tk.Frame(self.root, bg=self.bg_color)
        self.grid_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_cells()
        self.configure_grid_layout()

    def configure_grid_layout(self):
        for i in range(self.n):
            self.grid_frame.rowconfigure(i, weight=1)
        for j in range(self.m):
            self.grid_frame.columnconfigure(j, weight=1)
        self.grid_frame.pack_propagate(False)

    def create_cells(self):
        for i in range(self.n):
            row = []
            for j in range(self.m):
                btn = tk.Button(self.grid_frame,
                                bg=self.cell_color,
                                relief='flat',
                                activebackground='#b2bec3',
                                borderwidth=0.5,
                                highlightthickness=0,
                                command=lambda i=i, j=j: self.select_cells(i, j))
                btn.grid(row=i, column=j, sticky='nsew', padx=1, pady=1)
                row.append({'button': btn, 'color': self.cell_color, 'original': self.cell_color})
            self.cells.append(row)

    def select_cells(self, i, j):
        if not self.searching:
            if self.source_pos is None:
                self.source_pos = (i, j)
                self.set_color(i, j, '#0984e3')
            elif self.dest_pos is None and (i, j) != self.source_pos:
                self.dest_pos = (i, j)
                self.set_color(i, j, '#00b894')
            elif (i, j) not in [self.source_pos, self.dest_pos]:
                current_color = self.cells[i][j]['color']
                if current_color in ['#0984e3', '#00b894']:
                    return
                try:
                    next_idx = (self.color_cycle.index(current_color) + 1) % len(self.color_cycle)
                except ValueError:
                    next_idx = 0
                new_color = self.color_cycle[next_idx]
                self.set_color(i, j, new_color)

    def set_color(self, i, j, color):
        self.cells[i][j]['color'] = color
        self.cells[i][j]['original'] = color
        self.cells[i][j]['button'].config(bg=color)

    def reset_cell_color(self, i, j):
        original_color = self.cells[i][j]['original']
        self.cells[i][j]['button'].config(bg=original_color)

    def clear_grid(self):
        self.searching = False
        self.states_explored = 0
        self.info_panel.config(text="States Explored: 0")
        self.reset_grid()
        self.create_cells()
        self.configure_grid_layout()
        self.update_button_states()

    def reset_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.cells = []
        self.source_pos = None
        self.dest_pos = None

    def randomize_grid(self):
        try:
            new_n = int(self.n)
            new_m = int(self.m)
            if new_n <= 0 or new_m <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid dimensions first")
            return

        if new_n != self.n or new_m != self.m:
            self.n = new_n
            self.m = new_m
            self.reset_grid()
            self.create_cells()
            self.configure_grid_layout()

        p = self.obstacle_scale.get() / 100

        is_black = {}
        for i in range(self.n):
            for j in range(self.m):
                is_black[(i, j)] = 0
        t = max(min(int(p * self.n * self.m), self.n * self.m), 0)
        while t > 0:
            ((i, j), value) = random.choices(list(is_black.items()), k=1)[0]
            if not value:
                cond = True
                for pos in (i + 1, j + 1), (i + 1, j - 1), (i - 1, j + 1), (i - 1, j - 1):
                    if is_black.get(pos):
                        cond = False
                        break
                for pos in (i + 1, j), (i, j + 1), (i, j - 1), (i - 1, j):
                    if is_black.get(pos):
                        cond = True
                        break
                if cond:
                    is_black[(i, j)] = True
                    t = t - 1
        for i in range(self.n):
            for j in range(self.m):
                if (i, j) in [self.source_pos, self.dest_pos]:
                    continue
                if is_black[(i, j)]:
                    self.set_color(i, j, self.obstacle_color)
                else:
                    self.set_color(i, j, self.cell_color)

    def start_solving(self):
        if not self.source_pos or not self.dest_pos:
            messagebox.showerror("Missing Points", "Please set both start (blue) and end (green) points!")
            return

        if not self.searching:
            self.searching = True
            self.stopped = False
            self.states_explored = 0
            self.clear_path()
            self.initialize_pathfinder()
            self.solve()
            self.update_button_states()

    def stop_animation(self):
        self.stopped = True
        self.searching = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.update_button_states()

    def clear_path(self):
        for i in range(self.n):
            for j in range(self.m):
                self.reset_cell_color(i, j)
        self.states_explored = 0
        self.info_panel.config(text="States Explored: 0")

    def initialize_pathfinder(self):
        grid_state = [[cell['original'] for cell in row] for row in self.cells]
        self.pathfinder = PathFinder(
            grid=grid_state,
            start=self.source_pos,
            end=self.dest_pos,
            obstacle_color=self.obstacle_color
        )

    def solve(self):
        algorithm = self.algo_var.get()
        if algorithm == "BFS":
            generator = self.pathfinder.bfs_generator()
        elif algorithm == "DFS":
            generator = self.pathfinder.dfs_generator()
        elif algorithm == "A*":
            generator = self.pathfinder.a_star_generator()
        else:
            return
        self.run_algorithm(generator)

    def run_algorithm(self, generator):
        if self.stopped:
            return

        try:
            path, current, visited = next(generator)
            self.states_explored += 1
            self.update_visuals(current, visited)
            self.info_panel.config(text=f"States Explored: {self.states_explored}")
            self.after_id = self.root.after(self.step_delay, lambda: self.run_algorithm(generator))
        except StopIteration as e:
            self.handle_solution(e.value)

    def update_visuals(self, current, visited):
        for i in range(self.n):
            for j in range(self.m):
                pos = (i, j)
                if pos == current:
                    self.set_temp_color(i, j, '#fdcb6e')
                elif pos in visited and self.show_visited.get():
                    self.set_temp_color(i, j, '#636e72')
                elif pos in visited and not self.show_visited.get():
                    self.reset_cell_color(i, j)

    def set_temp_color(self, i, j, color):
        if (i, j) not in [self.source_pos, self.dest_pos]:
            self.cells[i][j]['button'].config(bg=color)

    def handle_solution(self, path):
        self.searching = False
        self.update_button_states()
        if path:
            self.highlight_path(path)
        else:
            messagebox.showinfo("No Path", "No valid path exists between start and end points!")

    def highlight_path(self, path):
        for pos in path[1:-1]:
            i, j = pos
            self.set_temp_color(i, j, '#ffeaa7')

    def toggle_visited_display(self):
        if not self.show_visited.get():
            self.clear_visited_colors()

    def clear_visited_colors(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.cells[i][j]['button'].cget('bg') == '#636e72':
                    self.reset_cell_color(i, j)

    def update_button_states(self):
        state_normal = tk.NORMAL if not self.searching else tk.DISABLED
        state_stop = tk.NORMAL if self.searching else tk.DISABLED

        self.generate_btn.config(state=state_normal)
        self.clear_btn.config(state=state_normal)
        self.random_btn.config(state=state_normal)
        self.solve_btn.config(state=state_normal)
        self.stop_btn.config(state=state_stop)
        self.clear_path_btn.config(state=state_normal)
        self.n_entry.config(state=state_normal)
        self.m_entry.config(state=state_normal)
        self.bfs_rb.config(state=state_normal)
        self.dfs_rb.config(state=state_normal)
        self.a_star_rb.config(state=state_normal)


if __name__ == "__main__":
    main_root = tk.Tk()
    app = GridUI(main_root)
    main_root.mainloop()
