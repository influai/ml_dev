import itertools
import json
import logging
import sys
from pathlib import Path
from time import sleep

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


BATCH_SAVE = 500  # Number of summaries to save to file
SUMMARY_PROMPT_PATH = Path("summary_prompt.txt")
OUT_SUMMARIES_FOLDER_PATH = Path(
    "/home/deniskirbaba/Documents/influai-data/embeddings/ad_prev_summaries/"
)


def save(summaries: dict, prefix: str, summaries_created: int):
    """
    Save the summaries
    """
    output_file = OUT_SUMMARIES_FOLDER_PATH / f"{prefix}_{summaries_created}.json"
    try:
        with open(output_file, "w") as f:
            json.dump(summaries, f, ensure_ascii=False)
        logging.info(f"Summaries saved to {output_file}.")
    except Exception as e:
        logging.error(f"Error saving summaries to {output_file}: {e}")


def main():
    """
    Script for creating summary of legal practice docs, using Mistral AI.

    Requires 2 command-line arguments:
        1. str: MISTRAL_API_KEY
        2. str: path to file with ad_prev_texts
    """
    try:
        mistral_api_key, ad_prev_texts_path = sys.argv[1:]
        ad_prev_texts_path = Path(ad_prev_texts_path)
        logging.info("Starting the script.")
    except ValueError:
        logging.error(
            "Invalid number of arguments. Provide MISTRAL_API_KEY and the path to ad_prev_texts."
        )
        sys.exit(1)

    # Read the summary prompt
    try:
        with open(SUMMARY_PROMPT_PATH, "r") as f:
            summary_prompt = f.read()
        logging.info("Loaded summary prompt from file.")
    except FileNotFoundError:
        logging.error(
            "summary_prompt.txt not found. Ensure the file exists in the script's directory."
        )
        sys.exit(1)

    # Initialize the Mistral AI model
    try:
        llm = ChatMistralAI(
            model_name="mistral-large-latest", api_key=mistral_api_key, timeout=60 * 3
        )
        logging.info("Initialized Mistral AI model.")
    except Exception as e:
        logging.error(f"Error initializing Mistral AI model: {e}")
        sys.exit(1)

    prompt_1 = ChatPromptTemplate.from_messages(
        [
            ("system", summary_prompt),
            ("user", "{doc}"),
        ]
    )
    chain = prompt_1 | llm | StrOutputParser()

    # Load the ad_prev_texts data
    try:
        with open(ad_prev_texts_path, "r") as f:
            ad_prev_texts = json.load(f)
        logging.info(f"Loaded ad_prev_texts from {ad_prev_texts_path}.")
    except FileNotFoundError:
        logging.error(f"File {ad_prev_texts_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {ad_prev_texts_path}: {e}")
        sys.exit(1)

    OUT_SUMMARIES_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
    logging.info(f"Summaries will be saved in {OUT_SUMMARIES_FOLDER_PATH}.")

    summaries = {}
    summaries_created = 0

    # Process each ad post
    for ad_post_id, prev_posts in tqdm(ad_prev_texts.items(), desc="Processing posts"):
        # If we have posts previous to the target ad post
        if prev_posts:
            doc = "\n===\n".join(itertools.chain.from_iterable(prev_posts[1]))

            while True:
                try:
                    summary = chain.invoke({"doc": doc})
                    break
                except Exception as e:
                    logging.error(f"Error generating summary for ad_post_id {ad_post_id}: {e}")
                    sleep(5)

            summaries[ad_post_id] = summary
            summaries_created += 1

            if summaries_created % BATCH_SAVE == 0:
                save(summaries, ad_prev_texts_path.stem.split("_")[-1], summaries_created)
                summaries = {}

    # Save the last batch, if any
    if summaries:
        save(summaries, ad_prev_texts_path.stem.split("_")[-1], summaries_created)


if __name__ == "__main__":
    main()
