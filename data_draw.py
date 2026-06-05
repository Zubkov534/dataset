import tkinter as tk
from tkinter import ttk
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

CATEGORICAL_COLUMNS = [
    "GEO",
    "Before-tax household income quintile",
    "Household expenditures, summary-level categories",
    "COORDINATE",
    "Family type",
    "Age of older adult",
    "Family income"
]

ALL_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS

COLUMN_LABELS = {
    "REF_DATE": "REF_DATE",
    "Expense": "Expense",
    "Income": "Income",
    "GEO": "GEO",
    "Before-tax household income quintile": "Income quintile",
    "Household expenditures, summary-level categories": "Expenditure category",
    "COORDINATE": "COORDINATE",
    "Family type": "Family type",
    "Age of older adult": "Age older adult",
    "Family income": "Family income"
}

CMAPS = [
    "viridis", "plasma", "inferno", "magma", "cividis",
    "Greys", "Purples", "Blues", "Greens", "Oranges",
    "Reds", "YlOrBr", "YlOrRd", "OrRd", "PuRd",
    "RdPu", "BuPu", "GnBu", "PuBu", "YlGnBu",
    "PuBuGn", "BuGn", "YlGn", "binary", "gist_yarg",
    "spring", "summer", "autumn", "winter"
]

DRAW_COLORS = [
    "red", "blue", "green", "black", "orange", "purple", "brown"
]

DEFAULT_CMAP = "Blues"
MARKER_STYLE = "<"


class DrawVisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Модификация визуализаций данных")
        self.root.geometry("1120x760")
        self.root.resizable(False, False)

        self.x_column = ALL_COLUMNS[0]
        self.y_column = ALL_COLUMNS[1]
        self.cmap_name = DEFAULT_CMAP

        self.draw_mode = False
        self.draw_color = DRAW_COLORS[0]
        self.draw_width = 2
        self.current_line_points = []
        self.drawn_lines = []

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 8))

        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.content_frame, width=180)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.right_frame = tk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.graph_frame = tk.Frame(self.right_frame, width=880, height=500)
        self.graph_frame.pack(side=tk.TOP)

        self.bottom_frame = tk.Frame(self.right_frame)
        self.bottom_frame.pack(side=tk.TOP, pady=8)

        self.draw_frame = tk.Frame(self.right_frame)
        self.draw_frame.pack(side=tk.TOP, pady=4)

        self.save_frame = tk.Frame(self.right_frame)
        self.save_frame.pack(side=tk.TOP, pady=5)

        tk.Label(self.top_frame, text="Цветовая схема:").pack(side=tk.LEFT, padx=(0, 5))

        self.cmap_combo = ttk.Combobox(
            self.top_frame,
            values=CMAPS,
            state="readonly",
            width=18
        )
        self.cmap_combo.set(DEFAULT_CMAP)
        self.cmap_combo.pack(side=tk.LEFT, padx=5)
        self.cmap_combo.bind("<<ComboboxSelected>>", self.change_cmap)

        tk.Label(
            self.top_frame,
            text="По умолчанию для фамилии на З: Blues"
        ).pack(side=tk.LEFT, padx=15)

        tk.Label(self.left_frame, text="Ось Y").pack(pady=(0, 6))

        for column in ALL_COLUMNS:
            tk.Button(
                self.left_frame,
                text=COLUMN_LABELS[column],
                width=22,
                command=lambda selected_column=column: self.set_y_column(selected_column)
            ).pack(pady=2)

        self.figure, self.ax = plt.subplots(figsize=(8.7, 4.9), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

        self.root.bind("<Control-z>", self.undo_last_line)
        self.root.bind("<Control-Z>", self.undo_last_line)

        tk.Label(self.bottom_frame, text="Ось X").grid(row=0, column=0, padx=4, pady=3)

        for index, column in enumerate(ALL_COLUMNS):
            row = index // 5
            col = index % 5 + 1
            tk.Button(
                self.bottom_frame,
                text=COLUMN_LABELS[column],
                width=18,
                command=lambda selected_column=column: self.set_x_column(selected_column)
            ).grid(row=row, column=col, padx=3, pady=3)

        self.draw_button = tk.Button(
            self.draw_frame,
            text="Режим рисования: выкл.",
            width=24,
            relief=tk.RAISED,
            command=self.toggle_draw_mode
        )
        self.draw_button.grid(row=0, column=0, padx=5, pady=3)

        tk.Label(self.draw_frame, text="Цвет:").grid(row=0, column=1, padx=5)

        self.color_combo = ttk.Combobox(
            self.draw_frame,
            values=DRAW_COLORS,
            state="readonly",
            width=12
        )
        self.color_combo.set(self.draw_color)
        self.color_combo.grid(row=0, column=2, padx=5)
        self.color_combo.bind("<<ComboboxSelected>>", self.change_draw_color)

        tk.Label(self.draw_frame, text="Толщина:").grid(row=0, column=3, padx=5)

        self.width_spinbox = tk.Spinbox(
            self.draw_frame,
            from_=1,
            to=10,
            width=5,
            command=self.change_draw_width
        )
        self.width_spinbox.delete(0, tk.END)
        self.width_spinbox.insert(0, str(self.draw_width))
        self.width_spinbox.grid(row=0, column=4, padx=5)

        tk.Label(
            self.draw_frame,
            text="Отмена линии: Ctrl+Z"
        ).grid(row=0, column=5, padx=10)

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
        self.drawn_lines.clear()
        self.draw_graph()

    def set_y_column(self, column):
        self.y_column = column
        self.drawn_lines.clear()
        self.draw_graph()

    def change_cmap(self, event=None):
        self.cmap_name = self.cmap_combo.get()
        self.drawn_lines.clear()
        self.draw_graph()

    def change_draw_color(self, event=None):
        self.draw_color = self.color_combo.get()

    def change_draw_width(self):
        try:
            self.draw_width = int(self.width_spinbox.get())
        except ValueError:
            self.draw_width = 2

    def toggle_draw_mode(self):
        self.draw_mode = not self.draw_mode

        if self.draw_mode:
            self.draw_button.config(
                text="Режим рисования: вкл.",
                relief=tk.SUNKEN
            )
            self.status_label.config(text="Рисование включено")
        else:
            self.draw_button.config(
                text="Режим рисования: выкл.",
                relief=tk.RAISED
            )
            self.status_label.config(text="Рисование выключено")

    def is_numeric(self, column):
        return column in NUMERIC_COLUMNS

    def is_categorical(self, column):
        return column in CATEGORICAL_COLUMNS

    def draw_graph(self):
        self.ax.clear()

        x_is_num = self.is_numeric(self.x_column)
        y_is_num = self.is_numeric(self.y_column)
        x_is_cat = self.is_categorical(self.x_column)
        y_is_cat = self.is_categorical(self.y_column)

        if x_is_num and y_is_num and self.x_column == self.y_column:
            self.draw_histogram()
        elif x_is_cat and y_is_cat and self.x_column == self.y_column:
            self.draw_pie_chart()
        elif x_is_cat and y_is_num:
            self.draw_bar_chart()
        elif x_is_num and y_is_cat:
            self.draw_box_plot()
        elif x_is_num and y_is_num:
            self.draw_scatter_plot()
        elif x_is_cat and y_is_cat:
            self.draw_category_bar_chart()
        else:
            self.ax.text(0.5, 0.5, "График для выбранных колонок не задан",
                         ha="center", va="center")

        self.redraw_saved_lines()
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_scatter_plot(self):
        data = df[[self.x_column, self.y_column]].dropna()

        self.ax.scatter(
            data[self.x_column],
            data[self.y_column],
            marker=MARKER_STYLE,
            c=data[self.y_column],
            cmap=self.cmap_name
        )

        self.ax.set_xlabel(self.x_column)
        self.ax.set_ylabel(self.y_column)
        self.ax.set_title(f"Точечная диаграмма: {self.x_column} / {self.y_column}")
        self.ax.grid(True)

    def draw_histogram(self):
        data = df[self.x_column].dropna()

        n, bins, patches = self.ax.hist(data, bins=10, edgecolor="black")
        cmap = plt.get_cmap(self.cmap_name)

        for i, patch in enumerate(patches):
            patch.set_facecolor(cmap(i / max(len(patches) - 1, 1)))

        self.ax.set_xlabel(self.x_column)
        self.ax.set_ylabel("Количество записей")
        self.ax.set_title(f"Гистограмма: {self.x_column}")
        self.ax.grid(True, axis="y")

    def draw_pie_chart(self):
        counts = df[self.x_column].value_counts(dropna=False).head(10)

        labels = [str(item) for item in counts.index]
        values = counts.values
        cmap = plt.get_cmap(self.cmap_name)
        colors = [cmap(i / max(len(values) - 1, 1)) for i in range(len(values))]

        self.ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90
        )
        self.ax.set_title(f"Круговая диаграмма: {self.x_column}")

    def draw_bar_chart(self):
        counts = df[self.x_column].value_counts(dropna=False).head(12)

        labels = [str(item) for item in counts.index]
        values = counts.values
        cmap = plt.get_cmap(self.cmap_name)
        colors = [cmap(i / max(len(values) - 1, 1)) for i in range(len(values))]

        self.ax.bar(labels, values, color=colors)
        self.ax.set_xlabel(self.x_column)
        self.ax.set_ylabel("Количество записей")
        self.ax.set_title(f"Столбчатая диаграмма: {self.x_column}")
        self.ax.tick_params(axis="x", rotation=30, labelsize=8)
        self.ax.grid(True, axis="y")

    def draw_box_plot(self):
        data = df[[self.x_column, self.y_column]].dropna()

        categories = list(data[self.y_column].value_counts().head(10).index)
        grouped_values = [
            data.loc[data[self.y_column] == category, self.x_column]
            for category in categories
        ]

        box = self.ax.boxplot(
            grouped_values,
            labels=[str(category) for category in categories],
            patch_artist=True
        )

        cmap = plt.get_cmap(self.cmap_name)
        for i, patch in enumerate(box["boxes"]):
            patch.set_facecolor(cmap(i / max(len(box["boxes"]) - 1, 1)))

        self.ax.set_xlabel(self.y_column)
        self.ax.set_ylabel(self.x_column)
        self.ax.set_title(f"Коробочная диаграмма: {self.x_column} по {self.y_column}")
        self.ax.tick_params(axis="x", rotation=30, labelsize=8)
        self.ax.grid(True, axis="y")

    def draw_category_bar_chart(self):
        counts = df[self.x_column].value_counts(dropna=False).head(12)

        labels = [str(item) for item in counts.index]
        values = counts.values
        cmap = plt.get_cmap(self.cmap_name)
        colors = [cmap(i / max(len(values) - 1, 1)) for i in range(len(values))]

        self.ax.bar(labels, values, color=colors)
        self.ax.set_xlabel(self.x_column)
        self.ax.set_ylabel("Количество записей")
        self.ax.set_title(f"Распределение категорий: {self.x_column}")
        self.ax.tick_params(axis="x", rotation=30, labelsize=8)
        self.ax.grid(True, axis="y")

    def on_mouse_press(self, event):
        if not self.draw_mode or event.inaxes != self.ax or event.button != 1:
            return

        self.change_draw_width()
        self.current_line_points = [(event.xdata, event.ydata)]

    def on_mouse_move(self, event):
        if not self.draw_mode or not self.current_line_points:
            return
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        self.current_line_points.append((event.xdata, event.ydata))

        if len(self.current_line_points) >= 2:
            x_values = [point[0] for point in self.current_line_points[-2:]]
            y_values = [point[1] for point in self.current_line_points[-2:]]

            line, = self.ax.plot(
                x_values,
                y_values,
                color=self.draw_color,
                linewidth=self.draw_width
            )
            self.canvas.draw_idle()

    def on_mouse_release(self, event):
        if not self.draw_mode or not self.current_line_points:
            return

        if len(self.current_line_points) > 1:
            self.drawn_lines.append({
                "points": self.current_line_points[:],
                "color": self.draw_color,
                "width": self.draw_width
            })

        self.current_line_points = []

    def redraw_saved_lines(self):
        for saved_line in self.drawn_lines:
            points = saved_line["points"]
            if len(points) < 2:
                continue

            x_values = [point[0] for point in points]
            y_values = [point[1] for point in points]

            self.ax.plot(
                x_values,
                y_values,
                color=saved_line["color"],
                linewidth=saved_line["width"]
            )

    def undo_last_line(self, event=None):
        if self.drawn_lines:
            self.drawn_lines.pop()
            self.draw_graph()
            self.status_label.config(text="Последняя линия отменена")
        else:
            self.status_label.config(text="Нет линий для отмены")

    def save_graph(self):
        file_name = "graph" + datetime.now().strftime("%H_%M_%S") + ".png"
        self.figure.savefig(file_name, dpi=300)
        self.status_label.config(text=f"Файл сохранён: {file_name}")


def main():
    root = tk.Tk()
    DrawVisualApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
