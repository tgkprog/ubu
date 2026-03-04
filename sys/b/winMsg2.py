import gi
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class AtnApp(Gtk.Window):
    def __init__(self):
        # Set window title and default size
        super().__init__(title="Atn. Monitor")
        self.set_default_size(300, 150)
        self.set_border_width(10)
        self.move(300, 450)

        # 1. Handle Command Line Argument for Label
        # sys.argv[0] is the script name, sys.argv[1] is the first param
        arg_input = sys.argv[1] if len(sys.argv) > 1 else ""
        display_text = arg_input if arg_input.strip() else "Atn."     
        label = Gtk.Label(label=display_text)
        self.add(label)

        # 2. Dynamic Dock Icon Setup
        self.icons = ["/b/res/red.png", "/b/res/blue.png"]
        self.current_index = 0
        
        # Start timer: 1 second interval (1000ms)
        GLib.timeout_add_seconds(1, self.update_icon)
        self.update_icon()

    def update_icon(self):
        try:
            self.set_icon_from_file(self.icons[self.current_index])
            self.current_index = (self.current_index + 1) % 2
        except Exception as e:
            print(f"Icon Error: {e}")
        return True

    def force_to_front(self):
        # 3. Separate try-catch to bring window to front
        try:
            # present() deiconifies (unminimizes) and raises the window
            self.present()
            # Optional: Ask the Window Manager to treat this as urgent
            self.set_urgency_hint(True) 
        except Exception as e:
            print(f"Focus Error: {e}")

# Run the Application
if __name__ == "__main__":
    app = AtnApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()

    # Call bring-to-front after show_all()
    app.force_to_front()
    
    Gtk.main()

