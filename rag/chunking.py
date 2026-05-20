import re
import uuid

from utils.logger import logger
from config.settings import CHUNK_SIZE,CHUNK_OVERLAP
from config.error_codes import ErrorCode

class HierarchicalChunker:

    @staticmethod
    def identify_sections(text):
        section_pattern = (r"(?:^|\n)([A-Z][A-Z\s\-/]{3,})\n")
        matches = list(re.finditer(section_pattern,text))

        sections = []

        if not matches:
            return [
                {
                    "title": "DOCUMENT",
                    "content": text
                }
            ]

        for i in range(len(matches)):

            start = matches[i].start()

            end = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(text)
            )

            title = matches[i].group(1).strip()

            content = text[start:end]

            sections.append({
                "title": title,
                "content": content
            })

        return sections

    @staticmethod
    def create_child_chunks(
        parent_id,
        section_title,
        content,
        source_file
    ):

        words = content.split()
        child_chunks = []
        start = 0

        while start < len(words):

            end = start + CHUNK_SIZE

            chunk_words = words[start:end]

            chunk_text = " ".join(
                chunk_words
            )

            child_chunks.append({

                "chunk_id": str(
                    uuid.uuid4()
                ),

                "parent_id": parent_id,
                "section_title": (
                    section_title
                ),
                "source_file": (
                    source_file
                ),
                "chunk_text": (
                    chunk_text
                ),
                "token_count": len(
                    chunk_words
                )
            })

            start += (
                CHUNK_SIZE -
                CHUNK_OVERLAP
            )

        return child_chunks

    @staticmethod
    def chunk_text(
        text,
        source_file
    ):

        try:
            logger.info("Starting hierarchical chunking.")

            sections = (
                HierarchicalChunker
                .identify_sections(text)
            )

            all_chunks = []

            for section in sections:

                parent_id = str(
                    uuid.uuid4()
                )

                child_chunks = (

                    HierarchicalChunker
                    .create_child_chunks(

                        parent_id=parent_id,

                        section_title=(
                            section["title"]
                        ),

                        content=(
                            section["content"]
                        ),

                        source_file=(
                            source_file
                        )
                    )
                )
                all_chunks.extend(
                    child_chunks
                )

            logger.info(
                f"Generated "
                f"{len(all_chunks)} chunks.")

            return all_chunks

        except Exception as e:

            logger.exception("Chunking failed.")

            raise RuntimeError(ErrorCode.CHUNKING_ERROR) from e