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

DEFAULT_CMAP = "Blues"
MARKER_STYLE = "<"


class VisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Улучшенная визуализация данных")
        self.root.geometry("1080x720")
        self.root.resizable(False, False)

        self.x_column = ALL_COLUMNS[0]
        self.y_column = ALL_COLUMNS[1]
        self.cmap_name = DEFAULT_CMAP

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

        self.graph_frame = tk.Frame(self.right_frame, width=860, height=500)
        self.graph_frame.pack(side=tk.TOP)

        self.bottom_frame = tk.Frame(self.right_frame)
        self.bottom_frame.pack(side=tk.TOP, pady=8)

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

        self.figure, self.ax = plt.subplots(figsize=(8.5, 4.8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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

    def change_cmap(self, event=None):
        self.cmap_name = self.cmap_combo.get()
        self.draw_graph()

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

    def save_graph(self):
        file_name = "graph" + datetime.now().strftime("%H_%M_%S") + ".png"
        self.figure.savefig(file_name, dpi=300)
        self.status_label.config(text=f"Файл сохранён: {file_name}")


def main():
    root = tk.Tk()
    VisualApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
