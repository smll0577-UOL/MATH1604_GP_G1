import matplotlib.pyplot as plt
from data_extraction_M1 import extract_answers_sequence

def load_sequences(collated_answers_path):
    """
    Extracts all sequences of respondent answers from collated answers file.
    Based on layout of respondents in blocks separated by asterisks.

    Parameters
    ----------
    collated_answers_path : str
        Path to the collated answers file.

    Returns/Outputs
    ---------------
    sequences : list[list[int]]
        List of answer sequences each containing 100 integers:
        - 1, 2, 3, 4 for selected answers
        - 0 for non-answers

    Important Assumptions
    ---------------------
    - Each respondent block contains 100 questions.
    - Each question is formatted the same with a question line then 4 answer lines
    - Answers are selected by marking [X].

    Possible exceptions/edge cases
    ------------------------------
    A respondent block might contain more/less than 100 answers and not be properly extracted.

    """
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
    Calculates the mean of respondent's answers for each question.

    Parameters
    ----------
    collated_answers_path : str
        Path to the collated answers file.

    Returns/Outputs
    ---------------
    list[float]
        List of means of respondents' answers to each question.
        Zeroes (non-answers) are not included in the mean.

    Important Assumptions
    ---------------------
    - Respondent answers have been extracted and collated properly.

    Possible exceptions/edge cases
    ------------------------------
    - Questions that no students answered would have a mean of 0.
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
    """
    Visualises results as a scatter plot or a line plot based on value of n.
    Plots are saved as images in output folder.

    Parameters
    ----------
    collated_answers_path : str
        Path to the collated answers file

    n : int
        Deteremines the visualisation:
        1 = scatter graph of means per question; 2 = line graph of respondent's individual answers.

    Returns/Outputs:
    ----------------
    png
        Images of scatter and line graphs saved in output folder.
    Printed string
        Error message if n is not equal to 1 or 2

    Important Assumptions:
    ----------------------
    - Assumes data has been extracted properly.
    - Assumes means have been computed successfully.

    Possible exceptions/edge cases
    ------------------------------
    - If n is not equal to 1 or 2, an error message is printed
    """

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
        print("Error: n must be 1 or 2")
        return