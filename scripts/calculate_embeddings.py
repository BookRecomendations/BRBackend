import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
import logging
import argparse
import faiss


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('embedding.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate embeddings and build Annoy index for book descriptions.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output_file", type=str, default="annoy_index.ann",
                        help="Path for the output Annoy index file.")
    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging()
    logging.info("Starting process.")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Using device: {device}")

    model = SentenceTransformer('thenlper/gte-base').to(device)

    df = pd.read_csv(args.input_file, compression='gzip')
    sentences = df['description'].tolist()

    logging.info("Encoding sentences.")
    # Convert embeddings to NumPy array for FAISS
    embeddings = model.encode(sentences, batch_size=32, show_progress_bar=True, convert_to_numpy=True, device=device.index)

    logging.info("Encoded sentences.")

    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]  # Dimension of embeddings

    # Creating a FAISS index
    # Here we use IndexFlatIP for simplicity, consider using other indexes for larger datasets
    index = faiss.IndexFlatIP(dim)
    if device == 'cuda':
        # Use GPU
        faiss_res = faiss.StandardGpuResources()  # Use all GPU resources
        gpu_index = faiss.index_cpu_to_gpu(faiss_res, 0, index)
        gpu_index.add(embeddings)
        # gpu_index.add(embeddings)  # Add vectors to the index
    else:
        index.add(embeddings)  # If using CPU, add directly to the index

    logging.info("FAISS index built for cosine similarity.")
    # Save the index
    faiss.write_index(gpu_index if device == 'cuda' else index, args.output_file)
    logging.info(f"FAISS index saved to {args.output_file}")


if __name__ == "__main__":
    main()
