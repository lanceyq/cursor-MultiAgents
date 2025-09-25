import asyncio
from dotenv import load_dotenv
import time
from datetime import datetime

from database.neo4j_connector import Neo4jConnector
from extraction_pipeline import (
    assign_values_to_nodes,
    get_chunked_dialogs,
    embedding_generation,
    statement_extraction,
    temporal_extraction,
    triplet_extraction,
    assign_extracted_data_to_statements_in_place,
    generate_entity_embeddings_from_triplets
)
from database.graph_saver import save_dialog_and_statements_to_neo4j
from utils.helpers import log_time, get_llm_client

load_dotenv()


async def main():
    """Main function to demonstrate the complete pipeline"""
    print("=== MemSci Knowledge Extraction Pipeline ===")
    
    # Initialize timing log
    log_file = "time.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n=== Pipeline Run Started: {timestamp} ===\n")
    
    pipeline_start = time.time()

    # Initialize llm client
    llm_client = get_llm_client("openai/qwen2.5-14b")  #这主流水线上调用的qwen2.5-14b
    
    # Step 1: Load test data and create list of DialogData objects
    step_start = time.time()
    chunked_dialogs = await get_chunked_dialogs(group_id="group_123")
    log_time("Data Loading & Chunking", time.time() - step_start, log_file)
    
    # Step 2: Test statement extraction on all dialogs
    step_start = time.time()
    chunked_dialogs = await statement_extraction(chunked_dialogs, llm_client=llm_client)
    log_time("Statement Extraction", time.time() - step_start, log_file)

    # 3,4,5 Can run concurrently
    # Step 3: Test embedding extraction
    step_start = time.time()
    statement_embedding_maps, chunk_embedding_maps, dialog_embeddings = await embedding_generation(chunked_dialogs)
    log_time("Embedding Generation", time.time() - step_start, log_file)
    
    # Step 4: Run triplet extraction
    step_start = time.time()
    triplet_maps = await triplet_extraction(chunked_dialogs, llm_client=llm_client)
    log_time("Triplet Extraction", time.time() - step_start, log_file)
    
    # Step 5: Run temporal extraction
    step_start = time.time()
    temporal_maps = await temporal_extraction(chunked_dialogs, llm_client=llm_client)
    log_time("Temporal Extraction", time.time() - step_start, log_file)
    
    # Step 6: Generate and assign entity name embeddings based on triplet results
    step_start = time.time()
    triplet_maps = await generate_entity_embeddings_from_triplets(triplet_maps)
    log_time("Entity Embedding Generation", time.time() - step_start, log_file)
    
    # Step 7: Assign extracted data back to statements for all dialogs
    step_start = time.time()
    chunked_dialogs = await assign_extracted_data_to_statements_in_place(
        chunked_dialogs, temporal_maps, triplet_maps,
        statement_embedding_maps, chunk_embedding_maps, dialog_embeddings
    )
    log_time("Data Assignment to Statements", time.time() - step_start, log_file)
    
    # Step 8: Create graph nodes and edges from the processed data
    step_start = time.time()
    all_dialogue_nodes, all_statement_nodes, all_entity_nodes, all_statement_dialog_edges, all_statement_entity_edges, all_entity_entity_edges = await assign_values_to_nodes(chunked_dialogs)
    log_time("Graph Node & Edge Creation", time.time() - step_start, log_file)
    
    # Step 9: Save all data to Neo4j database using graph models
    step_start = time.time()
    neo4j_connector = Neo4jConnector()
    try:
        success = await save_dialog_and_statements_to_neo4j(
            dialogue_nodes=all_dialogue_nodes,
            statement_nodes=all_statement_nodes,
            entity_nodes=all_entity_nodes,
            statement_dialog_edges=all_statement_dialog_edges,
            statement_entity_edges=all_statement_entity_edges,
            entity_edges=all_entity_entity_edges,
            connector=neo4j_connector
        )
        if success:
            print("Successfully saved all data to Neo4j")
        else:
            print("Failed to save some data to Neo4j")
    finally:
        await neo4j_connector.close()
    
    log_time("Neo4j Database Save", time.time() - step_start, log_file)
    
    # Log total pipeline time
    total_time = time.time() - pipeline_start
    log_time("TOTAL PIPELINE TIME", total_time, log_file)
    
    # Add completion marker to log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"=== Pipeline Run Completed: {timestamp} ===\n\n")
    
    print("\n=== Pipeline Complete ===")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Timing details saved to: {log_file}")


if __name__ == "__main__":
    asyncio.run(main())
    
