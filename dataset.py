import pandas as pd
import sys

df = pd.read_csv("dataset.csv")

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

def write_line(text, report):
    print(text)
    report.write(str(text) + "\n")

def dataframe_info_to_string(dataframe):
    from io import StringIO
    buffer = StringIO()
    dataframe.info(buf=buffer)
    return buffer.getvalue()

def main():
    with open("report.txt", "w", encoding="utf-8") as report:

        write_line(df.shape, report)
        write_line("", report)

        info_text = dataframe_info_to_string(df)
        print(info_text)
        report.write(info_text + "\n")

        write_line("Количество пропусков по колонкам:", report)
        write_line(df.isnull().sum(), report)
        write_line("", report)

        write_line("Числовые колонки:", report)
        write_line(", ".join(NUMERIC_COLUMNS), report)
        write_line("", report)

        write_line("Категориальные колонки:", report)
        write_line(", ".join(CATEGORICAL_COLUMNS), report)
        write_line("", report)

        write_line("Колонка> среднее; медиана; отклонение", report)

        for column in NUMERIC_COLUMNS:
            mean_value = df[column].mean()
            median_value = df[column].median()
            std_value = df[column].std()

            line = (
                f"{column}> "
                f"{mean_value:.2f}; "
                f"{median_value:.2f}; "
                f"{std_value:.2f}"
            )
            write_line(line, report)

        write_line("", report)

        for column in CATEGORICAL_COLUMNS:
            write_line(column, report)
            write_line(df[column].value_counts(dropna=False), report)
            write_line("", report)

if __name__ == "__main__":
    main()
