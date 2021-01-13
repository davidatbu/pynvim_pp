from os import linesep
from string import whitespace
from typing import Iterable, Literal, Mapping, Sequence, Tuple, TypeVar, Union

from pynvim import Nvim
from pynvim.api import Buffer

T = TypeVar("T")

VisualTypes = Union[Literal["char"], Literal["line"], Literal["block"], None]


def writable(nvim: Nvim, buf: Buffer) -> bool:
    is_modifiable: bool = nvim.api.buf_get_option(buf, "modifiable")
    return is_modifiable


def operator_marks(
    nvim: Nvim, buf: Buffer, visual_type: VisualTypes
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    (1, 0) indexed
    """

    mark1, mark2 = ("[", "]") if visual_type else ("<", ">")
    row1, col1 = nvim.api.buf_get_mark(buf, mark1)
    row2, col2 = nvim.api.buf_get_mark(buf, mark2)
    return (row1, col1), (row2, col2)


def set_visual_selection(
    nvim: Nvim, buf: Buffer, mark1: Tuple[int, int], mark2: Tuple[int, int]
) -> None:
    """
    (1, 1) indexed
    """

    (row1, col1), (row2, col2) = mark1, mark2
    nvim.funcs.setpos("'<", (buf.number, row1, col1 + 1, 0))
    nvim.funcs.setpos("'>", (buf.number, row2, col2 + 1, 0))


def get_selected(nvim: Nvim, buf: Buffer, visual_type: VisualTypes) -> str:
    (row1, col1), (row2, col2) = operator_marks(nvim, buf=buf, visual_type=visual_type)
    row1, row2 = row1 - 1, row2 - 1

    lines: Sequence[str] = nvim.api.buf_get_lines(buf, row1, row2 + 1, True)

    if len(lines) == 1:
        return lines[0].encode()[col1 : col2 + 1].decode()
    else:
        head = lines[0].encode()[col1:].decode()
        body = lines[1:-1]
        tail = lines[-1].encode()[: col2 + 1].decode()
        return linesep.join((head, *body, tail))


def p_indent(line: str, tabsize: int) -> int:
    ws = {*whitespace}
    for idx, char in enumerate(line.expandtabs(tabsize), start=1):
        if char not in ws:
            return idx - 1
    else:
        return 0


def escape(stream: Iterable[T], escape: Mapping[T, T]) -> Iterable[T]:
    for unit in stream:
        if unit in escape:
            yield escape[unit]
        else:
            yield unit
