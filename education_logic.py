"""
education_logic.py

Provides specialized tools for the Teacher Module to analyze score distribution 
and automatically generate visualizations using Matplotlib, now with extensive localization
and AI Diagnostic pipeline exposure.
"""
import pandas as pd
import matplotlib.pyplot as plt
import io
import uuid
from config import GRAPH_DIR, ensure_app_directories

# Native MacOS / Universal Global Font Override for Chinese Text rendering
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

ensure_app_directories()
GRAPH_OUTPUT_DIR = str(GRAPH_DIR)


def _normalize_score_series(series: pd.Series) -> pd.Series:
    """
    Convert score-like text such as '100分', '95.5 ', or '1,234' into numbers.
    """
    text_series = series.astype(str).str.strip()
    cleaned = (
        text_series
        .str.replace(',', '', regex=False)
        .str.replace('，', '', regex=False)
        .str.replace(r'[^0-9.\-]+', '', regex=True)
    )
    cleaned = cleaned.replace({'': pd.NA, '-': pd.NA, '.': pd.NA, '-.': pd.NA})
    return pd.to_numeric(cleaned, errors='coerce')


def _score_column_priority(column_name: str) -> int:
    """
    Rank likely score columns so totals/finals beat IDs or item-level metrics.
    """
    name = str(column_name).strip().lower()

    high_priority_terms = [
        'total score', 'final score', 'overall score', 'total grade', 'final grade',
        '总分', '总成绩', '期末成绩', '总评', '合计', '成绩'
    ]
    medium_priority_terms = ['score', 'grade', 'marks', '分数', '得分']
    low_priority_bad_terms = ['id', '学号', 'student no', 'student id', '序号', '排名', 'rank']

    for term in high_priority_terms:
        if term in name:
            return 3
    for term in medium_priority_terms:
        if term in name:
            return 2
    for term in low_priority_bad_terms:
        if term in name:
            return 0
    return 1

def analyze_and_graph_scores(csv_content: str) -> str:
    """
    Analyzes student scores from CSV content, calculates statistics,
    generates a bar graph with highlighted max/min.
    Returns a unified summary string embedding the [GRAPH] token
    and a RAW Output Data log so the User can debug the AI's hallucination rate.
    """
    try:
        normalized_csv = csv_content.strip()
        df = pd.read_csv(io.StringIO(normalized_csv))
        df = df.dropna(how='all').copy()
        
        # Name defaults to the primary index (usually Student Names)
        name_col = df.columns[0]
        score_col = None
        numeric_candidates = {}

        for col in df.columns:
            normalized = _normalize_score_series(df[col])
            if normalized.notna().any():
                numeric_candidates[col] = normalized
        
        # 1. Prefer score-like columns such as 总分 / Final Score over IDs or other numeric fields.
        if score_col is None:
            numeric_cols = [col for col in df.columns if col in numeric_candidates]
            if numeric_cols:
                score_col = max(
                    numeric_cols,
                    key=lambda col: (
                        _score_column_priority(col),
                        numeric_candidates[col].notna().sum(),
                        df.columns.get_loc(col)
                    )
                )
                
        if score_col is None:
            return "Error: I could not find a usable numeric score column in the uploaded file."

        df[score_col] = numeric_candidates[score_col]
        df = df.dropna(subset=[score_col]).copy()

        if df.empty:
            return "Error: I found a possible score column, but none of its values could be converted into numbers."

        if df[name_col].isna().all():
            df[name_col] = [f"Student {i + 1}" for i in range(len(df))]
        else:
            df[name_col] = df[name_col].fillna('').astype(str).str.strip()
            blank_names = df[name_col] == ''
            if blank_names.any():
                fallback_names = [f"Student {i + 1}" for i in range(len(df))]
                df.loc[blank_names, name_col] = [fallback_names[i] for i, is_blank in enumerate(blank_names) if is_blank]

        # Calculate Statistics
        highest_score = round(df[score_col].max(), 2)
        lowest_score = round(df[score_col].min(), 2)
        average_score = round(df[score_col].mean(), 2)
        
        # Find students who got Highest and Lowest
        highest_students = df[df[score_col] == df[score_col].max()][name_col].tolist()
        lowest_students = df[df[score_col] == df[score_col].min()][name_col].tolist()
        
        # Sort values for a better looking chart
        df_sorted = df.sort_values(by=score_col, ascending=False).reset_index(drop=True)

        # Matplotlib Graph Generation
        plt.figure(figsize=(10, 6))
        colors = ['dodgerblue'] * len(df_sorted)
        
        for i, row in df_sorted.iterrows():
            if round(row[score_col], 2) == highest_score:
                colors[i] = 'limegreen'
            elif round(row[score_col], 2) == lowest_score:
                colors[i] = 'crimson'

        bars = plt.bar(df_sorted[name_col].astype(str), df_sorted[score_col], color=colors)
        
        # Add numeric markers
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 1, round(yval, 1), ha='center', va='bottom', fontsize=9)

        plt.title('Class Score Distribution', fontsize=16)
        plt.xlabel('Student Matrix', fontsize=12)
        plt.ylabel('Score Output', fontsize=12)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save Graph
        graph_path = str(GRAPH_DIR / f"score_graph_{uuid.uuid4().hex}.png")
        plt.savefig(graph_path)
        plt.close()

        report = (
            f"📈 **Score Analysis Complete!**\n"
            f"- **Highest Score:** {highest_score} ({', '.join(str(s) for s in highest_students)})\n"
            f"- **Lowest Score:** {lowest_score} ({', '.join(str(s) for s in lowest_students)})\n"
            f"- **Average Score:** {average_score:.2f}\n"
            f"\n[GRAPH: {graph_path}]"
        )
        return report

    except Exception as e:
        return f"Error analyzing scores. Ensure the file is a valid CSV or spreadsheet with a name column and a numeric score column. Details: {str(e)}"
