import uuid
from datetime import datetime

from docx import Document

from query_processor.templates.template import Template


class DocxTemplate(Template):
    template = ''
    __fields = []
    output_file_prefix = ''

    def get_fields(self):
        return self.__fields

    def fill(self, fields) -> str:
        doc = Document(self.template)
        output_file = f"./query_processor/out/{self.output_file_prefix}_{uuid.uuid4()}.docx"
        for paragraph in doc.paragraphs:
            for key, value in fields.items():
                for run in paragraph.runs:
                    if f'{{{{ {key} }}}}' in run.text:
                        if isinstance(value, datetime):
                            value = value.strftime('%d.%m.%Y')
                        run.text = run.text.replace(f'{{{{ {key} }}}}', str(value))

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for key, value in fields.items():
                            for run in paragraph.runs:
                                if f'{{{{ {key} }}}}' in run.text:
                                    if isinstance(value, datetime):
                                        value = value.strftime('%d.%m.%Y')
                                    run.text = run.text.replace(f'{{{{ {key} }}}}', str(value))

        doc.save(output_file)
        return output_file

