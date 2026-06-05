import tkinter as tk
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import dataset


df = dataset.df

NUMERIC_COLUMNS = [
    "REF_DATE",
    "Expense",
    "Income"
]

MARKER_STYLE = "<"


class ScatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Первичная визуализация данных")
        self.root.geometry("850x620")
        self.root.resizable(False, False)

        self.x_column = NUMERIC_COLUMNS[0]
        self.y_column = NUMERIC_COLUMNS[1]

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame, width=140)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.center_frame = tk.Frame(self.main_frame)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.graph_frame = tk.Frame(self.center_frame, width=660, height=470)
        self.graph_frame.pack(side=tk.TOP)

        self.bottom_frame = tk.Frame(self.center_frame)
        self.bottom_frame.pack(side=tk.TOP, pady=8)

        self.save_frame = tk.Frame(self.center_frame)
        self.save_frame.pack(side=tk.TOP, pady=5)

        tk.Label(self.left_frame, text="Ось Y").pack(pady=(0, 8))

        for column in NUMERIC_COLUMNS:
            tk.Button(
                self.left_frame,
                text=column,
                width=16,
                command=lambda selected_column=column: self.set_y_column(selected_column)
            ).pack(pady=3)

        self.figure, self.ax = plt.subplots(figsize=(6.5, 4.6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.bottom_frame, text="Ось X").pack(side=tk.LEFT, padx=(0, 8))

        for column in NUMERIC_COLUMNS:
            tk.Button(
                self.bottom_frame,
                text=column,
                width=16,
                command=lambda selected_column=column: self.set_x_column(selected_column)
            ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            self.save_frame,
            text="Сохранить график",
            width=24,
            command=self.save_graph
        ).pack()

        self.status_label = tk.Label(self.save_frame, text="")
        self.status_label.pack(pady=4)

        self.draw_graph()

    def set_x_column(self, column):
        self.x_column = column
        self.draw_graph()

    def set_y_column(self, column):
        self.y_column = column
        self.draw_graph()

    def draw_graph(self):
        self.ax.clear()

        data = df[[self.x_column, self.y_column]].dropna()

        self.ax.scatter(
            data[self.x_column],
            data[self.y_column],
            marker=MARKER_STYLE
        )

        self.ax.set_xlabel(self.x_column)
        self.ax.set_ylabel(self.y_column)
        self.ax.set_title(f"{self.x_column} / {self.y_column}")
        self.ax.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()

    def save_graph(self):
        file_name = "graph" + datetime.now().strftime("%H_%M_%S") + ".png"
        self.figure.savefig(file_name, dpi=300)
        self.status_label.config(text=f"Файл сохранён: {file_name}")


def main():
    root = tk.Tk()
    ScatterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
