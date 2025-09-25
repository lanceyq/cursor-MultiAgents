import asyncio
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

from llm_tools.openai_client import OpenAIClient
from models.message_models import DialogData, Statement, TemporalValidityRange
from utils.helpers import render_temporal_extraction_prompt
from ontology.ontology import LABEL_DEFINITIONS, TemporalInfo


class RawTemporalRange(BaseModel):
    """Schema for the raw temporal range extracted by the LLM."""

    valid_at: Optional[str] = Field(
        None, description="The start date and time of the validity range in ISO 8601 format."
    )
    invalid_at: Optional[str] = Field(
        None, description="The end date  and time of the validity range in ISO 8601 format."
    )


class TemporalExtractor:
    """
    Extracts temporal validity ranges from statements using an LLM.
    """

    def __init__(self, llm_client: OpenAIClient):
        """
        Initializes the TemporalExtractor.

        Args:
            llm_client (OpenAIClient): The OpenAI client to use for LLM calls.
        """
        self.llm_client = llm_client

    async def _extract_temporal_ranges(
        self, statement: Statement, ref_dates: dict[str, Any]
    ) -> TemporalValidityRange:
        """
        Extracts the temporal range for a single statement.

        Args:
            statement (Statement): The statement to process.
            ref_dates (dict[str, Any]): Reference dates for context.

        Returns:
            TemporalValidityRange: The extracted temporal validity range.
        """
        if not ref_dates:
            ref_dates = {"today": datetime.now().strftime("%Y-%m-%d")}

        if statement.temporal_info == TemporalInfo.ATEMPORAL:
            return TemporalValidityRange(valid_at=None, invalid_at=None)

        temporal_guide = LABEL_DEFINITIONS["temporal_labelling"]
        statement_guide = LABEL_DEFINITIONS["episode_labelling"]

        prompt_content = render_temporal_extraction_prompt(
            ref_dates=ref_dates,
            statement=statement.model_dump(),
            temporal_guide=temporal_guide,
            statement_guide=statement_guide,
            json_schema=RawTemporalRange.model_json_schema(),
        )

        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting temporal validity ranges from statements. Follow the provided instructions carefully and return valid JSON.",
            },
            {"role": "user", "content": prompt_content},
        ]

        try:
            response = await self.llm_client.response_structured(
                messages, RawTemporalRange
            )
            if response:
                return TemporalValidityRange(
                    valid_at=response.valid_at, invalid_at=response.invalid_at
                )
        except Exception as e:
            print(f"Error processing statement for temporal extraction: {e}")

        return TemporalValidityRange(valid_at=None, invalid_at=None)

    from typing import Dict, Tuple
    
    async def extract_temporal_ranges(
        self, dialog_data: DialogData, ref_dates: Optional[dict[str, Any]] = None
    ) -> Dict[str, TemporalValidityRange]:
        """
        Extracts temporal ranges for statements in the dialog_data.
    
        Args:
            dialog_data (DialogData): The dialog data containing chunks with statements to process.
            ref_dates (Optional[dict[str, Any]]): Reference dates for context.
        
        Returns:
            Dict[str, TemporalValidityRange]: A dictionary mapping statement IDs to their temporal ranges.
        """
        if ref_dates is None:
            ref_dates = {}
        
        statement_temporal_map = {}
        
        # Collect all statements with their IDs
        all_tasks = []
        statement_ids = []
        
        for chunk in dialog_data.chunks:
            if not chunk.statements:
                continue
                
            for statement in chunk.statements:
                all_tasks.append(self._extract_temporal_ranges(statement, ref_dates))
                statement_ids.append(statement.id)
        
        # Process all statements concurrently
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Map results back to statement IDs
        for i, result in enumerate(results):
            statement_id = statement_ids[i]
            if isinstance(result, TemporalValidityRange):
                statement_temporal_map[statement_id] = result
            else:
                print(f"Failed to process statement {statement_id}. Error: {result}")
                statement_temporal_map[statement_id] = TemporalValidityRange(
                    valid_at=None, invalid_at=None
                )
        
        return statement_temporal_map

    def save_temporal_extractions_to_file(
        self, dialog_data: DialogData, output_path: str = "extracted_temporal_data.txt"
    ):
        """
        Saves the extracted temporal data to a text file.

        Args:
            dialog_data (DialogData): The dialog data containing the statements with temporal data.
            output_path (str): The path to the output file.
        """
        with open(output_path, "w") as f:
            for chunk in dialog_data.chunks:
                f.write(f"Chunk: {chunk.content}\n")
                for statement in chunk.statements:
                    f.write(f"  - Statement: {statement.statement}\n")
                    if statement.temporal_validity:
                        f.write(f"    - Valid At: {statement.temporal_validity.valid_at}\n")
                        f.write(f"    - Invalid At: {statement.temporal_validity.invalid_at}\n")
                    else:
                        f.write(f"    - Temporal Validity: Not Extracted\n")
                f.write("\n")