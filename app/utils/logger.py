import logging
from pathlib import Path

def setup_logger(path="logs/pipeline.log"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(path, encoding="utf-8"), logging.StreamHandler()]
    )
# import logging
# from pathlib import Path


# def setup_logger(log_file):
#     log_path = Path(log_file)
#     log_path.parent.mkdir(parents=True, exist_ok=True)

#     logger = logging.getLogger()
#     logger.setLevel(logging.INFO)

#     if not logger.handlers:
#         handler = logging.FileHandler(log_path, encoding="utf-8")
#         formatter = logging.Formatter(
#             "%(asctime)s - %(levelname)s - %(message)s"
#         )
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)

#     return logger


# def get_logger(log_file=None):
#     if log_file is not None:
#         setup_logger(log_file)

#     return logging.getLogger()
