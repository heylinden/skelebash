from __future__ import annotations
import os, sys, re, typing, time


class Style:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    STRIKETHROUGH = '\033[9m'
    UNDERLINE = '\033[4m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ORANGE = '\033[38;5;208m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BRIGHT_ORANGE = '\033[38;5;214m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'
    BG_ORANGE = '\033[48;5;208m'

def printStyle(*args) -> None:
    print(*args, Style.RESET)
def printStyleInline(*args) -> None:
    print(" ".join(args) + Style.RESET, end="", flush=True)
def printTypewriter(text: str, delay: float = 0.02, printer: typing.Callable = lambda s: print(s, end="", flush=True)) -> None:
    _ansi = re.compile(r'\033\[[0-9;]*m')
    i: int = 0
    while i < len(text):
        if text[i] == "\033":
            m: re.Match | None = _ansi.match(text, i)
            if m:
                printer(m.group(0))
                i = m.end()
                continue
        elif text[i] == "\t":
            time.sleep(0.5)
            continue
        printer(text[i])
        if "--fast" not in sys.argv:
            time.sleep(delay)
        i += 1
    print(f"{Style.RESET}")
def printCommandPrompt(cmd: str, info: str, printer: typing.Callable = lambda text: printTypewriter(text, 0.005)) -> None:
    indentation: str = " " * (len(re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', str(cmd))) + 3)
    new_info: str = info.replace('\n', '\n' + indentation)
    printer(f"{Style.BOLD}[{cmd}{Style.RESET}{Style.BOLD}]{Style.RESET} {new_info}")
def breakLine(count: int = 1) -> None:
    print("\n" * (count - 1))
def clearScreen() -> None:
    if "--no-clear" not in sys.argv:
        os.system("cls" if os.name == "nt" else "clear")
def printPanel(text: str, printer: typing.Callable = printStyle) -> None:
    plain_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
    content_width = max([len(line) + 2 for line in plain_text.split("\n")])
    content_width += 1 if content_width % 2 != 0 else 0
    printer(f"╭{'─'*content_width}╮")
    for plain_line, line in zip(plain_text.split("\n"), text.split("\n")):
        printer(f"│{' ' * ((content_width - len(plain_line)) // 2)}{line}{' ' * ((content_width - len(plain_line)) // 2 + (1 if len(plain_line) % 2 != 0 else 0))}{Style.RESET}│")
    printer(f"╰{'─'*content_width}╯")
def printCentered(text: str) -> None:
    plain_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
    plain_centered: str = plain_text.center(os.get_terminal_size().columns)
    printStyle(" " * (len(plain_centered) - len(plain_centered.lstrip())) + text)
def enterToContinue(show_text: bool = True) -> None:
    if "--no-clear" not in sys.argv and "--fast" not in sys.argv and show_text:
        printCentered(f"{Style.BRIGHT_BLACK}{Style.BOLD}-- press enter to continue --")
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            ...
def toIdentifier(s: str) -> str:
    new_s: str = ""
    for char in s:
        if char.isupper():
            new_s += f"_{char.lower()}"
        else:
            new_s += char
    new_s = new_s.removeprefix("_")
    return new_s
def prompt(key: str, skelebash: Skelebash | None = None, safe: bool = False) -> str:
    while True:
        try:
            return input(f"{key}> ").strip().lower()
        except KeyboardInterrupt:
            breakLine()
        except EOFError:
            breakLine()
            if skelebash:
                skelebash.saveGame()
                if not skelebash.temp:
                    printStyle(f"{Style.BRIGHT_GREEN}game saved to {skelebash.id}.save")
                exit(0)
            elif not safe:
                breakLine()
                printStyle(f"{Style.BRIGHT_RED}are you sure? your game may not be saved if you continue. (y/N)")
                inp: str = input(f"{Style.BRIGHT_RED}^d> ").strip().lower()
                if inp == "y":
                    exit(0)
                else:
                    printStyleInline(Style.RESET)
                    continue
            else:
                exit(0)