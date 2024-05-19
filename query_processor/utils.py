from typing import Callable

import docx


def for_all_runs(paragraph, func: Callable[[docx.text.run.Run], None]):
    for paragraph in paragraph.paragraphs:
        for run in paragraph.runs:
            func(run)