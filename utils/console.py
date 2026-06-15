import subprocess
import sys


def configure_console_encoding() -> None:
    """Configure Windows terminals to display UTF-8 emoji and symbols."""
    if sys.platform != "win32":
        return

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)

        stdout_handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(stdout_handle, ctypes.byref(mode)):
            enable_vt = 0x0004
            kernel32.SetConsoleMode(stdout_handle, mode.value | enable_vt)
    except (AttributeError, OSError):
        pass

    try:
        subprocess.run(
            ["cmd", "/c", "chcp", "65001"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        pass

    for stream in (sys.stdout, sys.stderr):
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass
