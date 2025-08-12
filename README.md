OS Process Scheduler Simulator
Project Overview
This project is a web-based simulator designed to visualize and compare various CPU scheduling algorithms used in operating systems. It provides a user-friendly interface to add processes with custom arrival times, burst times, and priorities, and then simulates how different algorithms would handle them. The results are displayed in a dynamic Gantt chart and with key performance metrics.

Key Features
Multiple Algorithms: Supports First-Come, First-Served (FCFS), Shortest Job First (SJF) (both non-preemptive and preemptive), Round Robin, Priority, and Multilevel Feedback Queue scheduling.

Visual Gantt Chart: Generates a dynamic Gantt chart to visually represent the execution timeline of each process.

Performance Metrics: Calculates and displays average waiting time, turnaround time, and response time for easy comparison.

Interactive Simulation: Allows for both a full-run comparison and a step-by-step simulation to see how the ready queue and CPU state change over time.

Responsive UI: A modern, clean interface built with Tailwind CSS that works well on both desktop and mobile devices.

Technologies Used
Backend: Python with the Flask framework

Frontend: HTML, CSS (Tailwind CSS), and JavaScript

State Management: The backend uses a stateful approach to handle incremental simulations for the "Next Step" feature.

How to Run the Simulator
Clone the repository:

git clone https://github.com/MukeshSingh123-tech/os-scheduler-simulator.git
cd os-scheduler-simulator

(Note: Replace the URL with your own repository URL).

Install Python dependencies:

pip install Flask Flask-Cors

Run the Flask application:

python app.py

Your backend server will start and be accessible at http://127.0.0.1:5000.

Open the application in your browser:
Navigate to http://127.0.0.1:5000 to view and use the simulator.

How to Use the Interface
Add Processes:

In the "Add Processes" section, enter the Process ID, Arrival Time, and Burst Time for each process.

For algorithms like Priority Scheduling and Multilevel Feedback Queue, make sure to also provide a Priority value.

Click "Add Process" to add the new process to the table.

Configure Simulation:

Select the two algorithms you want to compare from the dropdown menus.

If you select an algorithm like Round Robin, a "Time Quantum" field will appear, allowing you to set the time slice for each process.

Run the Simulation:

Click "Run Comparison" to execute both algorithms fully and see the final Gantt charts and performance metrics.

Click "Next Step" to advance the simulation one time unit at a time, watching the Gantt chart build step by step.

Click "Reset" to clear all processes and start over.
