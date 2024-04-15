import uuid

from docx import Document

from query_processor.templates.template import Template


class LetterMaintenanceDocxTemplate(Template):
    __fields = [
        'date', 'id', 'first_application', 'timestamp', 'main_application',
        'patent_id', 'patent_name', 'payment_order', 'payment_count',
        'date', 'id'
    ]

    template = './docs/Letter_maintenance_template.docx'

    def get_fields(self):
        return self.__fields

    def fill(self, fields) -> str:
        doc = Document(self.template)
        output_file = f"../out/Letter_maintenance_{uuid.uuid4()}.docx"
        for paragraph in doc.paragraphs:
            for key, value in fields.items():
                if f'{{{{ {key} }}}}' in paragraph.text:
                    paragraph.text = paragraph.text.replace(f'{{{{ {key} }}}}', str(value))

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for key, value in fields.items():
                            if f'{{{{ {key} }}}}' in paragraph.text:
                                paragraph.text = paragraph.text.replace(f'{{{{ {key} }}}}', str(value))

        doc.save(output_file)
        return output_file
