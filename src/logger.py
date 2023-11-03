import time
import logging
import warnings
from rich.theme import Theme
from rich.logging import RichHandler
from rich.console import Console
from rich.pretty import install as pretty_install
from rich.traceback import install as traceback_install

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

console = Console(log_time=True, log_time_format='%H:%M:%S-%f', theme=Theme({
    "traceback.border": "black",
    "traceback.border.syntax_error": "black",
    "inspect.value.border": "black",
}))

lg = logging.getLogger("sd")
rh = RichHandler(show_time=True, omit_repeated_times=False, show_level=True, show_path=False, markup=False, rich_tracebacks=True, log_time_format='%H:%M:%S-%f', level=logging.DEBUG, console=console)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[rh])
lg.setLevel(logging.DEBUG)

pretty_install(console=console)
traceback_install(console=console, extra_lines=1, max_frames=10, width=console.width, word_wrap=False, indent_guides=False, suppress=[])

buffer = []

def log(msg):
    buffer.append(f'{time.strftime("%H:%M:%S", time.gmtime())} {msg}')
    if len(buffer) > 10:
        buffer.pop(0)
    lg.info(msg)
    html = '<br>'.join(buffer)
    return html
