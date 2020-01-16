import fire
from dotenv import load_dotenv

from cli import Commands

if __name__ == "__main__":
    load_dotenv()
    fire.Fire(Commands)
