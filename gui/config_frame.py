import tkinter as tk

class ConfigFrame(tk.Frame):
    def __init__(self, master: Misc | None = None, cnf: dict[str, Any] | None = ..., *, background: str = ..., bd: _ScreenUnits = ..., bg: str = ..., border: _ScreenUnits = ..., borderwidth: _ScreenUnits = ..., class_: str = ..., colormap: Literal["new", ""] | Misc = ..., container: bool = ..., cursor: _Cursor = ..., height: _ScreenUnits = ..., highlightbackground: str = ..., highlightcolor: str = ..., highlightthickness: _ScreenUnits = ..., name: str = ..., padx: _ScreenUnits = ..., pady: _ScreenUnits = ..., relief: _Relief = ..., takefocus: _TakeFocusValue = ..., visual: str | tuple[str, int] = ..., width: _ScreenUnits = ..., filename: str) -> None:
        super().__init__(master, cnf, background=background, bd=bd, bg=bg, border=border, borderwidth=borderwidth, class_=class_, colormap=colormap, container=container, cursor=cursor, height=height, highlightbackground=highlightbackground, highlightcolor=highlightcolor, highlightthickness=highlightthickness, name=name, padx=padx, pady=pady, relief=relief, takefocus=takefocus, visual=visual, width=width)
        self.config_filename = filename
