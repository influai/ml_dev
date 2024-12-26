import sys
from pathlib import Path
from time import sleep
import pickle

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from tqdm import tqdm


AD_PREV_TEXTS_FOLDER = Path("/home/deniskirbaba/Documents/influai-data/embeddings/ad_prev_texts_splitted")
SUMMARY_PROMPT_PATH = Path("./summary_prompt.txt")

SUMMARIES_FOLDER = Path("/home/deniskirbaba/Documents/influai-data/embeddings/ad_prev_summaries")
SUMMARIES_FOLDER.mkdir(exist_ok=True)

def main():
    """
    Script for creating summary using Mistral AI.

    Need 3 cmd params:
        1. str: MISTRAL_API_KEY
        2. str: path to .pkl file with list of file name stems to summarized
    """
    mistral_api_key, name_stems_path = sys.argv[1:]

    with open(SUMMARY_PROMPT_PATH) as f:
        summary_prompt = f.read()

    llm = ChatMistralAI(model_name="mistral-large-latest", api_key=mistral_api_key, timeout=60 * 3)
    prompt_1 = ChatPromptTemplate.from_messages(
        [
            ("system", summary_prompt),
            ("user", "{doc}"),
        ]
    )
    chain = prompt_1 | llm | StrOutputParser()

    with open(name_stems_path, "rb") as f:
        name_stems = pickle.load(f)

    for stem in tqdm(name_stems):
        with open(AD_PREV_TEXTS_FOLDER / (stem + ".txt"), "r") as f:
            doc = f.read()

        while True:
            try:
                summary = chain.invoke({"doc": doc})
                break
            except Exception as e:
                print(e)
                sleep(5)

        with open(SUMMARIES_FOLDER / f"{stem}.txt", "w") as f:
            f.write(summary)


if __name__ == "__main__":
    main()