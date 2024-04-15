import pandas as pd
from tqdm.auto import tqdm
from transformers import pipeline
import torch
import argparse
import logging
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

summarized_count = 0


def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    # Formatter for our handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler('summarization.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create a stream handler for logging to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logging.info("Logging is set up.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Summarize book descriptions from a CSV file.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the output CSV file.")
    parser.add_argument("--max_summary_length", type=int, default=512, help="Maximum length of the summary.")
    parser.add_argument("--min_summary_length", type=int, default=256, help="Minimum length of the summary.")
    return parser.parse_args()


def desc_summarize(description: str, summarizer, max_length, min_length):
    global summarized_count

    if len(description.split()) > 512:
        try:
            summarized_text = summarizer(description, max_length=max_length, min_length=min_length)[0]["summary_text"]
            summarized_count += 1
            return summarized_text
        except Exception as e:
            logging.error(f"Error summarizing description: {e}")
            return description
    else:
        return description


def main():
    args = parse_arguments()

    setup_logging()
    logging.info("Starting summarization process.")

    tqdm.pandas()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Using device: {device}")

    summarizer = pipeline(
        "summarization",
        "pszemraj/long-t5-tglobal-base-16384-book-summary",
        device=device.index,
    )

    logging.info(f"Loading data from {args.input_file}")
    df = pd.read_csv(args.input_file, compression='gzip')

    logging.info("Starting to summarize descriptions.")
    df['description'] = df['description'].progress_apply(
        lambda desc: desc_summarize(desc, summarizer, args.max_summary_length, args.min_summary_length))

    df.to_csv(args.output_file, compression='gzip', index=True)
    logging.info(f"Summarization completed. Output file saved to {args.output_file}")
    logging.info(f"Summarized {summarized_count} descriptions.")


if __name__ == "__main__":
    main()
