# https://abdus.dev/posts/monitor-clipboard/

import ctypes
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union, List, Optional

import win32api, win32clipboard, win32con, win32gui
import translators as ts
from ColorPrint import *

proxy = None


# def translate(text):
#     text = text.value
#     result = ""
#     ts_func_list = [ts.alibaba, ts.tencent, ts.google, ts.baidu, ts.bing, ts.caiyun]
#     ColorPrint.print_bold("Plain: " + text)
#     is_word = (" " in text)
#     for i, translator in enumerate(ts_func_list):
#         try:
#             result += "[" + str(translator).split(' ')[2].split('.')[0] + "]\r\n" + translator(text, to_language="zh",
#                                                                                                if_use_cn_host=True,
#                                                                                                timeout=3,
#                                                                                                proxy=proxy) + "\r\n"
#         except:
#             if i == len(ts_func_list) - 1:
#                 ColorPrint.print_fail("Translate Failed")
#                 return
#             continue
#         if is_word:
#             break
#     ColorPrint.print_pass(result)


class Clipboard:
    @dataclass
    class Clip:
        type: str
        value: Union[str, List[Path]]

    def __init__(
            self,
            trigger_at_start: bool = False,
            on_text: Callable[[str], None] = None,
            on_update: Callable[[Clip], None] = None,
            on_files: Callable[[str], None] = None,
    ):
        self._trigger_at_start = trigger_at_start
        self._on_update = on_update
        self._on_files = on_files
        self._on_text = on_text

    def _create_window(self) -> int:
        """
        Create a window for listening to messages
        :return: window hwnd
        """
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._process_message
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)

    def _process_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
        WM_CLIPBOARDUPDATE = 0x031D
        if msg == WM_CLIPBOARDUPDATE:
            self._process_clip()
        return 0

    def _process_clip(self):
        clip = self.read_clipboard()
        if not clip:
            return

        if self._on_update:
            self._on_update(clip)
        if clip.type == 'text' and self._on_text:
            self._on_text(clip.value)
        elif clip.type == 'files' and self._on_text:
            self._on_files(clip.value)

    @staticmethod
    def read_clipboard() -> Optional[Clip]:
        try:
            win32clipboard.OpenClipboard()

            clip_types = {
                # win32con.CF_HDROP: "files",
                win32con.CF_UNICODETEXT: "text",
                win32con.CF_TEXT: "text",
            }
            for type, type_str in clip_types.items():
                if win32clipboard.IsClipboardFormatAvailable(type):
                    return Clipboard.Clip(type_str,
                                          win32clipboard.GetClipboardData(type)
                                          .replace("\r\n", " ")
                                          .replace("\n", " ")
                                          .replace("- ", ""))   # support for `-\n`

            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                print("")

    def listen(self):
        if self._trigger_at_start:
            self._process_clip()

        def runner():
            hwnd = self._create_window()
            ctypes.windll.user32.AddClipboardFormatListener(hwnd)
            win32gui.PumpMessages()

        th = threading.Thread(target=runner, daemon=True)
        th.start()
        while th.is_alive():
            th.join(1)


if __name__ == '__main__':
    clipboard = Clipboard(on_update=translate, trigger_at_start=True)
    clipboard.listen()
