from __future__ import annotations
import asyncio, tkinter, typing, io, contextlib, traceback

def skelepanel(skelebash: Skelebash, after: typing.Callable) -> None:  # type: ignore
    root: tkinter.Tk = tkinter.Tk()
    root.title("skelepanel™")

    tkinter.Label(root, text="skelepanel™", font=("Arial", 40)).pack()

    def run() -> None:
        stdout_buf.seek(0)
        stdout_buf.truncate(0)
        stderr_buf.seek(0)
        stderr_buf.truncate(0)
        ok: bool = False
        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                context: dict[str, typing.Any] = {
                    "game": skelebash,
                    "selected": skelebash.selected,
                    "select": skelebash.select,
                    "player": skelebash.player,
                    "player_character": skelebash.player_character,
                    "pc": skelebash.player_character,
                    "dungeon": skelebash.dungeon,
                    "room": skelebash.room,
                    "enemy": lambda i: skelebash.room.enemies[i],
                    "pinv": skelebash.player.inventory,
                    "pinvitem": lambda i: skelebash.player.inventory[i].item,
                    "pheal": skelebash.player.heal,
                    "phealst": skelebash.player.healStamina,
                    "phealmn": skelebash.player.healMana
                }
                exec(before.get().strip(), context)
                exec(before2.get().strip(), context)
                exec(before3.get().strip(), context)
                value: typing.Any = (exec if entry.get().strip().startswith("@") else eval)(entry.get().strip().removeprefix("@").strip() or "None", context)
                ok = True
        except Exception: # type: ignore
            stderr_buf.write(traceback.format_exc())

        out_text = stdout_buf.getvalue().strip()
        err_text = stderr_buf.getvalue().strip()

        result.config(text=str(value) if ok and str(value) != "None" else "no result")
        output.config(text=out_text or "no output")
        error.config(text=err_text.split("File \"<string>\", line 1", maxsplit=1)[-1].removeprefix(", in <module>").strip() if err_text else "nuffin :D")

    entry: tkinter.Entry = tkinter.Entry(root, font=("Arial", 20))
    def select_all(event: tkinter.Event) -> str:
        event.widget.select_range(0, "end")
        event.widget.icursor("end")
        return "break"

    entry.bind("<Control-a>", select_all)
    entry.bind("<Control-A>", select_all)
    entry.bind("<Return>", lambda _: run())
    entry.pack(fill="x", padx=10, pady=10)

    before: tkinter.Entry = tkinter.Entry(root, font=("Arial", 13))
    def select_all(event: tkinter.Event) -> str:
        event.widget.select_range(0, "end")
        event.widget.icursor("end")
        return "break"
    before.insert(0, "pass")
    before.bind("<Control-a>", select_all)
    before.bind("<Control-A>", select_all)
    before.bind("<Return>", lambda _: run())
    before.pack(fill="x", padx=10)

    before2: tkinter.Entry = tkinter.Entry(root, font=("Arial", 13))
    def select_all(event: tkinter.Event) -> str:
        event.widget.select_range(0, "end")
        event.widget.icursor("end")
        return "break"
    before2.insert(0, "pass")
    before2.bind("<Control-a>", select_all)
    before2.bind("<Control-A>", select_all)
    before2.bind("<Return>", lambda _: run())
    before2.pack(fill="x", padx=10)

    before3: tkinter.Entry = tkinter.Entry(root, font=("Arial", 13))
    def select_all(event: tkinter.Event) -> str:
        event.widget.select_range(0, "end")
        event.widget.icursor("end")
        return "break"
    before3.insert(0, "pass")
    before3.bind("<Control-a>", select_all)
    before3.bind("<Control-A>", select_all)
    before3.bind("<Return>", lambda _: run())
    before3.pack(fill="x", padx=10)
    
    result: tkinter.Label = tkinter.Label(root, text="result will appear here", font=("Courier", 20, "italic bold"), anchor="w", justify="left")
    result.pack(fill="x", padx=10)
    
    output: tkinter.Label = tkinter.Label(root, text="output will appear here", font=("Courier", 14, "italic"), anchor="w", justify="left")
    output.pack(fill="x", padx=10)

    error: tkinter.Label = tkinter.Label(root, text="errors will appear here", font=("Courier", 12, "italic"), fg="red", anchor="w", justify="left")
    error.pack(fill="x", padx=10, pady=(6, 10))

    stdout_buf: io.StringIO = io.StringIO()
    stderr_buf: io.StringIO = io.StringIO()
    tkinter.Button(root, text="run", command=run).pack(pady=(0, 8))

    root.minsize(600, 220)
    root.after(0, after) # type: ignore
    root.mainloop()