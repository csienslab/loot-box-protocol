import pandas as pd
import matplotlib.pyplot as plt
import os


"""
experiments should be run on CSIE workstations
"""


def plot_data(df, y_columns, title, xlabel, ylabel, colors):
    plt.figure(figsize=(10, 6))
    for y_column in y_columns:
        x = df.index
        y = df[y_column]["mean"]
        dy = df[y_column]["std"]
        plt.plot(
            x,
            y,
            label=y_column,
            color=colors[y_column],
            marker="o",
        )
        plt.fill_between(
            x,
            y - dy,
            y + dy,
            alpha=0.2,
            color=colors[y_column],
        )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)


df1 = pd.read_csv("poly_deg.csv").groupby("degree").agg(["mean", "std"])
print(df1)
plot_data(
    df1,
    ["setup", "evaluation", "verification"],
    "Probability Verification (over different polynomial degrees)",
    "Polynomial Degree (Sample Size = 30, Parallelism = 8, Runs = 10)",
    "Execution Time (s)",
    {"setup": "blue", "evaluation": "orange", "verification": "gray"},
)
plt.savefig("poly_deg.png")

df2 = pd.read_csv("poly_sample.csv")
df2["setup"] = 0  # Adding 'setup' as 0 for the second dataset
df2 = df2.groupby("Sample Size").agg(["mean", "std"])
print(df2)
plot_data(
    df2,
    ["setup", "evaluation", "verification"],
    "Probability Verification (over different sample sizes)",
    "Sample Size (Degree = 150, Parallelism = 8, Runs = 10)",
    "Execution Time (s)",
    {"setup": "blue", "evaluation": "orange", "verification": "gray"},
)
plt.savefig("poly_sample.png")

df3 = pd.read_csv("fc_samples.csv")
df3["setup"] = 0  # Adding 'setup' as 0 for the second dataset
df3 = df3.groupby("Sample Size").agg(["mean", "std"])
print(df3)
plot_data(
    df3,
    ["setup", "evaluation", "verification"],
    "Probability Verification (over different sample sizes)",
    "Sample Size (Function Commitment, Parallelism = 8, Runs = 10)",
    "Execution Time (s)",
    {"setup": "blue", "evaluation": "orange", "verification": "gray"},
)
plt.savefig("fc_samples.png")
