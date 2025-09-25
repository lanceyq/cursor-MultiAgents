from typing import Any
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from chonkie import SemanticChunker, RecursiveChunker, RecursiveRules, LateChunker, NeuralChunker

from models.config_models import ChunkerConfig
from models.message_models import DialogData, Chunk

class ChunkerClient:
    def __init__(self, chunker_config: ChunkerConfig):
        """Initialize ChunkerClient with specified configuration.
        
        Args:
            chunker_config: Configuration object containing chunker strategy,
                          embedding model, chunk size, and other parameters
        """
        self.embedding_model = chunker_config.embedding_model
        self.chunk_size = chunker_config.chunk_size
        self.threshold = chunker_config.threshold
        self.language = chunker_config.language
        self.skip_window = chunker_config.skip_window
        self.min_sentences = chunker_config.min_sentences
        self.min_characters_per_chunk = chunker_config.min_characters_per_chunk

        if chunker_config.chunker_strategy == "SemanticChunker":
            self.chunker = SemanticChunker(
                embedding_model=self.embedding_model,
                threshold=self.threshold,
                min_sentences_per_chunk=self.min_sentences,
                skip_window=self.skip_window,
            )
        elif chunker_config.chunker_strategy == "RecursiveChunker":
            self.chunker = RecursiveChunker.from_recipe(lang=self.language)
        elif chunker_config.chunker_strategy == "LateChunker":
            self.chunker = LateChunker(
                embedding_model=self.embedding_model,
                chunk_size = self.chunk_size,
                rules = RecursiveRules(),
                min_characters_per_chunk = self.min_characters_per_chunk,
            )
        elif chunker_config.chunker_strategy == "NeuralChunker":
            self.chunker = NeuralChunker(
                model=self.embedding_model,
                min_characters_per_chunk = self.min_characters_per_chunk,
            )

    
    def generate_chunks(self, dialogue: DialogData) -> list[Chunk]:
        """Generate chunks from dialogue content using the configured chunker.
        
        Args:
            dialogue: DialogData object containing the content to be chunked
            
        Returns:
            List of Chunk objects with content and metadata (start/end indices)
        """
        chunks = [
            Chunk(
                content=c.text,
                metadata={
                    "start_index": getattr(c, "start_index", None),
                    "end_index": getattr(c, "end_index", None),
                },
            )
            for c in self.chunker(dialogue.content)
        ]
        return chunks