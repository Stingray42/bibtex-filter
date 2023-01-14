import re

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
from rich.console import RenderableType
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Static, Input, Label

from _localization import gettext as _


def full_text_search(bib: BibDatabase, regex: re.Pattern) -> BibDatabase:
    out = []
    for entry in bib.entries:
        for k, v in entry.items():
            if regex.findall(v):
                out.append(entry)
                break
    result = BibDatabase()
    result.entries = out
    return result


class BibtexContent(Static):
    content = reactive(str)

    def watch_content(self, content: str) -> None:
        self.refresh(repaint=False, layout=True)

    def render(self) -> RenderableType:
        return self.content


class Indicator(Label):
    case_insensitive = reactive(True)

    def toggle(self) -> None:
        self.case_insensitive = not self.case_insensitive

    def render(self) -> RenderableType:
        if self.case_insensitive:
            return '/[b]i[/b] '
        else:
            return '/ '


class SearchBar(Static):
    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def compose(self) -> ComposeResult:
        yield Label('> /')
        yield Input(placeholder=_('Regular expression'))
        yield Indicator()


class CustomFooter(Footer):
    error: Exception = reactive(None)

    def watch_error(self, error: Exception):
        if error:
            self.add_class('error')
        else:
            self.remove_class('error')

    def render(self) -> RenderableType:
        if self._key_text is None:
            self._key_text = self.make_key_text()
        if self.error:
            error_text = Text(str(self.error), style='underline')
            gap_width = self.container_size.width - self._key_text.cell_len - error_text.cell_len
            return self._key_text.copy().append(' ' * gap_width).append_text(error_text)
        else:
            return self._key_text


# todo wait for PR https://github.com/Textualize/textual/pull/1033 to be merged and remove
from functools import wraps


def debounce(timeout: float):
    def decorator(f):
        timer = None

        @wraps(f)
        async def wrapper(self: App, *args, **kwargs) -> None:
            nonlocal timer
            if timer:
                timer.stop_no_wait()

            timer = self.set_timer(timeout, lambda: f(self, *args, **kwargs))

        return wrapper

    return decorator


class BibtexFilter(App[str]):
    CSS_PATH = 'main.css'
    BINDINGS = [
        ('escape', 'quit', _('Close')),
        ('ctrl+b', 'toggle_case_sensitive', _('Case-sensitive search')),  # todo better shortcuts
        ('ctrl+t', 'toggle_dark', _('Dark mode')),
    ]

    pattern = reactive(str, init=False)
    flags = reactive(int, init=False)
    regex: re.Pattern = reactive(None, init=False)
    result: BibDatabase = reactive(None, init=False)

    bib: BibDatabase
    writer: BibTexWriter

    def __init__(self, bibtex: str):
        super().__init__(watch_css=True)
        self.writer = BibTexWriter()
        self.writer.indent = ' ' * 4
        self.bib = bibtexparser.loads(bibtex)

    def on_mount(self) -> None:
        self.result = self.bib

    def compute_pattern(self) -> str:
        return self.query_one(Input).value

    def compute_flags(self) -> int:
        return re.IGNORECASE if self.query_one(Indicator).case_insensitive else 0

    def watch_pattern(self, pattern: str) -> None:
        try:
            self.regex = re.compile(pattern, self.flags)
            self.query_one(CustomFooter).error = None
        except re.error as e:
            self.query_one(CustomFooter).error = e

    def watch_flags(self, flags: int) -> None:
        try:
            self.regex = re.compile(self.pattern, flags)
            self.query_one(CustomFooter).error = None
        except re.error as e:
            self.query_one(CustomFooter).error = e

    def watch_regex(self, regex: re.Pattern) -> None:
        self.result = full_text_search(self.bib, regex)

    def watch_result(self, result: BibDatabase) -> None:
        self.query_one(BibtexContent).content = bibtexparser.dumps(result, self.writer)

    def watch_dark(self, dark: bool) -> None:
        self.query_one(BibtexContent).dark = dark
        super().watch_dark(dark)

    async def action_quit(self) -> None:
        self.exit(None)

    def action_toggle_case_sensitive(self) -> None:
        self.query_one(Indicator).toggle()
        self.flags = self.compute_flags()

    def action_scroll_up(self) -> None:
        self.query_one(Container).scroll_up()

    def action_scroll_down(self) -> None:
        self.query_one(Container).scroll_down()

    def action_page_up(self) -> None:
        self.query_one(Container).scroll_page_up(animate=False)

    def action_page_down(self) -> None:
        self.query_one(Container).scroll_page_down(animate=False)

    # @debounce(0.25)
    def on_input_changed(self, event: Input.Changed) -> None:
        self.pattern = event.value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        result = bibtexparser.dumps(self.result, self.writer)
        self.exit(result)

    def compose(self) -> ComposeResult:
        yield Container(BibtexContent())
        yield SearchBar()
        yield CustomFooter()


if __name__ == '__main__':
    import sys

    with open(sys.argv[1], encoding=sys.getdefaultencoding()) as f:
        print(BibtexFilter(f.read()).run())
