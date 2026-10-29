"""Reloj compatible con MicroPython; facilita pruebas en CPython."""
import time


def now_ms():
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.monotonic() * 1000)


def elapsed(now, before):
    if hasattr(time, "ticks_diff"):
        return time.ticks_diff(now, before)
    return now - before
