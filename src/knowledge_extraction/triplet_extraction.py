import os
import asyncio
from typing import List, Dict

from llm_tools.openai_client import OpenAIClient
from utils.helpers import render_triplet_extraction_prompt
from ontology.ontology import PREDICATE_DEFINITIONS 
from models.triplet_models import TripletExtractionResponse
from models.message_models import DialogData, Statement



class TripletExtractor:
    """Extracts knowledge triplets and entities from statements using LLM"""
    
    def __init__(self, llm_client: OpenAIClient):
        """Initialize the TripletExtractor with an LLM client
        
        Args:
            llm_client: OpenAIClient instance for processing
        """
        self.llm_client = llm_client

    async def _extract_triplets(self, statement: Statement, chunk_content: str) -> TripletExtractionResponse:
        """Process a single statement and return extracted triplets and entities"""
        # Render the prompt using helper function
        prompt_content = render_triplet_extraction_prompt(
            statement=statement.statement,
            chunk_content=chunk_content,
            json_schema=TripletExtractionResponse.model_json_schema(),
            predicate_instructions=PREDICATE_DEFINITIONS
        )
        
        # Create messages for LLM
        messages = [
            {"role": "system", "content": "You are an expert at extracting knowledge triplets and entities from text. Follow the provided instructions carefully and return valid JSON."},
            {"role": "user", "content": prompt_content}
        ]
        
        try:
            # Get structured response from LLM
            response = await self.llm_client.response_structured(messages, TripletExtractionResponse)
            # Create new triplets with statement_id set during creation
            updated_triplets = []
            for triplet in response.triplets:
                updated_triplet = triplet.model_copy(update={"statement_id": statement.id})
                updated_triplets.append(updated_triplet)

            # Return new response with updated triplets
            return TripletExtractionResponse(
                triplets=updated_triplets,
                entities=response.entities
            )
            # # Set statement_id for each triplet to establish parent relationship
            # for triplet in response.triplets:
            #     triplet.statement_id = statement.id
                
            # return response
                
        except Exception as e:
            print(f"Error processing statement: {e}")
            return TripletExtractionResponse(triplets=[], entities=[])
    
    async def extract_triplets_from_statements(self, dialog_data: DialogData, limit_chunks: int = 1) -> Dict[str, TripletExtractionResponse]:
        """Extract triplets and entities from statements
        
        Args:
            dialog_data: DialogData object to process
            limit_chunks: Number of chunks to process
            
        Returns:
            Dict[str, TripletExtractionResponse]: Dictionary mapping statement IDs to their triplet responses
        """
        # Collect all statements from the specified chunks
        all_statements = []
        chunks_to_process = dialog_data.chunks[:limit_chunks]
        
        for chunk in chunks_to_process:
            all_statements.extend(chunk.statements)
        
        print(f"Processing {len(all_statements)} statements for triplet extraction...")
        
        # Prepare tasks and statement IDs
        tasks = []
        statement_ids = []
        
        for chunk in chunks_to_process:
            for statement in chunk.statements:
                tasks.append(self._extract_triplets(statement, chunk.content))
                statement_ids.append(statement.id)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to statement IDs
        statement_triplet_map = {}
        for i, result in enumerate(results):
            statement_id = statement_ids[i]
            if isinstance(result, TripletExtractionResponse):
                statement_triplet_map[statement_id] = result
            else:
                print(f"Error in triplet extraction for statement {statement_id}: {result}")
                statement_triplet_map[statement_id] = TripletExtractionResponse(triplets=[], entities=[])
        
        return statement_triplet_map
    
    def save_triplets(self, triplet_responses: List[TripletExtractionResponse], output_path: str = None) -> str:
        """Save extracted triplets and entities to a file
        
        Args:
            triplet_responses: List of TripletExtractionResponse objects
            output_path: Optional path to save the results
            
        Returns:
            Path where the triplets were saved
        """
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), "..", "extracted_triplets.txt")
        
        # Flatten all triplets and entities
        all_triplets = []
        all_entities = []
        
        for response in triplet_responses:
            all_triplets.extend(response.triplets)
            all_entities.extend(response.entities)
        
        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"=== EXTRACTED TRIPLETS ({len(all_triplets)} total) ===\n\n")
            for i, triplet in enumerate(all_triplets, 1):
                f.write(f"Triplet {i}:\n")
                f.write(f"  Subject: {triplet.subject_name} (ID: {triplet.subject_id})\n")
                f.write(f"  Predicate: {triplet.predicate}\n")
                f.write(f"  Object: {triplet.object_name} (ID: {triplet.object_id})\n")
                if triplet.value:
                    f.write(f"  Value: {triplet.value}\n")
                f.write("\n")
            
            f.write(f"\n=== EXTRACTED ENTITIES ({len(all_entities)} total) ===\n\n")
            for i, entity in enumerate(all_entities, 1):
                f.write(f"Entity {i}:\n")
                f.write(f"  ID: {entity.entity_idx}\n")
                f.write(f"  Name: {entity.name}\n")
                f.write(f"  Type: {entity.type}\n")
                f.write(f"  Description: {entity.description}\n")
                f.write("\n")
        
        print(f"Saved {len(all_triplets)} triplets and {len(all_entities)} entities to: {output_path}")
        return output_path

