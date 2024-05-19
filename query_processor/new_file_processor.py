import json
import re
from dataclasses import dataclass
from pathlib import Path

import docx

from query_processor.utils import for_all_runs
from utils.models import Document


@dataclass
class FieldMetadata:
    name: str
    gpt_description: str


def find_field_in_run(destination: set):
    def inner(run: docx.text.run.Run):
        for m in re.finditer(r'\{\{\s*(?P<field>\S*)\s}}', run.text):
            destination.add(m.group('field'))

    return inner


def get_all_fields(path: Path) -> set[str]:
    doc = docx.Document(str(path))
    res = set()
    for_all_runs(doc, find_field_in_run(res))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for_all_runs(cell, find_field_in_run(res))
    return res


async def process_new_file(path_to_file: Path, db_model: Document) -> set[str]:
    fields: set[str] = get_all_fields(path_to_file)
    metadata = [
        {"field": field, "gpt_description": "null"} for field in fields
    ]
    json_metadata = json.dumps(metadata)
    await db_model.update(fields_metadata=json_metadata).apply()
    return fields
