from query_processor.templates.docx_template import DocxTemplate


class UserFileTemplate(DocxTemplate):

    def __init__(self, file: str):
        self.template = file