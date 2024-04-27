from docx2pdf import convert as convert_docx_to_pdf

from query_processor.templates.docx_template import DocxTemplate


class LetterMaintenanceDocxTemplate(DocxTemplate):
    template = './query_processor/templates/docs/LetterMaintenance.docx'
    __fields = [
        'date', 'id', 'timestamp', 'main_application',
        'patent_id', 'patent_name', 'payment_order', 'payment_date', 'payment_count'
    ]
    output_file_prefix = 'Letter_maintenance'


class LetterMaintenancePdfTemplate(LetterMaintenanceDocxTemplate):

    # Для конвертации word в pdf используется библиотека docx2pdf
    # также есть вариант использовать pandoc
    # TODO: попробовать другие варианты конвертации
    def fill(self, fields) -> str:
        docx_file = super().fill(fields)
        pdf_file = docx_file.replace('.docx', '.pdf')
        convert_docx_to_pdf(docx_file, pdf_file)

        return pdf_file
