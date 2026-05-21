import matplotlib.pyplot as plt
from data_extraction_M1 import extract_answers_sequence

def load_sequences(collated_answers_path):

    with open(collated_answers_path, "r") as f:
        blocks = f.read().strip().split("\n*\n")

    sequences = []

    for block in blocks:
        lines = block.splitlines()
        answers = []

        i = 0
        while i < len(lines):
            if lines[i].startswith("Question"):
                for j in range(4):
                    if "[X]" in lines[i + j + 1]:
                        answers.append(j + 1)
                        break
                else:
                    answers.append(0)

                i += 5
            else:
                i += 1

        if len(answers) == 100:
            sequences.append(answers)

    return sequences

def generate_means_sequence(collated_answers_path):
    """
    Input: path to collated_answers.txt
    Output: list of floats (mean per question)
    """

    sequences = load_sequences(collated_answers_path)

    means = []

    for q in range(len(sequences[0])):

        values = []

        for student in sequences:
            val = student[q]
            if val != 0:
                values.append(val)

        if len(values) == 0:
            means.append(0)
        else:
            means.append(sum(values) / len(values))

    return means


def visualize_data(collated_answers_path, n):

    sequences = load_sequences(collated_answers_path)

    if n == 1:
        means = generate_means_sequence(collated_answers_path)

        plt.scatter(range(len(means)), means)
        plt.title("Mean Answer Per Question")
        plt.xlabel("Question")
        plt.ylabel("Mean Answer")

        plt.savefig("output/means_scatter_graph.png")
        plt.clf()

    elif n == 2:
        for seq in sequences:
            plt.plot(range(len(seq)), seq, alpha=0.3)

        plt.title("All Respondent Answer Sequences")
        plt.xlabel("Question")
        plt.ylabel("Answer")

        plt.savefig("output/all_sequences_line_graph.png")
        plt.clf()

    else:
        print("n must be 1 or 2")
        return