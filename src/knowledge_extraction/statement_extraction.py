import os
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field

from models.message_models import DialogData, Statement
from llm_tools.openai_client import OpenAIClient
from utils.helpers import render_statement_extraction_prompt
from ontology.ontology import LABEL_DEFINITIONS, StatementType, TemporalInfo, RelevenceInfo

class ExtractedStatement(BaseModel):
    """Schema for extracted statement from LLM"""
    statement: str = Field(..., description="The extracted statement text")
    statement_type: str = Field(..., description="FACT, OPINION,SUGGESTION or PREDICTION")
    temporal_type: str = Field(..., description="STATIC, DYNAMIC, ATEMPORAL")
    relevence: str = Field(..., description="RELEVANT, IRRELEVANT")

class StatementExtractionResponse(BaseModel):
    """Schema for the complete response from statement extraction"""
    statements: List[ExtractedStatement] = Field(..., description="List of extracted statements")

class StatementExtractor:
    """Class for extracting statements from dialog chunks using LLM"""
    
    def __init__(self, llm_client: OpenAIClient):
        """Initialize the StatementExtractor with an LLM client
        
        Args:
            llm_client: OpenAIClient instance for processing
        """
        self.llm_client = llm_client
    
    async def _extract_statements(self, chunk, group_id: Optional[str] = None) -> List[Statement]:
        """Process a single chunk and return extracted statements
        
        Args:
            chunk: Chunk object to process
            group_id: Group ID to assign to all statements in this chunk
            
        Returns:
            List of Statement objects extracted from the chunk
        """
        # Prepare the chunk content for processing
        chunk_content = chunk.content
        
        # Render the prompt using helper function
        prompt_content = render_statement_extraction_prompt(
            chunk_content=chunk_content,
            definitions=LABEL_DEFINITIONS,
            json_schema=StatementExtractionResponse.model_json_schema()
        )
        
        # Create messages for LLM
        messages = [
            {"role": "system", "content": "You are an expert at extracting and classifying statements from conversational text. Follow the provided instructions carefully and return valid JSON."},
            {"role": "user", "content": prompt_content}
        ]
        
        try:
            # Get structured response from LLM
            response = await self.llm_client.response_structured(messages, StatementExtractionResponse)
            
            # Convert extracted statements to Statement objects
            chunk_statements = []
            for extracted_stmt in response.statements:
                # Map string types to enum types
                stmt_type = StatementType(extracted_stmt.statement_type)
                temporal_type = TemporalInfo(extracted_stmt.temporal_type)
                relevence_type = RelevenceInfo(extracted_stmt.relevence)
                
                chunk_statement = Statement(
                    statement=extracted_stmt.statement,
                    stmt_type=stmt_type,
                    temporal_info=temporal_type,
                    relevence_info=relevence_type,
                    chunk_id=chunk.id,
                    group_id=group_id
                )
                chunk_statements.append(chunk_statement)
            
            return chunk_statements
                
        except Exception as e:
            print(f"Error processing chunk: {e}")
            return None 
    
    async def extract_statements(self, dialog_data: DialogData, limit_chunks: int = None) -> List[List[Statement]]:
        """Extract statements from a DialogData object.
        
        Args:
            dialog_data: The DialogData object containing chunks. 
            limit_chunks: Optional limit on the number of chunks to process.
        """
        # Determine how many chunks to process
        chunks_to_process = dialog_data.chunks[:limit_chunks] if limit_chunks else dialog_data.chunks
        
        print(f"Processing {len(chunks_to_process)} chunks for statement extraction")
        
        # TODO: Add chunk context for statement extraction
        # Process all chunks concurrently, passing the group_id from dialog_data
        results = await asyncio.gather(
            *[self._extract_statements(chunk, dialog_data.group_id) for chunk in chunks_to_process], 
            return_exceptions=True
        )

        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, list) and result is not None:
                valid_results.append(result)
            else:
                print(f"Error in statement extraction: {result}")
                valid_results.append([])   
        
        return valid_results
        
    def save_statements(self, statements: List[Statement], output_path: str = None) -> str:
        """Save the extracted statements to a file and return the output path.
        
        Args:
            statements: List of Statement objects to save
            output_path: Optional path to save the output (default: statement_extraction.txt)
            
        Returns:
            The path where the output was saved
        """
        if not output_path:
            output_path = os.path.join(os.path.dirname(__file__), "..", "statement_extraction.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Extracted Statements ({len(statements)} total)\n")
            f.write("=" * 50 + "\n\n")
            
            for i, statement in enumerate(statements, 1):
                f.write(f"Statement {i}:\n")
                f.write(f"Content: {statement.statement}\n")
                f.write(f"Type: {statement.stmt_type.value}\n")
                f.write(f"Temporal Info: {statement.temporal_info.value}\n")
                f.write(f"Relevence Info: {statement.relevence_info.value}\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"Extracted {len(statements)} statements and saved to {output_path}")
        return output_path
