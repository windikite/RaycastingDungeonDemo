import sys, os

def resource_path(rel_path):
    if getattr(sys, "_MEIPASS", False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir)
        )
    return os.path.join(base, 'assets', rel_path)