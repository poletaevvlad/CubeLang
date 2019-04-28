from click import secho


class DisplayOptions:
    pass


def display_code_line(file, text: str, number: int, number_length: int,
                      max_width: int, use_color: bool = True):
    fopt = dict(color=use_color, reset=use_color)

    max_width -= number_length + 2
    secho(f"{number:{number_length}}  ", file, nl=False, **fopt)
    offset = 0
    while offset < len(text):
        secho(text[offset: offset + max_width], file, **fopt)
        offset += max_width
        if offset < len(text):
            secho(" " * (number_length + 2), file, nl=False, **fopt)


def display_code_error(file, text: str, start_line: int, end_line: int,
                       start_column: int = -1, end_column: int = -1,
                       use_color: bool = True):
    pass