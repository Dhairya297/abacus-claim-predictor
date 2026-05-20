import os
import sys
import fitz
import docx

from config.settings import PROJECT_ROOT
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.logger import logger
from config.error_codes import ErrorCode

class DataLoader:
    @staticmethod
    def load_txt(file_path):
        with open(file_path,"r",encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def load_document(file_path):
        try:
            logger.info(f"Loading document: {file_path}")

            if not os.path.exists(file_path):
                raise FileNotFoundError(ErrorCode.FILE_NOT_FOUND)

            extension = os.path.splitext(file_path)[1].lower()

            if extension == ".txt":
                text = DataLoader.load_txt(file_path)

            else:
                raise ValueError(f"Unsupported file format: {extension}")

            logger.info("Document loaded successfully.")

            return text

        except Exception as e:

            logger.exception(
                "Document loading failed."
            )

            raise RuntimeError(
                ErrorCode.FILE_READ_ERROR
            ) from e