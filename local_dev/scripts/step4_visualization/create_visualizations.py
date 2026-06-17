from pathlib import Path 
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from core.config import OUTPUT_DIR
from matplotlib import font_manager

FIGURE_DIR = OUTPUT_DIR/"figures"

def setup_japanese_font() -> None:
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
        "C:/Windows/Fonts/YuGothR.ttc",
        "C:/Windows/Fonts/meiryo.ttc",
    ]
    for font_path in font_paths:
        path = Path(font_path)
        if path.exists():
            font_manager.fontManager.addfont(str(path))
            font_name = font_manager.FontProperties(fname=str(path)).get_name()
            plt.rcParams["font.family"] = font_name
            plt.rcParams["axes.unicode_minus"] = False
            print(f"Using font: {font_name}")
            return
    print("Japanese font was not found. Japanese text may not render correctly.")
    plt.rcParams["axes.unicode_minus"] = False
setup_japanese_font()


def visualization_pipeline(): 
    FIGURE_DIR.mkdir(parents=True, exist_ok=True) 

    df = pd.read_csv(OUTPUT_DIR/"high_growth_companies.csv")
    create_top_cagr_chart(df)
    create_growth_vs_sales_size_scatter(df)
    create_industry_pie_chart(df)
    create_industry_avg_cagr_chart(df)



def create_top_cagr_chart(df: pd.DataFrame, limit: int | None = None ):
    chart_df = df.sort_values("four_year_cagr", ascending=False).copy()

    if limit is not None: 
        chart_df = chart_df.head(limit)
    chart_df["four_year_cagr_percent"] = chart_df["four_year_cagr"] * 100

    plt.figure(figsize=(12, 8))
    bars = plt.barh(chart_df["filerName"], chart_df["four_year_cagr_percent"])

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            va="center"
        )
    plt.xlabel("4年間CAGR（年平均成長率、%）", fontsize=12)
    plt.ylabel("企業", fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.title("4年間CAGRに基づく高成長企業ランキング", fontsize=16, pad=15)
    plt.gca().invert_yaxis()
    plt.tight_layout()

    ax = plt.gca()
    ax.tick_params(axis="y", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.savefig(FIGURE_DIR / "top_four_year_cagr.png", dpi=300)
    plt.close()

def yen_to_oku_label(x, pos):
    oku = x / 100_000_000

    if oku >= 10_000:
        return f"{oku/10_000:.0f}兆円"
    else:
        return f"{oku:.0f}億円"


def assign_sales_size_group(sales):
    if sales < 1_000_000_000:        
        return "10億円未満"
    elif sales < 10_000_000_000: 
        return "10億〜100億円"
    elif sales < 100_000_000_000: 
        return "100億〜1,000億円"
    elif sales < 300_000_000_000:
        return "1,000億〜3,000億円"
    else:
        return "3,000億円以上"


def create_growth_vs_sales_size_scatter(df: pd.DataFrame):
    chart_df = df.copy()
    chart_df["four_year_cagr_percent"] = chart_df["four_year_cagr"] * 100
    chart_df["sales_size_group"] = chart_df["sales_4_years_ago"].apply(assign_sales_size_group)

    plt.figure(figsize=(13, 7))

    groups = [
        "10億円未満",
        "10億〜100億円",
        "100億〜1,000億円",
        "1,000億〜3,000億円",
        "3,000億円以上",
    ]

    for group in groups:
        group_df = chart_df[chart_df["sales_size_group"] == group]

        if group_df.empty:
            continue

        plt.scatter(
            group_df["sales_4_years_ago"],
            group_df["four_year_cagr_percent"],
            alpha=0.75,
            label=group,
            s=60,
        )

    plt.axhline(40, linestyle="--", linewidth=1)
    plt.text(
        chart_df["sales_4_years_ago"].min(),
        42,
        "40%基準",
        fontsize=10,
    )

    plt.axvline(1_000_000_000, linestyle=":", linewidth=1)       
    plt.axvline(10_000_000_000, linestyle=":", linewidth=1)    
    plt.axvline(100_000_000_000, linestyle=":", linewidth=1)   
    plt.axvline(300_000_000_000, linestyle=":", linewidth=1)  

    plt.xscale("log")
    ticks = [
        100_000_000,          
        300_000_000,          
        1_000_000_000,
        3_000_000_000, 
        10_000_000_000, 
        30_000_000_000,  
        100_000_000_000,  
        300_000_000_000,  
    ]

    plt.xticks(ticks)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(yen_to_oku_label))

    plt.xlabel("4年前売上高（円、対数スケール）", fontsize=12)
    plt.ylabel("4年間CAGR（年平均成長率、%）", fontsize=12)
    plt.title("売上規模と売上成長率の関係", fontsize=16, pad=15)

    plt.grid(axis="both", linestyle="--", alpha=0.3)
    plt.legend(title="4年前売上規模", fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "growth_vs_sales_size.png", dpi=300)
    plt.close()


def create_industry_pie_chart(df: pd.DataFrame):
    chart_df = df.copy()

    industry_col = "industry"

    industry_counts = (
        chart_df[industry_col]
        .fillna("不明")
        .value_counts()
    )

    plt.figure(figsize=(10, 8))

    plt.pie(
        industry_counts,
        labels=industry_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
    )

    plt.title("高成長企業の業種構成", fontsize=16, pad=15)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "high_growth_industry_pie.png", dpi=300)
    plt.close()


def create_industry_avg_cagr_chart(df: pd.DataFrame, min_companies: int = 2, top_n: int = 10):
    chart_df = df.copy()
    chart_df["four_year_cagr_percent"] = chart_df["four_year_cagr"] * 100

    industry_summary = (
        chart_df.groupby("industry")
        .agg(
            company_count=("industry", "size"),
            avg_cagr_percent=("four_year_cagr_percent", "mean")
        )
        .reset_index()
    )

    industry_summary = industry_summary[industry_summary["company_count"] >= min_companies]
    industry_summary = industry_summary.sort_values("avg_cagr_percent", ascending=False).head(top_n)

    plt.figure(figsize=(12, 8))
    bars = plt.barh(industry_summary["industry"], industry_summary["avg_cagr_percent"])

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            va="center"
        )

    plt.xlabel("平均4年間CAGR（%）", fontsize=12)
    plt.ylabel("業種", fontsize=12)
    plt.title("業種別平均4年間CAGRランキング", fontsize=16, pad=15)

    plt.gca().invert_yaxis()

    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "industry_avg_cagr.png", dpi=300)
    plt.close()

if __name__ == "__main__": 
    visualization_pipeline()