# DocuSort

DocuSort is a desktop application for sorting scanned and digital documents into a consistent target folder structure while standardizing their filenames.

## Project goals

- select a source directory and process files one by one
- choose whether files in source subdirectories are included
- show the target folder tree for placement
- prefill document metadata such as title, company, and date
- let the user review and correct metadata before moving the file
- rename files into a standardized format like DATE_CATEGORY_NAME
- detect name conflicts and give the user clear replacement choices

## Tech stack

- Python
- PySide6 for the desktop GUI
- pathlib and shutil for file system handling
- optional extraction libraries for PDFs, DOCX, OCR, and scanned input

## Run locally with Pipenv

Python 3.13 is the version already installed and available in this environment, so it will be used for the project.

1. Install Pipenv if it is not already available
   python -m pip install pipenv
2. Install the project dependencies
   pipenv install --python 3.13
3. Start the app in the Pipenv environment
   pipenv run python main.py

Optional:
- Run a shell inside the environment:
  pipenv shell
- Start with the custom script:
  pipenv run start

## Download

Download the latest Windows executable from the [latest GitHub release](https://github.com/schoenfelder1997/DocuSort/releases/latest/download/DocuSort.exe).

To publish a release, run the **Release** workflow from the GitHub Actions tab and choose a major, minor, or patch version bump. The workflow builds the executable and attaches it to the release.

## Notes

This is the initial working scaffold. The first version focuses on the core review-and-sort workflow, while AI-based analysis and smart folder suggestions are planned as future enhancements.
