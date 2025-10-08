# mcq_prompt_template_maker
Prompt Template Generator For MCQ Based on Files

## Description

A Python CLI tool that analyzes text files and generates multiple-choice question (MCQ) prompt templates using OpenAI's API. The tool infers targeted learning outcomes from the input text and creates 3-5 tailored MCQ templates, saving the results in markdown format.

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

```bash
python3 generate_prompts.py --in <input_directory> --out <output_directory> --model <openai_model>
```

### Arguments

- `--in`: Input directory containing `.txt` files to process
- `--out`: Output directory where `.md` files will be saved
- `--model`: OpenAI model to use (e.g., `gpt-4`, `gpt-3.5-turbo`, `gpt-4-turbo`)

### Example

```bash
python3 generate_prompts.py --in examples/input --out examples/output --model gpt-3.5-turbo
```

This will:
1. Read all `.txt` files from `examples/input/`
2. For each file, call OpenAI to infer learning outcomes and generate MCQ prompt templates
3. Save the results as markdown files in `examples/output/` with the same basename

## Output Format

Each generated markdown file includes:
- **Title**: Descriptive title for the content
- **Context**: Source file information
- **Learning Outcomes**: Identified learning objectives (2-3 items)
- **MCQ Prompt Templates**: 3-5 numbered templates with placeholders and purposes
- **Metadata**: Source file, model used, and template count

## Features

- ✓ Type hints throughout the codebase
- ✓ Comprehensive error handling
- ✓ Support for multiple text files in batch processing
- ✓ Automatic output directory creation
- ✓ Clear progress reporting during execution

## Requirements

- Python 3.7+
- OpenAI API key
- Dependencies listed in `requirements.txt`
