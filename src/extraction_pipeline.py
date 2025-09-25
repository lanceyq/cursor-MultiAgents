import os 
import asyncio
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime

from numpy import extract

from llm_tools.openai_client import OpenAIClient,LLMClient
from llm_tools.openai_embedder import OpenAIEmbedderClient
from utils.helpers import get_model_config, get_embedder_config, get_llm_client
from knowledge_extraction.chunk_extraction import DialogueChunker
from knowledge_extraction.statement_extraction import StatementExtractor
from knowledge_extraction.temporal_extraction import TemporalExtractor
from knowledge_extraction.triplet_extraction import TripletExtractor
from models.config_models import LLMConfig, EmbedderConfig
from models.message_models import DialogData, ConversationContext, ConversationMessage
from models.graph_models import(
    StatementNode, 
    DialogueNode,
    StatementDialogEdge, 
    StatementEntityEdge, 
    EntityEntityEdge, 
    ExtractedEntityNode
)


async def get_chunked_dialog(chunker_strategy: str = "RecursiveChunker") -> DialogData:
    """Generate chunks from test data using the specified chunker strategy.
    
    Args:
        chunker_strategy: The chunking strategy to use (default: RecursiveChunker)
        
    Returns:
        DialogData object with generated chunks
    """
    # Load test data
    testdata_path = os.path.join(os.path.dirname(__file__), "../data", "testdata.json")
    with open(testdata_path, "r", encoding="utf-8") as f:
        test_data = [json.loads(line) for line in f]
    
    # Process test case
    first_test = test_data[2]
    
    # Parse the conversation context
    context_text = first_test['context']
    
    # Split the conversation into messages 
    lines = context_text.split('\n')
    messages = []
    
    # Simple code to parse the conversation
    for line in lines:
        line = line.strip()
        if line.startswith('用户:'):
            messages.append(ConversationMessage(role="用户", msg=line[3:].strip()))
        elif line.startswith('AI:'):
            messages.append(ConversationMessage(role="AI", msg=line[3:].strip()))
    
    # Create DialogData
    conversation_context = ConversationContext(msgs=messages)
    # Create DialogData with group_id
    dialog_data = DialogData(
        context=conversation_context,
        ref_id=first_test['id'],
        group_id="group_1"   
    )
    # Create DialogueChunker and process the dialogue
    chunker = DialogueChunker(chunker_strategy)
    extracted_chunks = chunker.process_dialogue(dialog_data)
    dialog_data.chunks = extracted_chunks
    
    # Save the results to a file
    chunker.save_chunking_results(dialog_data, 
                                 os.path.join(os.path.dirname(__file__), "chunker_test_output.txt"))
    
    return dialog_data

async def get_chunked_dialogs(chunker_strategy: str = "RecursiveChunker", group_id: str = "group_1") -> List[DialogData]:
    """Generate chunks from all test data entries using the specified chunker strategy.
    
    Args:
        chunker_strategy: The chunking strategy to use (default: RecursiveChunker)
        
    Returns:
        List of DialogData objects with generated chunks for each test entry
    """
    # Load test data
    testdata_path = os.path.join(os.path.dirname(__file__), "../data", "testdata.json")
    with open(testdata_path, "r", encoding="utf-8") as f:
        test_data = [json.loads(line) for line in f]
    
    dialog_data_list = []
    
    for data in test_data[:1]:
        # Parse the conversation context
        context_text = data['context']
        
        # Split the conversation into messages
        lines = context_text.split('\n')
        messages = []
        
        # Simple code to parse the conversation
        for line in lines:
            line = line.strip()
            if line.startswith('用户:'):
                messages.append(ConversationMessage(role="用户", msg=line[3:].strip()))
            elif line.startswith('AI:'):
                messages.append(ConversationMessage(role="AI", msg=line[3:].strip()))
        
        # Create DialogData
        conversation_context = ConversationContext(msgs=messages)
        # Create DialogData with group_id based on the entry's id for uniqueness
        dialog_data = DialogData(
            context=conversation_context,
            ref_id=data['id'],
            group_id=group_id 
        )
        # Create DialogueChunker and process the dialogue
        chunker = DialogueChunker(chunker_strategy)
        extracted_chunks = chunker.process_dialogue(dialog_data)
        dialog_data.chunks = extracted_chunks
        
        dialog_data_list.append(dialog_data)
    
    # Convert to dict with datetime serialized
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
    
    combined_output = [dd.model_dump() for dd in dialog_data_list]
    with open(os.path.join(os.path.dirname(__file__), "chunker_test_output.txt"), "w", encoding="utf-8") as f:
        json.dump(combined_output, f, ensure_ascii=False, indent=4, default=serialize_datetime)
    
    return dialog_data_list

async def statement_extraction(chunked_dialogs: List[DialogData], llm_client: LLMClient) -> List[DialogData]:
    """Statement extraction on chunked dialogs."""
    print("\n=== Statement Extraction ===")
    
    # Initialize statement extractor
    statement_extractor = StatementExtractor(llm_client=llm_client)
    
    # Prepare async tasks for extracting statements from each dialog
    async def extract_for_dialog(chunked_dialog: DialogData):
        # Extract statements using the extractor
        results = await statement_extractor.extract_statements(chunked_dialog, limit_chunks=1)
        
        for i, chunk_statements in enumerate(results):
            if chunk_statements:
                chunk = chunked_dialog.chunks[i]
                chunk.statements = chunk_statements
            else:
                print("Error processing statements. ")
        
        # Flatten the results for this dialog
        all_statements = []
        for chunk_statements in results:
            if chunk_statements:
                all_statements.extend(chunk_statements)
        
        return chunked_dialog, all_statements
    
    # Run extractions concurrently for all dialogs
    tasks = [extract_for_dialog(dialog) for dialog in chunked_dialogs]
    extraction_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    updated_dialogs = []
    all_statements_across_dialogs = []
    
    for result in extraction_results:
        if isinstance(result, Exception):
            print(f"Error in concurrent extraction: {result}")
            continue
        updated_dialog, dialog_statements = result
        updated_dialogs.append(updated_dialog)
        all_statements_across_dialogs.extend(dialog_statements)
    
    # Save all statements across all dialogs to file
    statement_extractor.save_statements(all_statements_across_dialogs)
    

    return updated_dialogs

# enforce type for maps
async def assign_extracted_data_to_statements_in_place(
    dialog_data_list: List[DialogData], 
    temporal_maps: List[Dict[str, Any]], 
    triplet_maps: List[Dict[str, Any]],
    statement_embedding_maps: List[Dict[str, List[float]]],
    chunk_embedding_maps: List[Dict[str, List[float]]],
    dialog_embeddings: List[List[float]]
) -> List[DialogData]:
    """In-place operation to assign temporal, triplet, and embedding data back to statements   
    
    Args:
        dialog_data_list: List of DialogData objects
        temporal_maps: List of dictionaries mapping statement IDs to temporal ranges
        triplet_maps: List of dictionaries mapping statement IDs to triplet responses
        statement_embedding_maps: List of dictionaries mapping statement IDs to embeddings (per dialog)
        chunk_embedding_maps: List of dictionaries mapping chunk IDs to embeddings (per dialog)
        dialog_embeddings: List of dialog embeddings (per dialog)
        
    Returns:
        List[DialogData]: The same dialog data list with assigned extraction results
    """
    print("\n=== Assigning Extracted Data to Statements ===")
    
    # Ensure we have matching lists
    expected_length = len(dialog_data_list)
    if (len(temporal_maps) != expected_length or len(triplet_maps) != expected_length or 
        len(statement_embedding_maps) != expected_length or len(chunk_embedding_maps) != expected_length or 
        len(dialog_embeddings) != expected_length):
        print(f"Warning: Mismatch in data sizes - dialogs: {len(dialog_data_list)}, "
              f"temporal maps: {len(temporal_maps)}, triplet maps: {len(triplet_maps)}, "
              f"statement embeddings: {len(statement_embedding_maps)}, "
              f"chunk embeddings: {len(chunk_embedding_maps)}, "
              f"dialog embeddings: {len(dialog_embeddings)}")
    
    total_dialogs = 0
    total_statements = 0
    assigned_temporal = 0
    assigned_triplets = 0
    assigned_statement_embeddings = 0
    assigned_chunk_embeddings = 0
    assigned_dialog_embeddings = 0
    
    # Process each dialog with its corresponding maps
    for i, dialog_data in enumerate(dialog_data_list):
        if (i >= len(temporal_maps) or i >= len(triplet_maps) or 
            i >= len(statement_embedding_maps) or i >= len(chunk_embedding_maps) or 
            i >= len(dialog_embeddings)):
            print(f"Warning: Missing extraction data for dialog {dialog_data.group_id}, skipping assignment")
            continue
            
        temporal_map = temporal_maps[i]
        triplet_map = triplet_maps[i]
        statement_embedding_map = statement_embedding_maps[i]
        chunk_embedding_map = chunk_embedding_maps[i]
        dialog_embedding = dialog_embeddings[i]
        total_dialogs += 1
        
        dialog_statements = 0
        dialog_temporal = 0
        dialog_triplets = 0
        dialog_stmt_embeddings = 0
        dialog_chunk_embeddings = 0
        
        # Assign dialog embedding
        if hasattr(dialog_data, 'dialog_embedding'):
            dialog_data.dialog_embedding = dialog_embedding
            assigned_dialog_embeddings += 1
        
        for chunk in dialog_data.chunks:
            # Assign chunk embedding
            if hasattr(chunk, 'chunk_embedding') and chunk.id in chunk_embedding_map:
                chunk.chunk_embedding = chunk_embedding_map[chunk.id]
                assigned_chunk_embeddings += 1
                dialog_chunk_embeddings += 1
            
            for statement in chunk.statements:
                total_statements += 1
                dialog_statements += 1
                
                # Assign temporal data
                if statement.id in temporal_map:
                    statement.temporal_validity = temporal_map[statement.id]
                    assigned_temporal += 1
                    dialog_temporal += 1
                
                # Assign triplet data
                if statement.id in triplet_map:
                    statement.triplet_extraction_info = triplet_map[statement.id]
                    assigned_triplets += 1
                    dialog_triplets += 1
                
                # Assign statement embedding
                if hasattr(statement, 'statement_embedding') and statement.id in statement_embedding_map:
                    statement.statement_embedding = statement_embedding_map[statement.id]
                    assigned_statement_embeddings += 1
                    dialog_stmt_embeddings += 1
        
        print(f"Dialog {dialog_data.group_id}: Processed {dialog_statements} statements:")
        print(f"  - Assigned temporal data to {dialog_temporal} statements")
        print(f"  - Assigned triplet data to {dialog_triplets} statements")
        print(f"  - Assigned embeddings to {dialog_stmt_embeddings} statements")
        print(f"  - Assigned embeddings to {dialog_chunk_embeddings} chunks")
        print(f"  - Assigned embedding to dialog: {'Yes' if assigned_dialog_embeddings > 0 else 'No'}")
    
    print(f"Total: Processed {total_statements} statements across {total_dialogs} dialogs:")
    print(f"  - Assigned temporal data to {assigned_temporal} statements")
    print(f"  - Assigned triplet data to {assigned_triplets} statements")
    print(f"  - Assigned embeddings to {assigned_statement_embeddings} statements")
    print(f"  - Assigned embeddings to {assigned_chunk_embeddings} chunks")
    print(f"  - Assigned embeddings to {assigned_dialog_embeddings} dialogs")
    
    return dialog_data_list   

async def embedding_generation(chunked_dialogs: List[DialogData]) -> Tuple[
    List[Dict[str, List[float]]],  
    List[Dict[str, List[float]]],  
    List[List[float]] 
]:
    """Generate embeddings for statements, chunks, and dialogs with concurrency."""
    print("\n=== Generating Embeddings with LLM ===")
    #TODO: add concurrency
    embedding_name = "openai/nomic-embed-text:v1.5"  
    embedder_config = get_embedder_config(embedding_name)
    embedder_client = OpenAIEmbedderClient(
        model_config=EmbedderConfig.model_validate(embedder_config),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Helper to generate embeddings for a batch of texts concurrently
    async def generate_embeddings(texts: List[str]) -> List[List[float]]:
        return await embedder_client.response(texts)
    
    # Step 1: Collect all statements across dialogs for batch embedding
    all_statements = []
    statement_to_dialog_chunk_map = []   
    for d_idx, dialog in enumerate(chunked_dialogs):
        for c_idx, chunk in enumerate(dialog.chunks):
            for s_idx, stmt in enumerate(chunk.statements):
                all_statements.append(stmt.statement) 
                statement_to_dialog_chunk_map.append((d_idx, c_idx, s_idx))
    
    stmt_embeddings = await generate_embeddings(all_statements)
    
    # Step 2: Collect all chunks for batch embedding 
    all_chunks = []
    chunk_to_dialog_map = []  
    for d_idx, dialog in enumerate(chunked_dialogs):
        for c_idx, chunk in enumerate(dialog.chunks):
            all_chunks.append(chunk.content)  
            chunk_to_dialog_map.append((d_idx, c_idx))
    
    chunk_embeddings = await generate_embeddings(all_chunks)
    
    # Step 3: Collect all dialogs for batch embedding
    all_dialogs = []
    for dialog in chunked_dialogs:
        all_dialogs.append(dialog.content) 
    
    dialog_embeddings = await generate_embeddings(all_dialogs)
    
    # Create maps for assignment (similar to triplet/temporal maps)
    stmt_embedding_maps = [{} for _ in chunked_dialogs]
    chunk_embedding_maps = [{} for _ in chunked_dialogs]
    
    for idx, embedding in enumerate(stmt_embeddings):
        d_idx, c_idx, s_idx = statement_to_dialog_chunk_map[idx]
        stmt_id = chunked_dialogs[d_idx].chunks[c_idx].statements[s_idx].id
        stmt_embedding_maps[d_idx][stmt_id] = embedding
    
    for idx, embedding in enumerate(chunk_embeddings):
        d_idx, c_idx = chunk_to_dialog_map[idx]
        chunk_id = chunked_dialogs[d_idx].chunks[c_idx].id 
        chunk_embedding_maps[d_idx][chunk_id] = embedding
    
    # Print summary
    print(f"Generated embeddings for {len(all_statements)} statements, {len(all_chunks)} chunks, and {len(chunked_dialogs)} dialogs.")
    
    return stmt_embedding_maps, chunk_embedding_maps, dialog_embeddings

async def triplet_extraction(chunked_dialogs: List[DialogData], llm_client: LLMClient) -> List[Dict[str, Any]]:
    """Triplet extraction with LLM
    
    Note: Modified to handle multiple dialogs in batch.
    """
    print("\n=== Triplet Extraction ===")
        
    # Initialize triplet extractor
    triplet_extractor = TripletExtractor(llm_client=llm_client)
    
    # Prepare async tasks for extracting triplets from each dialog
    async def extract_for_dialog(chunked_dialog: DialogData):
        # This already returns a dictionary mapping statement IDs to TripletExtractionResponse
        triplet_map = await triplet_extractor.extract_triplets_from_statements(chunked_dialog)
        
        # Flatten responses for this dialog for saving
        triplet_responses = list(triplet_map.values())
        
        # Print summary for this dialog
        total_triplets = sum(len(response.triplets) for response in triplet_responses)
        total_entities = sum(len(response.entities) for response in triplet_responses)
        print(f"Extracted {total_triplets} triplets and {total_entities} entities from {len(chunked_dialog.chunks[0].statements if chunked_dialog.chunks else 0)} statements in dialog {chunked_dialog.group_id}")
        
        return triplet_map, triplet_responses
    
    # Run extractions concurrently for all dialogs
    tasks = [extract_for_dialog(dialog) for dialog in chunked_dialogs]
    extraction_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    triplet_maps = []
    all_triplet_responses = []
    
    for result in extraction_results:
        if isinstance(result, Exception):
            print(f"Error in concurrent triplet extraction: {result}")
            continue
        triplet_map, triplet_responses = result
        triplet_maps.append(triplet_map)
        all_triplet_responses.extend(triplet_responses)
    
    # Save all extracted triplets across all dialogs
    if all_triplet_responses:
        output_path = triplet_extractor.save_triplets(all_triplet_responses)
        print(f"Saved triplets to: {output_path}")
    
    return triplet_maps



async def temporal_extraction(chunked_dialogs: List[DialogData], llm_client: LLMClient) -> List[Dict[str, Any]]:
    """Temporal extraction with LLM
    
    Note: Modified to handle multiple dialogs in batch.
    """
    print("\n=== Temporal Extraction ===")
      
    # Initialize temporal extractor
    temporal_extractor = TemporalExtractor(llm_client=llm_client)
    
    # Prepare async tasks for extracting temporal ranges from each dialog
    async def extract_for_dialog(chunked_dialog: DialogData):
        # This already returns a dictionary mapping statement IDs to TemporalValidityRange
        temporal_map = await temporal_extractor.extract_temporal_ranges(chunked_dialog)
        
        # Print summary for this dialog
        print(f"Extracted temporal ranges for {len(temporal_map)} statements in dialog {chunked_dialog.group_id}")
        
        return temporal_map, chunked_dialog
    
    # Run extractions concurrently for all dialogs
    tasks = [extract_for_dialog(dialog) for dialog in chunked_dialogs]
    extraction_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    temporal_maps = []
    updated_dialogs = []
    
    for result in extraction_results:
        if isinstance(result, Exception):
            print(f"Error in concurrent temporal extraction: {result}")
            continue
        temporal_map, dialog = result
        temporal_maps.append(temporal_map)
        
        # Assign temporal data back to statements in the dialog for saving
        for chunk in dialog.chunks:
            for statement in chunk.statements:
                if statement.id in temporal_map:
                    statement.temporal_validity = temporal_map[statement.id]
        
        updated_dialogs.append(dialog)
    
    # Save temporal extraction results to file
    if updated_dialogs:
        output_path = os.path.join(os.path.dirname(__file__), "extracted_temporal_data.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Temporal Extraction Results ({len(updated_dialogs)} dialogs)\n")
            f.write("=" * 60 + "\n\n")
            
            for dialog_idx, dialog in enumerate(updated_dialogs, 1):
                f.write(f"Dialog {dialog_idx} (Group ID: {dialog.group_id}):\n")
                f.write("-" * 40 + "\n")
                
                for chunk_idx, chunk in enumerate(dialog.chunks, 1):
                    f.write(f"Chunk {chunk_idx}: {chunk.content[:100]}...\n")
                    
                    for stmt_idx, statement in enumerate(chunk.statements, 1):
                        f.write(f"  Statement {stmt_idx}: {statement.statement}\n")
                        if statement.temporal_validity:
                            f.write(f"    - Valid At: {statement.temporal_validity.valid_at}\n")
                            f.write(f"    - Invalid At: {statement.temporal_validity.invalid_at}\n")
                        else:
                            f.write(f"    - Temporal Validity: Not Extracted\n")
                        f.write("\n")
                    f.write("\n")
                f.write("\n")
        
        print(f"Saved temporal extraction results to: {output_path}")
    
    return temporal_maps


async def assign_values_to_nodes(
    dialog_data_list: List[DialogData]
) -> Tuple[
    DialogueNode,
    List[StatementNode],
    List[ExtractedEntityNode],
    List[StatementDialogEdge],
    List[StatementEntityEdge],
    List[EntityEntityEdge],
]:
    """Assign values to dialog, statement, and entity nodes from extracted data.
    
    Args:
        dialog_data_list: List of DialogData objects with all extracted information already assigned
        
    Returns:
        Tuple containing lists of DialogueNode, StatementNode, ExtractedEntityNode objects
        and their corresponding edge objects
    """
    print("\n=== Assigning Values to Graph Nodes and Edges ===")
    
    dialogue_nodes = []
    statement_nodes = []
    entity_nodes = []
    statement_dialog_edges = []
    statement_entity_edges = []
    entity_entity_edges = []
    
    for dialog_data in dialog_data_list:
        # Create DialogueNode
        dialogue_node = DialogueNode(
            id=dialog_data.id,
            name=f"Dialog_{dialog_data.id}",
            group_id=dialog_data.group_id,
            t_created=dialog_data.created_at,
            t_expired=datetime(9999, 12, 31),
            ref_id=dialog_data.ref_id,
            content=dialog_data.content if dialog_data.content else "",
            dialog_embedding=getattr(dialog_data, 'dialog_embedding', None)
        )
        dialogue_nodes.append(dialogue_node)
        
        # Process chunks and statements
        for chunk_idx, chunk in enumerate(dialog_data.chunks):
            for stmt_idx, statement in enumerate(chunk.statements):
                temporal_valid_at = None
                temporal_invalid_at = None
                
                if hasattr(statement, 'temporal_validity') and statement.temporal_validity:
                    if hasattr(statement.temporal_validity, 'valid_at'):
                        temporal_valid_at = statement.temporal_validity.valid_at
                    if hasattr(statement.temporal_validity, 'invalid_at'):
                        temporal_invalid_at = statement.temporal_validity.invalid_at
                
                # Create StatementNode
                statement_node = StatementNode(
                    id=statement.id,
                    name=f"Statement_{statement.id}",
                    group_id=dialog_data.group_id,
                    t_created=dialog_data.created_at,
                    t_expired=datetime(9999, 12, 31),
                    chunk_id=chunk.id,
                    stmt_type=statement.stmt_type,
                    temporal_info=statement.temporal_info,
                    relevence_info=statement.relevence_info,
                    statement=statement.statement,
                    temporal_validity_valid_at=temporal_valid_at,
                    temporal_validity_invalid_at=temporal_invalid_at,
                    statement_embedding=getattr(statement, 'statement_embedding', None),
                    chunk_embedding=getattr(chunk, 'chunk_embedding', None)
                )
                statement_nodes.append(statement_node)
                
                # Create StatementDialogEdge 
                statement_dialog_edge = StatementDialogEdge(
                    source=dialogue_node.id,  
                    target=statement.id,
                    group_id=dialog_data.group_id,
                    t_created=dialog_data.created_at,
                    t_expired=datetime(9999, 12, 31),
                    chunk_id=chunk.id
                )
                statement_dialog_edges.append(statement_dialog_edge)
                
                # Extract entities from already-assigned triplet information
                if hasattr(statement, 'triplet_extraction_info') and statement.triplet_extraction_info:
                    triplet_info = statement.triplet_extraction_info
                    if hasattr(triplet_info, 'entities'):
                        entity_by_idx = {}   
                        
                        for entity in triplet_info.entities:
                            entity_node = ExtractedEntityNode(
                                id=entity.id,
                                name=entity.name,
                                group_id=dialog_data.group_id,
                                t_created=dialog_data.created_at,
                                t_expired=datetime(9999, 12, 31),
                                entity_idx=str(entity.entity_idx),
                                statement_id=statement.id,
                                entity_type=entity.type,
                                description=entity.description,
                                aliases=entity.aliases if hasattr(entity, 'aliases') else [],
                                name_embedding=getattr(entity, 'name_embedding', []),
                                fact_summary=getattr(entity, 'fact_summary', f"Entity {entity.name} from statement {statement.id}")
                            )
                            entity_nodes.append(entity_node)
                            entity_by_idx[entity.entity_idx] = entity_node
                            
                            # Create StatementEntityEdge  
                            statement_entity_edge = StatementEntityEdge(
                                source=statement.id,
                                target=entity_node.id,
                                group_id=dialog_data.group_id,
                                t_created=dialog_data.created_at,
                                t_expired=datetime(9999, 12, 31)
                            )
                            statement_entity_edges.append(statement_entity_edge)
                        
                        # Create EntityEntityEdges from triplets
                        if hasattr(triplet_info, 'triplets'):
                            for triplet in triplet_info.triplets:
                                subject_idx = triplet.subject_id   
                                object_idx = triplet.object_id     
                                
                                subject_entity = entity_by_idx.get(subject_idx)
                                object_entity = entity_by_idx.get(object_idx)
                                
                                if subject_entity and object_entity and subject_entity.id != object_entity.id:
                                    entity_entity_edge = EntityEntityEdge(
                                        source=subject_entity.id,
                                        target=object_entity.id,
                                        group_id=dialog_data.group_id,
                                        t_created=dialog_data.created_at,
                                        t_expired=datetime(9999, 12, 31),
                                        relation_type=getattr(triplet, 'predicate', 'RELATED_TO'),
                                        relation_value=triplet.value,
                                        statement=statement.statement,
                                        source_statement_id=statement.id,
                                        temporal_validity_valid_at=temporal_valid_at,
                                        temporal_validity_invalid_at=temporal_invalid_at
                                    )
                                    entity_entity_edges.append(entity_entity_edge)
    
    print(f"Created {len(dialogue_nodes)} dialogue nodes")
    print(f"Created {len(statement_nodes)} statement nodes")
    print(f"Created {len(entity_nodes)} entity nodes")
    print(f"Created {len(statement_dialog_edges)} statement-dialog edges")
    print(f"Created {len(statement_entity_edges)} statement-entity edges")
    print(f"Created {len(entity_entity_edges)} entity-entity edges")
    
    return (dialogue_nodes, statement_nodes, entity_nodes, 
            statement_dialog_edges, statement_entity_edges, entity_entity_edges)


 
async def generate_entity_embeddings_from_triplets(
    triplet_maps: List[Dict[str, Any]],
    embedding_name: str = "openai/nomic-embed-text:v1.5"
) -> List[Dict[str, Any]]:
    
    print("\n=== Generating Entity Embeddings from Triplets ===")
    embedder_config = get_embedder_config(embedding_name)
    embedder_client = OpenAIEmbedderClient(
        model_config=EmbedderConfig.model_validate(embedder_config),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    entity_texts: List[str] = []
    entity_refs: List[Any] = []
    for trip_map in triplet_maps:
        for _, triplet_info in trip_map.items():
            entities = getattr(triplet_info, "entities", None)
            if not entities:
                continue
            for ent in entities:
                text = getattr(ent, "name", None) or getattr(ent, "description", None)
                if text:
                    entity_texts.append(text)
                    entity_refs.append(ent)
    if not entity_texts:
        print("No entities found to embed.")
        return triplet_maps
    embeddings = await embedder_client.response(entity_texts)
    for ent, emb in zip(entity_refs, embeddings):
        setattr(ent, "name_embedding", emb)
    print(f"Assigned embeddings to {len(entity_refs)} entities.")
    return triplet_maps
    