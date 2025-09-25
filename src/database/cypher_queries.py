


# EPISODIC_NODE_SAVE = """
#     MERGE (n:Episodic {uuid: $uuid})
#     SET n = {uuid: $uuid, name: $name, group_id: $group_id, source_description: $source_description, source: $source, content: $content,
#     entity_edges: $entity_edges, created_at: $created_at, valid_at: $valid_at}
#     RETURN n.uuid AS uuid
# """

# EPISODIC_NODE_SAVE_BULK = """
#     UNWIND $episodes AS episode
#     MERGE (n:Episodic {uuid: episode.uuid})
#     SET n = {uuid: episode.uuid, name: episode.name, group_id: episode.group_id, source_description: episode.source_description,
#         source: episode.source, content: episode.content,
#     entity_edges: episode.entity_edges, created_at: episode.created_at, valid_at: episode.valid_at}
#     RETURN n.uuid AS uuid
# """

# EPISODIC_NODE_RETURN = """
#     e.content AS content,
#     e.created_at AS created_at,
#     e.valid_at AS valid_at,
#     e.uuid AS uuid,
#     e.name AS name,
#     e.group_id AS group_id,
#     e.source_description AS source_description,
#     e.source AS source,
#     e.entity_edges AS entity_edges
# """

# ENTITY_NODE_SAVE =  """
#         UNWIND $nodes AS node
#         MERGE (n:Entity {uuid: node.uuid})
#         SET n:$(node.labels)
#         SET n = node
#         WITH n, node CALL db.create.setNodeVectorProperty(n, "name_embedding", node.name_embedding)
#         RETURN n.uuid AS uuid
#     """

DIALOGUE_NODE_SAVE = """
    UNWIND $dialogues AS dialogue
    CREATE (n:Dialogue {uuid: dialogue.id, 
        group_id: dialogue.group_id, 
        ref_id: dialogue.ref_id, 
        created_at: dialogue.created_at, 
        content: dialogue.content,
        dialog_embedding: dialogue.dialog_embedding})
    RETURN n.uuid AS uuid
"""
# id: str = Field(default_factory=lambda: uuid4().hex, description="A unique identifier for the statement.")
#     chunk_id: str = Field(..., description="ID of the parent chunk this statement belongs to.")
#     statement: str = Field(..., description="The text content of the statement.")
#     stmt_type: StatementType = Field(..., description="The type of the statement.")
#     temporal_info: TemporalInfo = Field(..., description="The temporal information of the statement.")
#     relevence_info: RelevenceInfo = Field(..., description="The relevence information of the statement.")   
#     temporal_validity


STATEMENT_NODE_SAVE = """
UNWIND $statements AS statement
CREATE (s:Statement {
    id: statement.id,
    group_id: statement.group_id,
    chunk_id: statement.chunk_id,
    created_at: statement.created_at,
    stmt_type: statement.stmt_type,
    temporal_info: statement.temporal_info,
    relevence_info: statement.relevence_info,
    statement: statement.statement,
    temporal_validity_valid_at: statement.temporal_validity_valid_at,
    temporal_validity_invalid_at: statement.temporal_validity_invalid_at,
    statement_embedding: statement.statement_embedding,
    chunk_embedding: statement.chunk_embedding
})
RETURN s.id AS uuid
"""


EXTRACTED_ENTITY_NODE_SAVE = """
UNWIND $entities AS entity
CREATE (e:ExtractedEntity {
    id: entity.id,
    name: entity.name,
    group_id: entity.group_id,
    t_created: entity.t_created,
    t_expired: entity.t_expired,
    entity_idx: entity.entity_idx,
    entity_type: entity.entity_type,
    description: entity.description,
    statement_id: entity.statement_id,
    name_embedding: entity.name_embedding
})
RETURN e.id AS uuid
"""

# Add back ENTITY_RELATIONSHIP_SAVE to be used by graph_saver.save_entities_and_relationships
ENTITY_RELATIONSHIP_SAVE = """
UNWIND $relationships AS rel
MATCH (subject:ExtractedEntity {id: rel.source_id})
MATCH (object:ExtractedEntity {id: rel.target_id})
CREATE (subject)-[r:EXTRACTED_RELATIONSHIP {
    predicate: rel.predicate,
    statement_id: rel.statement_id,
    value: rel.value,
    created_at: rel.created_at,
    statement: rel.statement,
    statement_id: rel.statement_id,
    temporal_validity_valid_at: rel.temporal_validity_valid_at,
    temporal_validity_invalid_at: rel.temporal_validity_invalid_at
}]->(object)
RETURN id(r) AS uuid
"""

DIALOGUE_STATEMENT_EDGE_SAVE = """
    UNWIND $dialogue_statement_edges AS edge
    MATCH (dialogue:Dialogue {uuid: edge.source})
    MATCH (statement:Statement {id: edge.target})
    MERGE (dialogue)-[e:MENTIONS {uuid: edge.id}]->(statement)
    SET e = {
        uuid: edge.id,
        group_id: edge.group_id,
        t_created: edge.t_created,
        t_expired: edge.t_expired
    }
    RETURN e.uuid AS uuid
"""

# EPISODIC_EDGE_SAVE_BULK = """
#     UNWIND $episodic_edges AS edge
#     MATCH (episode:Episodic {uuid: edge.source_node_uuid})
#     MATCH (node:Entity {uuid: edge.target_node_uuid})
#     MERGE (episode)-[e:MENTIONS {uuid: edge.uuid}]->(node)
#     SET e = {uuid: edge.uuid, group_id: edge.group_id, created_at: edge.created_at}
#     RETURN e.uuid AS uuid
# """

# ENTITY_EDGE_SAVE = """
#         UNWIND $entity_edges AS edge
#         MATCH (source:Entity {uuid: edge.source_node_uuid})
#         MATCH (target:Entity {uuid: edge.target_node_uuid})
#         MERGE (source)-[e:RELATES_TO {uuid: edge.uuid}]->(target)
#         SET e = edge
#         WITH e, edge CALL db.create.setRelationshipVectorProperty(e, "fact_embedding", edge.fact_embedding)
#         RETURN edge.uuid AS uuid
#     """

STATEMENT_ENTITY_EDGE_SAVE = """
UNWIND $relationships AS rel
MATCH (statement:Statement {id: rel.source})
MATCH (entity:ExtractedEntity {id: rel.target})
CREATE (statement)-[r:REFERENCES_ENTITY {
    group_id: rel.group_id,
    t_created: rel.t_created,
    t_expired: rel.t_expired
}]->(entity)
RETURN id(r) AS uuid
"""

# Entity keyword search (fallback as entities don't store embeddings)
SEARCH_ENTITIES_BY_NAME = """
MATCH (e:ExtractedEntity)
WHERE toLower(e.name) CONTAINS toLower($q)
  AND ($group_id IS NULL OR e.group_id = $group_id)
RETURN e.id AS id,
       e.name AS name,
       e.group_id AS group_id,
       e.entity_type AS entity_type
LIMIT $limit
"""

# Embedding-based search: cosine similarity on Statement.statement_embedding
STATEMENT_EMBEDDING_SEARCH = """
WITH $embedding AS q
MATCH (s:Statement)
WHERE s.statement_embedding IS NOT NULL
  AND ($group_id IS NULL OR s.group_id = $group_id)
WITH s, q, s.statement_embedding AS v
WITH s,
     reduce(dot = 0.0, i IN range(0, size(q)-1) | dot + toFloat(q[i]) * toFloat(v[i])) AS dot,
     sqrt(reduce(qs = 0.0, i IN range(0, size(q)-1) | qs + toFloat(q[i]) * toFloat(q[i]))) AS qnorm,
     sqrt(reduce(vs = 0.0, i IN range(0, size(v)-1) | vs + toFloat(v[i]) * toFloat(v[i]))) AS vnorm
WITH s, CASE WHEN qnorm = 0 OR vnorm = 0 THEN 0.0 ELSE dot / (qnorm * vnorm) END AS score
RETURN s.id AS id,
       s.statement AS statement,
       s.group_id AS group_id,
       s.chunk_id AS chunk_id,
       s.created_at AS created_at,
       score
ORDER BY score DESC
LIMIT $limit
"""

# Embedding-based search: cosine similarity on Dialogue.dialog_embedding
DIALOGUE_EMBEDDING_SEARCH = """
WITH $embedding AS q
MATCH (d:Dialogue)
WHERE d.dialog_embedding IS NOT NULL
  AND ($group_id IS NULL OR d.group_id = $group_id)
WITH d, q, d.dialog_embedding AS v
WITH d,
     reduce(dot = 0.0, i IN range(0, size(q)-1) | dot + toFloat(q[i]) * toFloat(v[i])) AS dot,
     sqrt(reduce(qs = 0.0, i IN range(0, size(q)-1) | qs + toFloat(q[i]) * toFloat(q[i]))) AS qnorm,
     sqrt(reduce(vs = 0.0, i IN range(0, size(v)-1) | vs + toFloat(v[i]) * toFloat(v[i]))) AS vnorm
WITH d, CASE WHEN qnorm = 0 OR vnorm = 0 THEN 0.0 ELSE dot / (qnorm * vnorm) END AS score
RETURN d.uuid AS uuid,
       d.group_id AS group_id,
       d.content AS content,
       score
ORDER BY score DESC
LIMIT $limit
"""

SEARCH_STATEMENTS_BY_KEYWORD = """
MATCH (s:Statement)
WHERE toLower(s.statement) CONTAINS toLower($q)
  AND ($group_id IS NULL OR s.group_id = $group_id)
OPTIONAL MATCH (d:Dialogue)-[:MENTIONS]->(s)
OPTIONAL MATCH (s)-[:REFERENCES_ENTITY]->(e:ExtractedEntity)
RETURN s.id AS id,
       s.statement AS statement,
       s.group_id AS group_id,
       s.chunk_id AS chunk_id,
       s.created_at AS created_at,
       d.uuid AS dialogue_id,
       collect(DISTINCT e.id) AS entity_ids
ORDER BY created_at DESC
LIMIT $limit
"""

SEARCH_ENTITIES_BY_NAME = """
MATCH (e:ExtractedEntity)
WHERE toLower(e.name) CONTAINS toLower($q)
  AND ($group_id IS NULL OR e.group_id = $group_id)
OPTIONAL MATCH (s:Statement)-[:REFERENCES_ENTITY]->(e)
OPTIONAL MATCH (d:Dialogue)-[:MENTIONS]->(s)
RETURN e.id AS id,
       e.name AS name,
       e.group_id AS group_id,
       e.entity_type AS entity_type,
       collect(DISTINCT s.id) AS statement_ids,
       collect(DISTINCT d.uuid) AS dialogue_ids
LIMIT $limit
"""

SEARCH_DIALOGUES_BY_CONTENT = """
MATCH (d:Dialogue)
WHERE d.content IS NOT NULL
  AND toLower(d.content) CONTAINS toLower($q)
  AND ($group_id IS NULL OR d.group_id = $group_id)
OPTIONAL MATCH (d)-[:MENTIONS]->(s:Statement)
OPTIONAL MATCH (s)-[:REFERENCES_ENTITY]->(e:ExtractedEntity)
RETURN d.uuid AS uuid,
       d.group_id AS group_id,
       d.content AS content,
       collect(DISTINCT s.id) AS statement_ids,
       collect(DISTINCT e.id) AS entity_ids
LIMIT $limit
"""