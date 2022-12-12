import sys

from src.base.utils import clean_string


if __name__ == "__main__":
    sys.stdout.write(clean_string(sys.argv[1]))
    sys.stdout.flush()
