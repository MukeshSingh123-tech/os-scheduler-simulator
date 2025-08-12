# OS Process Scheduler Simulator

### Project Overview
This project is a web-based simulator designed to visualize and compare various CPU scheduling algorithms used in operating systems. It provides a user-friendly interface to add processes with custom arrival times, burst times, and priorities, and then simulates how different algorithms would handle them. The results are displayed in a Gantt chart and with key performance metrics.

### Key Features
* **Multiple Algorithms:** Supports First-Come, First-Served (FCFS), Shortest Job First (SJF) (non-preemptive and preemptive), Round Robin, Priority, and Multilevel Feedback Queue scheduling.
* **Visual Gantt Chart:** Generates a dynamic Gantt chart to visually represent the execution timeline of each process.
* **Performance Metrics:** Calculates and displays average waiting time, turnaround time, and response time for easy comparison.
* **Interactive Simulation:** Allows for both a full-run comparison and a step-by-step simulation to see how the ready queue and CPU state change over time.
* **Responsive UI:** A modern, clean interface built with Tailwind CSS that works well on both desktop and mobile devices.

### Technologies Used
* **Backend:** Python with the Flask framework
* **Frontend:** HTML, CSS (Tailwind CSS), and JavaScript
* **State Management:** The backend uses a simple stateful approach to manage incremental simulations for the "Next Step" feature.

### How to Run the Simulator

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/MukeshSingh123-tech/os-scheduler-simulator.git](https://github.com/MukeshSingh123-tech/os-scheduler-simulator.git)
    cd os-scheduler-simulator
    ```
    (Note: Replace the URL with your own repository URL if needed).

2.  **Install Python dependencies:**
    ```bash
    pip install Flask Flask-Cors
    ```

3.  **Run the Flask application:**
    ```bash
    python app.py
    ```

4.  **Open the application in your browser:**
    Navigate to `http://127.0.0.1:5000` in your web browser to view and use the simulator.
