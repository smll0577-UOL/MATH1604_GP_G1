"""
run_full_analysis_M4.py

Team Member 4 integration script for the MATH1604 group project.

This script runs the complete analysis pipeline by using the modules written by
Team Members 1, 2, and 3:

1. Download raw answer files from the cloud source.
2. Collate the downloaded files into one combined file.
3. Extract answer sequences from each respondent file.
4. Generate the mean answer sequence.
5. Produce visualisations.
6. Save a short text report describing possible patterns.

The script is designed to work both with the final .py files and with the
provided .pyc testing files, as long as they are importable under the expected
module names:

- data_extraction_M1
- data_preparation_M2
- data_analysis_M3

Recommended repository structure:

project_root/
    data/
    output/
    scripts/
        data_extraction_M1.py
        data_preparation_M2.py
        data_analysis_M3.py
        run_full_analysis_M4.py
    reviews/

Run from the project root with:

    python scripts/run_full_analysis_M4.py

or run from inside the scripts folder with:

    python run_full_analysis_M4.py
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Iterable, Sequence


# -----------------------------------------------------------------------------
# Import path handling
# -----------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Allow imports when running either from project root or from scripts/.
for path in (SCRIPT_DIR, PROJECT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:
    from data_preparation_M2 import download_answer_files, collate_answer_files
    from data_extraction_M1 import extract_answers_sequence, write_answers_sequence
    from data_analysis_M3 import generate_means_sequence, visualize_data
except ImportError as exc:
    raise ImportError(
        "Could not import one or more required team modules. Make sure these "
        "files are in the scripts folder, or in the same folder as this script: "
        "data_preparation_M2, data_extraction_M1, and data_analysis_M3."
    ) from exc


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DEFAULT_CLOUD_URL = (
    "https://raw.githubusercontent.com/"
    "fc-leeds/MATH1604_2025_2026_data/main"
)
DEFAULT_TOTAL_RESPONDENTS = 64
QUESTION_COUNT = 100
VALID_ANSWERS = {1, 2, 3, 4}


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def ensure_project_folders() -> None:
    """Create required data and output folders if they do not already exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



def respondent_file_path(respondent_id: int) -> Path:
    """
    Return the expected local path for one downloaded respondent file.

    Parameters
    ----------
    respondent_id:
        Positive integer identifying the respondent.

    Returns
    -------
    pathlib.Path
        Path to answers_respondent_<id>.txt inside the data folder.
    """
    return DATA_DIR / f"answers_respondent_{respondent_id}.txt"



def safe_extract_sequence(file_path: Path) -> list[int] | None:
    """
    Extract one respondent's answer sequence, returning None if extraction fails.

    Parameters
    ----------
    file_path:
        Path to the respondent's answer file.

    Returns
    -------
    list[int] | None
        A list of 100 answer values, or None if the file could not be processed.
    """
    try:
        sequence = extract_answers_sequence(str(file_path))
    except Exception as exc:  # noqa: BLE001 - keep pipeline robust for marking/demo.
        print(f"Warning: could not extract answers from {file_path}: {exc}")
        return None

    if not isinstance(sequence, list) or len(sequence) != QUESTION_COUNT:
        print(
            f"Warning: extracted sequence from {file_path} does not have "
            f"{QUESTION_COUNT} entries."
        )
        return None

    return sequence



def extract_all_sequences(total_respondents: int) -> list[list[int]]:
    """
    Extract answer sequences from all locally available respondent files.

    The extracted lists are also written to the output folder using the Team
    Member 1 writer function. Missing or invalid files are skipped with a warning.

    Parameters
    ----------
    total_respondents:
        Number of respondent files expected by the pipeline.

    Returns
    -------
    list[list[int]]
        All successfully extracted answer sequences.
    """
    sequences: list[list[int]] = []

    for respondent_id in range(1, total_respondents + 1):
        file_path = respondent_file_path(respondent_id)

        if not file_path.exists():
            print(f"Warning: {file_path} is missing; skipping respondent {respondent_id}.")
            continue

        sequence = safe_extract_sequence(file_path)
        if sequence is None:
            continue

        sequences.append(sequence)

        try:
            write_answers_sequence(sequence, respondent_id, str(OUTPUT_DIR))
        except Exception as exc:  # noqa: BLE001
            print(
                "Warning: sequence was extracted but could not be written for "
                f"respondent {respondent_id}: {exc}"
            )

    return sequences



def rounded_mean_sequence(means: Sequence[float]) -> list[int]:
    """
    Convert mean answer values into an approximate answer sequence.

    Since the true correct answers are not directly supplied, this uses the mean
    answer per question as an approximate signal and rounds each value to the
    nearest option from 1 to 4.

    Parameters
    ----------
    means:
        Sequence of mean answer values.

    Returns
    -------
    list[int]
        Rounded sequence containing only values 1, 2, 3, and 4.
    """
    rounded: list[int] = []
    for value in means:
        if value is None or not isinstance(value, (int, float)) or math.isnan(float(value)):
            rounded.append(0)
            continue
        rounded.append(min(4, max(1, round(float(value)))))
    return rounded



def period_error(sequence: Sequence[int], period: int) -> int:
    """
    Count mismatches when a sequence is compared with a repeating period.

    Parameters
    ----------
    sequence:
        Sequence of integers to test.
    period:
        Candidate repeating period.

    Returns
    -------
    int
        Number of positions that do not match the candidate periodic pattern.
    """
    mismatches = 0
    for index, value in enumerate(sequence):
        if value == 0:
            continue
        if value != sequence[index % period]:
            mismatches += 1
    return mismatches



def find_best_period(sequence: Sequence[int], max_period: int = 20) -> tuple[int, int]:
    """
    Find the candidate period with the fewest mismatches.

    Parameters
    ----------
    sequence:
        Approximate answer sequence to test.
    max_period:
        Largest period length to test.

    Returns
    -------
    tuple[int, int]
        Best period and number of mismatches for that period.
    """
    if not sequence:
        return 0, 0

    upper_limit = min(max_period, len(sequence))
    results = [(period, period_error(sequence, period)) for period in range(1, upper_limit + 1)]
    return min(results, key=lambda item: item[1])



def count_answers(values: Iterable[int]) -> dict[int, int]:
    """
    Count answer options 1, 2, 3, and 4 in a sequence.

    Parameters
    ----------
    values:
        Iterable of answer values.

    Returns
    -------
    dict[int, int]
        Dictionary mapping each valid option to its count.
    """
    counts = {answer: 0 for answer in sorted(VALID_ANSWERS)}
    for value in values:
        if value in counts:
            counts[value] += 1
    return counts



def save_analysis_report(
    means: Sequence[float],
    approximate_sequence: Sequence[int],
    sequences: Sequence[Sequence[int]],
    report_path: Path,
) -> None:
    """
    Save a short text report summarising the analysis output.

    Parameters
    ----------
    means:
        Mean answer value for each question.
    approximate_sequence:
        Rounded mean sequence used as an approximate pattern signal.
    sequences:
        Individual respondent answer sequences.
    report_path:
        Destination path for the text report.
    """
    best_period, mismatches = find_best_period(approximate_sequence)
    counts = count_answers(approximate_sequence)

    lines = [
        "MATH1604 Group Project - Team Member 4 Integration Report",
        "=" * 64,
        "",
        f"Number of respondent sequences extracted: {len(sequences)}",
        f"Number of questions analysed: {len(means)}",
        "",
        "First 20 mean answer values:",
        ", ".join(f"{value:.3f}" for value in means[:20]),
        "",
        "First 20 rounded mean values used as an approximate pattern signal:",
        ", ".join(str(value) for value in approximate_sequence[:20]),
        "",
        "Approximate answer-option counts from rounded means:",
        str(counts),
        "",
        "Simple periodicity check:",
        f"Best candidate period tested: {best_period}",
        f"Number of mismatches for this period: {mismatches}",
        "",
        "Interpretation note:",
        (
            "This report uses the mean answer sequence as an exploratory signal. "
            "The final review notebook should explain the plots and discuss whether "
            "the observed evidence is strong enough to suggest a deliberate pattern."
        ),
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------


def run_pipeline(
    cloud_url: str = DEFAULT_CLOUD_URL,
    total_respondents: int = DEFAULT_TOTAL_RESPONDENTS,
    make_plots: bool = True,
) -> None:
    """
    Run the full Team Member 4 analysis pipeline.

    Parameters
    ----------
    cloud_url:
        Base URL containing files named a1.txt, a2.txt, ..., aN.txt.
    total_respondents:
        Number of respondent files to attempt to download and analyse.
    make_plots:
        If True, call Team Member 3's visualisation function for scatter and line plots.
    """
    ensure_project_folders()

    print("Step 1/6: downloading answer files...")
    download_answer_files(cloud_url, str(DATA_DIR), total_respondents)

    print("Step 2/6: collating answer files...")
    collate_answer_files(str(DATA_DIR))

    collated_answers_path = OUTPUT_DIR / "collated_answers.txt"
    if not collated_answers_path.exists():
        # Some implementations may save relative to the current working directory.
        fallback_path = Path("output") / "collated_answers.txt"
        if fallback_path.exists():
            collated_answers_path = fallback_path
        else:
            raise FileNotFoundError(
                "collated_answers.txt was not found in the output folder after collation."
            )

    print("Step 3/6: extracting individual answer sequences...")
    sequences = extract_all_sequences(total_respondents)

    print("Step 4/6: generating mean answer sequence...")
    means = generate_means_sequence(str(collated_answers_path))

    if not isinstance(means, list) or len(means) != QUESTION_COUNT:
        raise ValueError(
            f"generate_means_sequence should return a list of {QUESTION_COUNT} floats."
        )

    approximate_sequence = rounded_mean_sequence(means)

    print("Step 5/6: creating visualisations...")
    if make_plots:
        visualize_data(str(collated_answers_path), 1)
        visualize_data(str(collated_answers_path), 2)
    else:
        print("Plot creation skipped because --no-plots was selected.")

    print("Step 6/6: saving analysis report...")
    report_path = OUTPUT_DIR / "team_member_4_analysis_report.txt"
    save_analysis_report(means, approximate_sequence, sequences, report_path)

    print("Pipeline completed successfully.")
    print(f"Collated answers: {collated_answers_path}")
    print(f"Analysis report:  {report_path}")



def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the integration script.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run the full MATH1604 Python quiz response analysis pipeline."
    )
    parser.add_argument(
        "--cloud-url",
        default=DEFAULT_CLOUD_URL,
        help="Base URL containing a1.txt, a2.txt, ..., aN.txt files.",
    )
    parser.add_argument(
        "--total-respondents",
        type=int,
        default=DEFAULT_TOTAL_RESPONDENTS,
        help="Number of respondent files to attempt to download and analyse.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Run the pipeline without displaying plots.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_pipeline(
        cloud_url=args.cloud_url,
        total_respondents=args.total_respondents,
        make_plots=not args.no_plots,
    )
