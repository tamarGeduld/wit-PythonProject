import os

import matplotlib.pyplot as plt
import tempfile

from db import analysis_collection


def save_plot_as_png(plot_func):
    tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plot_func()
    plt.savefig(tmp_file.name)
    plt.close()
    return tmp_file.name


def generate_function_length_histogram(lengths):
    def plot():
        plt.hist(lengths, bins=10, color='skyblue', edgecolor='black')
        plt.title('Histogram of Function Lengths')
        plt.xlabel('Function Length (lines)')
        plt.ylabel('Frequency')
    return save_plot_as_png(plot)


def generate_problem_type_pie_chart(problem_counts):
    def plot():
        labels = list(problem_counts.keys())
        sizes = list(problem_counts.values())
        if sum(sizes) == 0:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No issues detected!', horizontalalignment='center',
                    verticalalignment='center', fontsize=14, transform=ax.transAxes)
            ax.axis('off')
            plt.title("Problem Type Distribution")
        else:
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title("Problem Type Distribution")
    return save_plot_as_png(plot)


def generate_problem_count_bar_chart(problems_per_file):
    def plot():
        plt.figure(figsize=(8, 5))
        files = list(problems_per_file.keys())
        counts = list(problems_per_file.values())
        plt.bar(files, counts, color='orange')
        plt.xticks(rotation=45)
        plt.title("Problem Count per File")
        plt.xlabel("File Name")
        plt.ylabel("Number of Problems")
        plt.tight_layout()
    return save_plot_as_png(plot)


def get_all_function_lengths(results):
    lengths = []
    for file_checks in results.values():
        lengths.extend(file_checks.get("function_lengths", []))
    return lengths


def generate_issue_trend_graph(records):
    def plot():
        timestamps = [record["timestamp"] for record in records]
        issue_counts = [record["issues"] for record in records]

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, issue_counts, marker='o', linestyle='-', color='blue')
        plt.xlabel("Time")
        plt.ylabel("Number of Issues")
        plt.title("Code Issues Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()

    return save_plot_as_png(plot)