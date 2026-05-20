import matplotlib.pyplot as plt
from data_extraction_M1 import extract_answers_sequence


def generate_means_sequence(collated_answers_path):
    """
    Input: path to collated_answers.txt
    Output: list of 100 floats (mean per question)
    """

    sequences = extract_answers_sequence(collated_answers_path)

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
    """
    n=1 → scatter plot of means
    n=2 → line plot of all respondent sequences
    """

    sequences = extract_answers_sequence(collated_answers_path)

    if n == 1:
        means = generate_means_sequence(collated_answers_path)

        plt.scatter(range(len(means)), means)
        plt.title("Mean of Answers Per Question")
        plt.xlabel("Question")
        plt.ylabel("Mean Answer")
        plt.show()

    elif n == 2:
        for seq in sequences:
            plt.plot(range(len(seq)), seq, alpha=0.3)

        plt.title("All Respondent Answer Sequences")
        plt.xlabel("Question")
        plt.ylabel("Answer Value")
        plt.show()

    else:
        print("n must be 1 or 2")