import argparse
import concurrent.futures
import os
import re
from pprint import pprint

import huggingface_hub as hf

LOCAL_DIR = "/home/ubuntu/models"
GGUF_PREF = ["Q4_K_M", "Q4_K_S"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model", help="name of the model to download")

    args = parser.parse_args()

    model_or_url: str = args.model

    # Check if model is a link or model only
    # https://huggingface.co/deepseek-ai/DeepSeek-R1 --> Huggingface model repo link
    # https://huggingface.co/bartowski/DeepSeek-R1-GGUF --> Huggingface model repo link (GGUF)
    # deepseek-ai/DeepSeek-R1 --> model repo

    if model_or_url.startswith("https://huggingface.co"):
        pattern = r"https://huggingface.co/([^/]+)/([^/]+)"
        match = re.search(pattern, model_or_url)

        if match:
            model_repo = f"{match.group(1)}/{match.group(2)}"
        else:
            raise ValueError(f"Invalid link: {model_or_url}")
    elif r"/" in model_or_url:
        if len(model_or_url.split("/")) == 2:
            model_repo = model_or_url
        else:
            raise ValueError(f"Invalid model: {model_or_url}")

        pass

    is_gguf = "gguf" in model_repo.lower()

    files = hf.list_repo_files(model_repo)

    if is_gguf:

        def download_file(file):
            os.system(
                f"wget -O {LOCAL_DIR}/{file} https://huggingface.co/{model_repo}/resolve/main/{file}?download=true"
            )

        for _gguf in GGUF_PREF:
            dl_files = [file for file in files if _gguf in file]

            if dl_files:
                break
        else:
            for file in files:
                if file.endswith(".gguf"):
                    dl_files = [file]
            else:
                raise ValueError("No valid GGUF file found!")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(dl_files)
        ) as executor:
            executor.map(download_file, dl_files)
    else:
        if not os.path.exists(f"{LOCAL_DIR}/{model_repo}"):
            os.makedirs(f"{LOCAL_DIR}/{model_repo}", exist_ok=True)

        def download_file(file):
            os.system(
                f"wget -O {LOCAL_DIR}/{model_repo}/{file} https://huggingface.co/{model_repo}/resolve/main/{file}?download=true"
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(files)) as executor:
            executor.map(download_file, files)
