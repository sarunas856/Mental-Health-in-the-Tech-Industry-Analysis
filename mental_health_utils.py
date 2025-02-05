import sqlite3 as sql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sns
from typing import Dict, Tuple


def join_tables_to_dataframe(db_path: str) -> pd.DataFrame:
    """
    Joins Survey, Answer, and Question tables from the SQLite database and returns a DataFrame with relevant data.

    Parameters:
    - db_path (str): Path to the SQLite database.

    Returns:
    - pd.DataFrame: DataFrame with columns: year, survey, question_id, question_text, user_id, answer_text.

    Raises:
    - sql.Error: If an error occurs while querying the database.
    """
    try:
        conn = sql.connect(db_path)

        query = """
        SELECT
            Survey.SurveyID AS year,
            Survey.Description AS survey,
            Question.questionid AS question_id,
            Question.questiontext AS question_text,
            Answer.UserID AS user_id,
            Answer.AnswerText AS answer_text
        FROM
            Survey
        INNER JOIN Answer ON Survey.SurveyID = Answer.SurveyID
        INNER JOIN Question ON Answer.QuestionID = Question.QuestionID
        """

        df = pd.read_sql_query(query, conn)

        return df

    except sql.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def count_values(
    df: pd.DataFrame,
    question_text: str,
    missing_value: str = "-1",
    max_display: int = 5,
) -> Tuple[pd.Series, int, int]:
    """
    Function to count distinct values for a given question and return the count of missing values.

    Parameters:
    - df: DataFrame containing the data.
    - question_text: The question text to filter the DataFrame.
    - missing_value: The value representing missing data (default is '-1').
    - max_display: Maximum number of rows to display from the distinct values.

    Returns:
    - distinct_values: A series of distinct counts for the given question.
    - count_missing: The count of missing values ('-1') for the given question.
    - total_count: The total count of responses for the given question.
    """
    question_df = df[df["question_text"] == question_text].copy()

    distinct_values = question_df["answer_text"].value_counts()

    count_missing = (question_df["answer_text"] == missing_value).sum()

    total_count = len(question_df)

    print(distinct_values.head(max_display))
    if len(distinct_values) > max_display:
        print(f"\n... and {len(distinct_values) - max_display} more distinct values.")

    print(f"\nCount of {missing_value} values:", count_missing)
    print(f"Total count of responses: {total_count}")

    return distinct_values, count_missing, total_count


def transform_and_aggregate(
    df: pd.DataFrame, question: str, column_name: str, mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Filters, transforms, and aggregates data based on a specific question.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing the data.
        question (str): The question to filter the data by.
        column_name (str): The name for the transformed column in the output.
        mapping (dict): A dictionary mapping input values to their desired values.

    Returns:
        pd.DataFrame: A DataFrame with the transformed column and counts.
    """
    filtered_df = df[df["question_text"] == question].copy()

    filtered_df[column_name] = (
        filtered_df["answer_text"].str.lower().map(mapping).fillna("Other")
    )

    value_counts = filtered_df[column_name].value_counts()

    result_df = value_counts.reset_index()
    result_df.columns = [column_name, "count"]

    return result_df


def plot_bar_with_percentages(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: str,
    title: str,
    x_label: str,
    y_label: str,
    palette: str = None,
) -> None:
    """
    Function to plot a bar chart with percentage labels on top of bars.

    Parameters:
    - df: DataFrame containing the data.
    - x: Column name for x-axis.
    - y: Column name for y-axis.
    - hue: Column name for grouping (hue).
    - title: Title of the plot.
    - x_label: Label for the x-axis.
    - y_label: Label for the y-axis.
    - palette: Optional color palette for the bars.
    """
    plt.figure(figsize=(12, 5))

    sns.barplot(
        x=x,
        y=y,
        data=df,
        hue=hue,
        palette=palette,
    )

    total_count = df[y].sum()

    for patch in plt.gca().patches:
        bar_height = patch.get_height()
        percentage = (bar_height / total_count) * 100
        plt.gca().text(
            patch.get_x() + patch.get_width() / 2,
            bar_height + 0.5,
            f"{percentage:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.title(title, fontsize=16)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.show()


def calculate_confidence_interval(
    p: float, n: int, confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate the confidence interval for a proportion.

    Args:
        p (float): Proportion value (0 <= p <= 1).
        n (int): Sample size.
        confidence_level (float): Confidence level (default is 0.95).

    Returns:
        tuple: Lower and upper bounds of the confidence interval.
    """
    z_score = norm.ppf(1 - (1 - confidence_level) / 2)
    se = np.sqrt((p * (1 - p)) / n)
    margin_of_error = z_score * se
    return p - margin_of_error, p + margin_of_error


def plot_prevalence_with_ci(
    plot_data: pd.DataFrame, title: str, palette: str = None
) -> None:
    """
    Plot prevalence rates with confidence intervals.

    Args:
        plot_data (pd.DataFrame): DataFrame containing the following columns:
            - 'condition': Names of the conditions.
            - 'prevalence_rate': Prevalence rates as percentages.
            - 'ci_lower': Lower bounds of confidence intervals as percentages.
            - 'ci_upper': Upper bounds of confidence intervals as percentages.
        title (str): Title of the plot.
        palette: Optional color palette for the bars.

    Returns:
        None
    """
    plt.figure(figsize=(12, 6))
    sns.barplot(
        x="condition",
        y="prevalence_rate",
        hue="condition",
        data=plot_data,
        palette=palette,
        errorbar=None,
    )

    for i, row in plot_data.iterrows():
        plt.errorbar(
            x=i,
            y=row["prevalence_rate"],
            yerr=[
                [row["prevalence_rate"] - row["ci_lower"]],
                [row["ci_upper"] - row["prevalence_rate"]],
            ],
            fmt="none",
            color="black",
            capsize=5,
        )

        plt.text(
            x=i,
            y=row["ci_upper"] + 0.1,
            s=f"({row['ci_lower']:.0f}%, {row['ci_upper']:.0f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

        plt.text(
            x=i,
            y=row["prevalence_rate"] / 2,
            s=f"{row['prevalence_rate']:.1f}%",
            ha="center",
            va="center",
            fontsize=12,
            color="white",
            weight="bold",
        )

    plt.title(title, fontsize=16)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.xlabel("")
    plt.ylabel("Prevalence Rate (%)", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.show()
