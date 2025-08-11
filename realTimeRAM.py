import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

class RAMMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time RAM Consumption Monitor")
        self.root.geometry("600x500")

        ttk.Label(root, text="RAM Usage", font=("Arial", 14, "bold")).pack(pady=10)

        self.ram_bar = ttk.Progressbar(root, length=400, mode='determinate')
        self.ram_bar.pack(pady=5)

        self.ram_label = ttk.Label(root, text="Loading...", font=("Arial", 12))
        self.ram_label.pack()

        # CPU & RAM Usage Graph
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Usage (%)")
        self.ax.set_title("CPU & RAM Usage Over Time")
        self.x_data, self.cpu_data, self.ram_data = [], [], []
        self.line_cpu, = self.ax.plot([], [], label="CPU Usage (%)", color='r')
        self.line_ram, = self.ax.plot([], [], label="RAM Usage (%)", color='b')
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Process Table
        self.process_frame = ttk.LabelFrame(root, text="Top Processes by Memory Usage")
        self.process_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(self.process_frame, columns=("PID", "Name", "Memory %"), show="headings")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="Process Name")
        self.tree.heading("Memory %", text="Memory (%)")
        self.tree.pack(fill='both', expand=True)

        # Start updating data
        self.update_data()
        self.start_process_thread()  # Start process monitoring in a thread

    def update_data(self):
        """Updates RAM and CPU usage."""
        ram_info = psutil.virtual_memory()
        ram_percent = ram_info.percent
        cpu_percent = psutil.cpu_percent()

        # Update progress bar and label
        self.ram_bar["value"] = ram_percent
        self.ram_label.config(text=f"RAM Usage: {ram_percent:.2f}%")

        # Update graph data
        if len(self.x_data) > 50:  # Limit history size
            self.x_data.pop(0)
            self.cpu_data.pop(0)
            self.ram_data.pop(0)

        self.x_data.append(time.time() % 60)  # Keep time within a minute
        self.cpu_data.append(cpu_percent)
        self.ram_data.append(ram_percent)

        self.line_cpu.set_data(self.x_data, self.cpu_data)
        self.line_ram.set_data(self.x_data, self.ram_data)

        self.ax.set_xlim(max(0, self.x_data[0] - 1), self.x_data[-1] + 1)
        self.ax.set_ylim(0, 100)
        self.canvas.draw()

        self.root.after(1000, self.update_data)  # Refresh every second

    def start_process_thread(self):
        """Starts a thread to fetch process data without blocking the UI."""
        self.process_thread = threading.Thread(target=self.process_monitor_loop, daemon=True)
        self.process_thread.start()

    def process_monitor_loop(self):
        """Continuously updates the process list every second."""
        while True:
            self.update_processes()
            time.sleep(1)  # Update process list every second

    def update_processes(self):
        """Fetches top memory-consuming processes and updates the UI."""
        process_list = []
        
        # Efficiently fetch process details
        for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                if p.info['memory_percent'] and p.info['memory_percent'] > 0:
                    process_list.append((p.pid, p.info['name'], p.info['memory_percent']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  # Skip if process is unresponsive or inaccessible

        process_list.sort(key=lambda x: x[2], reverse=True)  # Sort by memory usage

        # Use root.after to safely update the UI from another thread
        self.root.after(0, self.update_tree, process_list[:10])  # Show top 10 processes

    def update_tree(self, process_list):
        """Updates the process table in the UI."""
        self.tree.delete(*self.tree.get_children())  # Clear old data
        for pid, name, mem_percent in process_list:
            self.tree.insert("", "end", values=(pid, name, f"{mem_percent:.2f}%"))


# Run application
if __name__ == "__main__":
    root = tk.Tk()
    app = RAMMonitor(root)
    root.mainloop()
