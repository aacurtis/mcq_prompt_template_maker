#!/usr/bin/env python3
"""
CLI tool to generate MCQ prompt templates from text files using OpenAI API.

This script reads text files from an input directory, uses OpenAI to infer learning
outcomes and generate MCQ prompt templates, then saves the results as markdown files.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments containing input directory, 
                           output directory, and OpenAI model name.
    """
    parser = argparse.ArgumentParser(
        description="Generate MCQ prompt templates from text files using OpenAI API"
    )
    parser.add_argument(
        "--in",
        dest="input_dir",
        required=True,
        help="Input directory containing .txt files"
    )
    parser.add_argument(
        "--out",
        dest="output_dir",
        required=True,
        help="Output directory for generated .md files"
    )
    parser.add_argument(
        "--model",
        dest="model",
        required=True,
        help="OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)"
    )
    return parser.parse_args()


def read_text_file(file_path: Path) -> str:
    """
    Read the contents of a text file.
    
    Args:
        file_path: Path to the text file.
        
    Returns:
        str: Contents of the file.
        
    Raises:
        IOError: If file cannot be read.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Failed to read file {file_path}: {str(e)}")


def generate_mcq_prompts(text: str, model: str, client: OpenAI) -> Dict[str, any]:
    """
    Use OpenAI API to infer learning outcomes and generate MCQ prompt templates.
    
    Args:
        text: Input text content to analyze.
        model: OpenAI model to use.
        client: OpenAI client instance.
        
    Returns:
        Dict containing title, learning_outcomes, and mcq_templates.
        
    Raises:
        Exception: If OpenAI API call fails.
    """
    try:
        # Create a prompt for OpenAI to generate MCQ templates
        system_prompt = """You are an educational content expert. Your task is to:
1. Analyze the given text and identify 2-3 key learning outcomes
2. Generate 3-5 multiple choice question (MCQ) prompt templates tailored to those outcomes
3. Each template should include placeholders like [TOPIC], [CONCEPT], etc.

Respond in JSON format with:
{
  "title": "Brief descriptive title",
  "learning_outcomes": ["outcome1", "outcome2", "outcome3"],
  "mcq_templates": [
    {
      "template": "Question template with [PLACEHOLDERS]",
      "purpose": "Brief description of what this template tests"
    }
  ]
}"""

        user_prompt = f"Analyze this text and generate MCQ prompt templates:\n\n{text}"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        raise Exception(f"OpenAI API call failed: {str(e)}")


def generate_markdown(data: Dict[str, any], original_filename: str, model: str) -> str:
    """
    Generate markdown output from the MCQ prompt data.
    
    Args:
        data: Dictionary containing title, learning_outcomes, and mcq_templates.
        original_filename: Name of the original input file.
        model: OpenAI model used for generation.
        
    Returns:
        str: Formatted markdown content.
    """
    md_lines = []
    
    # Title
    title = data.get("title", "MCQ Prompt Templates")
    md_lines.append(f"# {title}\n")
    
    # Context section
    md_lines.append("## Context\n")
    md_lines.append(f"Generated from: `{original_filename}`\n")
    
    # Learning Outcomes
    if "learning_outcomes" in data and data["learning_outcomes"]:
        md_lines.append("## Learning Outcomes\n")
        for outcome in data["learning_outcomes"]:
            md_lines.append(f"- {outcome}")
        md_lines.append("")
    
    # MCQ Templates
    md_lines.append("## MCQ Prompt Templates\n")
    templates = data.get("mcq_templates", [])
    for i, template_data in enumerate(templates, 1):
        template = template_data.get("template", "")
        purpose = template_data.get("purpose", "")
        md_lines.append(f"### {i}. {purpose}\n")
        md_lines.append(f"```")
        md_lines.append(template)
        md_lines.append(f"```\n")
    
    # Metadata section
    md_lines.append("## Metadata\n")
    md_lines.append(f"- **Source File**: {original_filename}")
    md_lines.append(f"- **Model Used**: {model}")
    md_lines.append(f"- **Templates Generated**: {len(templates)}")
    md_lines.append("")
    
    return "\n".join(md_lines)


def save_markdown(content: str, output_path: Path) -> None:
    """
    Save markdown content to a file.
    
    Args:
        content: Markdown content to save.
        output_path: Path where the file should be saved.
        
    Raises:
        IOError: If file cannot be written.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Failed to write file {output_path}: {str(e)}")


def process_text_files(input_dir: Path, output_dir: Path, model: str, client: OpenAI) -> None:
    """
    Process all .txt files in the input directory and generate markdown outputs.
    
    Args:
        input_dir: Path to input directory containing .txt files.
        output_dir: Path to output directory for .md files.
        model: OpenAI model to use.
        client: OpenAI client instance.
        
    Raises:
        FileNotFoundError: If input directory doesn't exist or contains no .txt files.
    """
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all .txt files
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {input_dir}")
    
    print(f"Found {len(txt_files)} .txt file(s) to process")
    
    # Process each file
    for txt_file in txt_files:
        print(f"\nProcessing: {txt_file.name}")
        
        try:
            # Read text content
            text_content = read_text_file(txt_file)
            print(f"  Read {len(text_content)} characters")
            
            # Generate MCQ prompts using OpenAI
            print(f"  Calling OpenAI API with model: {model}")
            mcq_data = generate_mcq_prompts(text_content, model, client)
            
            # Generate markdown
            markdown_content = generate_markdown(mcq_data, txt_file.name, model)
            
            # Save to output file
            output_file = output_dir / f"{txt_file.stem}.md"
            save_markdown(markdown_content, output_file)
            print(f"  Saved: {output_file}")
            
        except Exception as e:
            print(f"  ERROR processing {txt_file.name}: {str(e)}", file=sys.stderr)
            continue


def main() -> None:
    """
    Main entry point for the CLI script.
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Convert to Path objects
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        model = args.model
        
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY environment variable not set", file=sys.stderr)
            sys.exit(1)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Process all text files
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Model: {model}")
        
        process_text_files(input_dir, output_dir, model, client)
        
        print("\n✓ All files processed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
