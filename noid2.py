import tkinter as tk
from tkinter import ttk
import subprocess

class WiFiManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wi-Fi Manager")

        self.ssids = []
        self.selected_ssid = tk.StringVar()
        self.ssid_listbox = None
        self.log_text = None

        self.create_ui()

    def create_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ssid_label = ttk.Label(main_frame, text="Available Wi-Fi Networks:")
        ssid_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        self.ssid_listbox = tk.Listbox(main_frame, selectmode=tk.SINGLE, height=10, width=30)
        self.ssid_listbox.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        ssid_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.ssid_listbox.yview)
        ssid_scrollbar.grid(row=1, column=1, pady=(0, 10), sticky=(tk.N, tk.S))
        self.ssid_listbox.config(yscrollcommand=ssid_scrollbar.set)

        refresh_button = ttk.Button(main_frame, text="Refresh", command=self.refresh_ssids)
        refresh_button.grid(row=2, column=0, pady=(0, 10), sticky=tk.W)

        connect_button = ttk.Button(main_frame, text="Connect", command=self.connect_wifi)
        connect_button.grid(row=2, column=1, pady=(0, 10), sticky=tk.E)

        disconnect_button = ttk.Button(main_frame, text="Disconnect", command=self.disconnect_wifi)
        disconnect_button.grid(row=2, column=2, pady=(0, 10), sticky=tk.E)

        self.ssid_listbox.bind("<<ListboxSelect>>", self.on_ssid_selected)

        self.log_text = tk.Text(main_frame, height=5, width=50)
        self.log_text.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)

        self.refresh_ssids()

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def refresh_ssids(self):
        networks = self.get_wifi_networks()

        self.ssids.clear()

        try:
            for network in networks:
                ssid = network.split(":")[1].strip()
                self.ssids.append(ssid)

        except IndexError as error:
            self.log_message("Error retrieving network information: " + str(error))
            return

        self.update_ssid_listbox()

    def get_wifi_networks(self):
        try:
            output = subprocess.check_output(["netsh", "wlan", "show", "network"], universal_newlines=True)
        except subprocess.CalledProcessError as error:
            self.log_message("Error retrieving network information: " + str(error))
            return []

        self.log_message("Raw Output:\n" + output)

        networks = [line.strip() for line in output.splitlines() if "SSID" in line]

        return networks

    def update_ssid_listbox(self):
        if self.ssid_listbox:
            self.ssid_listbox.delete(0, tk.END)
            for ssid in self.ssids:
                self.ssid_listbox.insert(tk.END, ssid)

    def on_ssid_selected(self, event):
        widget = event.widget
        selected_index = widget.curselection()
        if selected_index:
            self.selected_ssid.set(widget.get(selected_index))
        else:
            self.selected_ssid.set("")

    def connect_wifi(self):
        selected_ssid = self.selected_ssid.get()
        if selected_ssid:
            self.connect_to_wifi(selected_ssid)

    def disconnect_wifi(self):
        selected_ssid = self.selected_ssid.get()
        if selected_ssid:
            self.disconnect_from_wifi(selected_ssid)

    def connect_to_wifi(self, ssid):
        try:
            subprocess.check_output(["netsh", "wlan", "connect", "name=" + ssid], universal_newlines=True)
            self.log_message("Connected to: " + ssid)
        except subprocess.CalledProcessError as error:
            self.log_message("Error connecting to " + ssid + ": " + str(error))

    def disconnect_from_wifi(self, ssid):
        try:
            subprocess.check_output(["netsh", "wlan", "disconnect"], universal_newlines=True)
            self.log_message("Disconnected from: " + ssid)
        except subprocess.CalledProcessError as error:
            self.log_message("Error disconnecting from " + ssid + ": " + str(error))

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiManagerApp(root)
    root.mainloop()
