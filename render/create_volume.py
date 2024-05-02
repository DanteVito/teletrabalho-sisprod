import typing

from docx import Document as Document_compose
from docxcompose.composer import Composer


def combine_docx(
    filename_initial: str, file_list: typing.List, filename_final: str
) -> None:
    """
    filename_initial: path arquivo inicial.
    filename_final: path arquivo final.
    file_list: lista com os paths dos arquivos
        que serão combinados.
    """
    n = len(file_list)
    master = Document_compose(filename_initial)
    composer = Composer(master)
    for i in range(0, n):
        doc_temp = Document_compose(file_list[i])
        composer.append(doc_temp)
    composer.save(filename_final)
