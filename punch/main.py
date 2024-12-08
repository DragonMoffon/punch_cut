from punch.lib.application import Window
from punch.views.root import RootView

def main() -> None:
    win = Window()
    root = RootView()

    win.show_view(root)
    win.run()
