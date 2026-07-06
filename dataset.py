import pandas as pd
from io import StringIO
from pathlib import Path

# Файл с данными должен находиться в одной папке с программой
DATASET_FILE = Path(__file__).with_name("dataset.csv")
REPORT_FILE = Path(__file__).with_name("report.txt")

# Глобальная переменная df используется другими модулями проекта
# при импорте dataset.py в data_scatter.py, data_visual.py и data_draw.py.
df = pd.read_csv(DATASET_FILE)

# Счётные / числовые колонки, для которых имеет смысл считать
# среднее значение, медиану и стандартное отклонение.
NUMERIC_COLUMNS = [
    "REF_DATE",
    "Expense",
    "Income"
]

# Категориальные колонки, для которых рассчитываются частотные распределения.
CATEGORICAL_COLUMNS = [
    "GEO",
    "Before-tax household income quintile",
    "Household expenditures, summary-level categories",
    "COORDINATE",
    "Family type",
    "Age of older adult",
    "Family income"
]

# Служебные колонки не участвуют в статистическом анализе.
SERVICE_COLUMNS = [
    "Unnamed: 0"
]


def write_line(text, report):
    """Выводит строку в консоль и одновременно записывает её в report.txt."""
    print(text)
    report.write(str(text) + "\n")


def write_block(text, report):
    """Выводит многострочный текст в консоль и одновременно записывает его в report.txt."""
    print(text)
    report.write(str(text) + "\n")


def dataframe_info_to_string(dataframe):
    """Преобразует результат dataframe.info() в строку для записи в отчёт."""
    buffer = StringIO()
    dataframe.info(buf=buffer)
    return buffer.getvalue()


def check_columns_exist(columns, dataframe):
    """Проверяет, что все указанные колонки присутствуют в датасете."""
    missing_columns = [column for column in columns if column not in dataframe.columns]
    if missing_columns:
        raise ValueError("В датасете отсутствуют колонки: " + ", ".join(missing_columns))


def print_numeric_statistics(dataframe, report):
    """Рассчитывает и выводит статистику по счётным колонкам."""
    write_line("Статистическая информация счётных колонок:", report)
    write_line("Колонка> среднее; медиана; отклонение", report)

    for column in NUMERIC_COLUMNS:
        mean_value = dataframe[column].mean()
        median_value = dataframe[column].median()
        std_value = dataframe[column].std()

        line = (
            f"{column}> "
            f"{mean_value:.2f}; "
            f"{median_value:.2f}; "
            f"{std_value:.2f}"
        )
        write_line(line, report)

    write_line("", report)


def print_categorical_frequencies(dataframe, report):
    """Формирует и выводит частотные распределения категориальных колонок."""
    write_line("Частотные распределения категориальных колонок:", report)

    for column in CATEGORICAL_COLUMNS:
        write_line(column, report)
        frequencies = dataframe[column].value_counts(dropna=False)
        write_block(frequencies.to_string(), report)
        write_line("", report)


def main():
    columns_for_analysis = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS + SERVICE_COLUMNS
    check_columns_exist(columns_for_analysis, df)

    with open(REPORT_FILE, "w", encoding="utf-8") as report:
        write_line("Размерность датасета:", report)
        write_line(df.shape, report)
        write_line("", report)

        write_line("Информация о типах данных в колонках:", report)
        info_text = dataframe_info_to_string(df)
        write_block(info_text, report)

        write_line("Количество пропусков по колонкам:", report)
        write_block(df.isnull().sum().to_string(), report)
        write_line("", report)

        write_line("Счётные колонки:", report)
        write_line(", ".join(NUMERIC_COLUMNS), report)
        write_line("", report)

        write_line("Категориальные колонки:", report)
        write_line(", ".join(CATEGORICAL_COLUMNS), report)
        write_line("", report)

        write_line("Служебные колонки, исключённые из статистического анализа:", report)
        write_line(", ".join(SERVICE_COLUMNS), report)
        write_line("", report)

        print_numeric_statistics(df, report)
        print_categorical_frequencies(df, report)


if __name__ == "__main__":
    main()
