import argparse
import concurrent.futures
import os
import re
from pprint import pprint
from subprocess import call
from tempfile import TemporaryDirectory

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

    print("Fetching file list...")
    files = hf.list_repo_files(model_repo)

    if is_gguf:
        # Get preferred gguf
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

        with TemporaryDirectory() as td:
            f_path = os.path.join(td, "links.txt")
            with open(f_path, "w") as f:
                f.writelines(
                    [
                        f"https://huggingface.co/{model_repo}/resolve/main/{file}?download=true#{file}\n  out={file}\n"
                        for file in dl_files
                    ]
                )

            call(
                [
                    "aria2c",
                    "-j",
                    "16",
                    "-s",
                    "16",
                    "-x",
                    "16",
                    "-c",
                    "-k",
                    "1M",
                    "-d",
                    f"{LOCAL_DIR}/{model_repo}",
                    "-i",
                    f_path,
                ]
            )

    else:
        if not os.path.exists(f"{LOCAL_DIR}/{model_repo}"):
            os.makedirs(f"{LOCAL_DIR}/{model_repo}", exist_ok=True)

        with TemporaryDirectory() as td:
            f_path = os.path.join(td, "links.txt")
            with open(f_path, "w") as f:
                f.writelines(
                    [
                        f"https://huggingface.co/{model_repo}/resolve/main/{file}?download=true#{file}\n  out={file}\n"
                        for file in files
                    ]
                )

            call(
                [
                    "aria2c",
                    "-j",
                    "16",
                    "-s",
                    "16",
                    "-x",
                    "16",
                    "-c",
                    "-k",
                    "1M",
                    "-d",
                    f"{LOCAL_DIR}/{model_repo}",
                    "-i",
                    f_path,
                ]
            )
