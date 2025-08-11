# Real-Time RAM and CPU Usage Monitor

This is a Python GUI application that monitors and visualizes real-time system resource usage (RAM and CPU) using `Tkinter`, `psutil`, and `matplotlib`. It includes a dynamic usage graph, a RAM usage progress bar, and a live-updating table of the top 10 memory-consuming processes.

## Features

- 📊 Live CPU and RAM usage line chart  
- 📈 Real-time RAM usage progress bar  
- 🧠 Displays top memory-consuming processes with PID, name, and usage  
- ⏱ Refreshes every second with smooth UI updates using threading

## Requirements

- Python 3.x  
- `psutil`  
- `matplotlib`  
- `tkinter` (usually included with Python)

Install the required libraries:

```bash
pip install psutil matplotlib
