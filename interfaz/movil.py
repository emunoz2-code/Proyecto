"""Vista web opcional para dispositivos en la misma red local."""
import os
from socket import gethostbyname, gethostname
import flet as ft
from main import ASSETS, main

if __name__ == "__main__":
    os.environ["FLET_FORCE_WEB_SERVER"] = "true"
    print(f"ATLAS en la red local: http://{gethostbyname(gethostname())}:8550", flush=True)
    ft.run(main, host="0.0.0.0", port=8550, view=None, assets_dir=str(ASSETS))
