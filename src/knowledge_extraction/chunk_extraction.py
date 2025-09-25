import os
from typing import Optional

from models.message_models import DialogData, Chunk
from models.config_models import ChunkerConfig
from llm_tools.chunker_client import ChunkerClient
from utils.helpers import get_chunker_config


class DialogueChunker:
    """A class that processes dialogues and fills them with chunks based on a specified strategy.
    
    This class encapsulates the chunking process, allowing for easy configuration and application
    of different chunking strategies to dialogue data.
    """
    
    def __init__(self, chunker_strategy: str = "RecursiveChunker"):
        """Initialize the DialogueChunker with a specific chunking strategy.
        
        Args:
            chunker_strategy: The chunking strategy to use (default: RecursiveChunker)
                             Options include: SemanticChunker, RecursiveChunker, LateChunker, NeuralChunker
        """
        self.chunker_strategy = chunker_strategy
        chunker_config_dict = get_chunker_config(chunker_strategy)
        self.chunker_config = ChunkerConfig.model_validate(chunker_config_dict)
        self.chunker_client = ChunkerClient(self.chunker_config)
    
    def process_dialogue(self, dialogue: DialogData) -> list[Chunk]:
        """Process a dialogue by generating chunks and adding them to the DialogData object.
        
        Args:
            dialogue: The DialogData object to process
            
        Returns:
            A list of Chunk objects
        """
        return self.chunker_client.generate_chunks(dialogue)
    
    def save_chunking_results(self, dialogue: DialogData, output_path: Optional[str] = None) -> str:
        """Save the chunking results to a file and return the output path.
        
        Args:
            dialogue: The processed DialogData object with chunks
            output_path: Optional path to save the output (default: chunker_output_{strategy}.txt)
            
        Returns:
            The path where the output was saved
        """
        if not output_path:
            output_path = os.path.join(os.path.dirname(__file__), "..", "..", 
                                      f"chunker_output_{self.chunker_strategy.lower()}.txt")
        
        output_lines = []
        output_lines.append(f"=== Chunking Results ({self.chunker_strategy}) ===")
        output_lines.append(f"Dialogue ID: {dialogue.ref_id}")
        output_lines.append(f"Original conversation has {len(dialogue.context.msgs)} messages")
        output_lines.append(f"Total characters: {len(dialogue.content)}")
        
        output_lines.append(f"Generated {len(dialogue.chunks)} chunks:")
        for i, chunk in enumerate(dialogue.chunks):
            output_lines.append(f"  Chunk {i+1}: {len(chunk.content)} characters")
            output_lines.append(f"    Content preview: {chunk.content}...")
            if chunk.metadata:
                output_lines.append(f"    Metadata: {chunk.metadata}")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        
        print(f"Chunking results saved to: {output_path}")
        return output_path


