import urllib.request
import os


def download_answer_files(cloud_url: str, path_to_data_folder: str, total_respondents: int) -> None:
  """Download the original data file and integrate it."""
  os.makedirs(path_to_data_folder, exist_ok=True)

  for i in range(1, total_respondents + 1):
        url = f"{cloud_url}/a{i}.txt"
        destination = os.path.join(path_to_data_folder, f"answers_respondent_{i}.txt")
        try:
            urllib.request.urlretrieve(url, destination)
            print(f"Downloaded: answers_respondent_{i}.txt")
        except Exception as e:
            print(f"Warning: could not download a{i}.txt: {e}")
 
    print("Download step complete.")
 
 
def collate_answer_files(data_folder_path: str) -> None:
    """
    Integrate all files together and use '*' to divide them..
    """
    files = [
        f for f in os.listdir(data_folder_path)
        if f.startswith("answers_respondent_") and f.endswith(".txt")
    ]
    files.sort(key=lambda x: int(x.split("_")[-1].replace(".txt", "")))
 
    if not files:
        raise FileNotFoundError(
            f"No respondent answer files found in '{data_folder_path}'."
        )
 
    parent_dir = os.path.dirname(os.path.abspath(data_folder_path))
    output_dir = os.path.join(parent_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    collated_path = os.path.join(output_dir, "collated_answers.txt")
 
    with open(collated_path, "w", encoding="utf-8") as outfile:
        for index, file_name in enumerate(files):
            file_path = os.path.join(data_folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as infile:
                content = infile.read().strip()
            outfile.write(content)
            if index != len(files) - 1:
                outfile.write("\n*\n")
 
    print(f"Collated file created: {collated_path}")
    print(f"Number of files collated: {len(files)}")
