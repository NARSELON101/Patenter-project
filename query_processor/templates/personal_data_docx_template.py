from query_processor.templates.docx_template import DocxTemplate


class PersonalDataDocxTemplate(DocxTemplate):
    template = './query_processor/templates/docs/PersonalData.docx'
    __fields = ["name", "address", "document",
                "invention_name", "invention_register_number",
                "applicant", "signatory", "date"]
    output_file_prefix = 'Personal_data'
