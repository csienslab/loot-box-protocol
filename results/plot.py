import pandas as pd
import matplotlib.pyplot as plt
import os


"""
experiments should be run on CSIE workstations
"""


def plot_data(df, x_column, y_columns, title, xlabel, ylabel, colors):
    plt.figure(figsize=(10, 6))
    for y_column in y_columns:
        plt.plot(df[x_column], df[y_column], label=y_column, color=colors[y_column])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)


df1 = pd.read_csv("poly_deg.csv")
plot_data(
    df1,
    "degree",
    ["setup", "evaluation", "verification"],
    "Probability Verification (over different polynomial degrees)",
    "Polynomial Degree (Sample Size = 30, Parallelism = 6)",
    "Execution Time (s)",
    {"setup": "blue", "evaluation": "orange", "verification": "gray"},
)
plt.savefig("poly_deg.png")

df2 = pd.read_csv("poly_sample.csv")
df2["setup"] = 0  # Adding 'setup' as 0 for the second dataset
plot_data(
    df2,
    "Sample Size",
    ["setup", "evaluation", "verification"],
    "Probability Verification (over different sample sizes)",
    "Sample Size (Degree = 150, Parallelism = 6)",
    "Execution Time (s)",
    {"setup": "blue", "evaluation": "orange", "verification": "gray"},
)
plt.savefig("poly_sample.png")
