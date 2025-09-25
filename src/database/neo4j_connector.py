import os
from typing import Any

from neo4j import AsyncGraphDatabase

from utils.helpers import get_neo4j_config


class Neo4jConnector:
    def __init__(self):
        config = get_neo4j_config()
        self.driver = AsyncGraphDatabase.driver(
            config["uri"],
            auth=(config["username"], os.getenv("NEO4J_PASSWORD"))
        )

    async def close(self):
        await self.driver.close()

    async def execute_query(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        result = await self.driver.execute_query(
            query,
            database="neo4j",
            **kwargs
        )
        records, summary, keys = result
        return [record.data() for record in records]
    
    async def delete_group(self, group_id: str):
        await self.driver.execute_query(
            "MATCH (n) WHERE n.group_id = $group_id DETACH DELETE n",
            database="neo4j",
            group_id=group_id
        )
        # DELETE EDGE
        await self.driver.execute_query(
            "MATCH ()-[r]->() WHERE r.group_id = $group_id DELETE r",
            database="neo4j",
            group_id=group_id
        )
        print(f"Group {group_id} deleted.")
