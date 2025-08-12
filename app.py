import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import copy
import random

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# A global dictionary to store the state of each running simulation
simulations = {}

# --- Helper Functions ---
def generate_random_color():
    """Generates a random pastel hex color."""
    r = random.randint(150, 255)
    g = random.randint(150, 255)
    b = random.randint(150, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def validate_process(process):
    """
    Validate individual process dict.
    Must have 'id' (str), 'arrivalTime' (non-negative int), 'burstTime' (positive int).
    'priority' is now an optional field.
    """
    if not isinstance(process, dict):
        return False, "Process should be a dictionary"
    if 'id' not in process or not isinstance(process['id'], str):
        return False, "Process must have a string 'id'"
    if 'arrivalTime' not in process or not (isinstance(process['arrivalTime'], int) and process['arrivalTime'] >= 0):
        return False, f"Process {process['id']} must have non-negative integer 'arrivalTime'"
    if 'burstTime' not in process or not (isinstance(process['burstTime'], int) and process['burstTime'] > 0):
        return False, f"Process {process['id']} must have positive integer 'burstTime'"
    if 'priority' in process and not isinstance(process['priority'], int):
        return False, f"Process {process['id']}'s 'priority' must be an integer"
    if 'color' in process and not isinstance(process['color'], str):
        return False, f"Process {process['id']}'s 'color' must be a string"
    return True, ""

def sanitize_processes(processes):
    """
    Validate and fill missing optional fields.
    """
    validated_processes = []
    for p in processes:
        valid, msg = validate_process(p)
        if not valid:
            return None, msg
        proc = p.copy()
        if 'priority' not in proc:
            proc['priority'] = 0  # Default priority if not given
        validated_processes.append(proc)
    return validated_processes, ""

def calculate_metrics(completed_processes):
    """Calculates and returns the average waiting, turnaround, and response times."""
    if not completed_processes:
        return {
            "avgWaitingTime": 0.0,
            "avgTurnaroundTime": 0.0,
            "avgResponseTime": 0.0,
        }

    total_waiting_time = sum(p['waitingTime'] for p in completed_processes)
    total_turnaround_time = sum(p['turnaroundTime'] for p in completed_processes)
    total_response_time = sum(p['responseTime'] for p in completed_processes)

    num_processes = len(completed_processes)

    return {
        "avgWaitingTime": round(total_waiting_time / num_processes, 3),
        "avgTurnaroundTime": round(total_turnaround_time / num_processes, 3),
        "avgResponseTime": round(total_response_time / num_processes, 3),
    }

# --- Stateful Scheduling Logic ---

def run_step_scheduler(state):
    """
    Runs one step of the scheduling algorithm based on the state.
    This function contains the core logic for all algorithms in a step-by-step fashion.
    """
    # Unpack state
    processes = state['processes']
    algorithm = state['algorithm']
    current_time = state['currentTime']
    quantum = state['quantum']
    ready_queue = state['readyQueue']
    completed_processes = state['completedProcesses']
    gantt_chart = state['ganttChart']
    
    # Check for newly arrived processes and add them to the ready queue
    arrived_this_step = [p for p in processes if p['arrivalTime'] == current_time and p['remainingBurstTime'] > 0]
    for p in arrived_this_step:
        ready_queue.append(p)

    # Re-sort the ready queue based on the algorithm's priority
    if algorithm == 'sjf-preemptive':
        ready_queue.sort(key=lambda p: p['remainingBurstTime'])
    elif algorithm == 'priority':
        ready_queue.sort(key=lambda p: p['priority'])
    
    current_process = None
    if ready_queue:
        current_process = ready_queue[0]

    if not current_process:
        # CPU is idle
        if gantt_chart and gantt_chart[-1]['id'] == 'Idle':
            gantt_chart[-1]['end'] += 1
        else:
            gantt_chart.append({'id': 'Idle', 'start': current_time, 'end': current_time + 1, 'color': '#ccc'})
    else:
        # Process is running
        if not current_process['hasStarted']:
            current_process['responseTime'] = current_time - current_process['arrivalTime']
            current_process['hasStarted'] = True

        run_time = 1
        # For non-preemptive algorithms, we run for the whole burst time in one go
        # This part of the logic is simplified for the step-by-step simulation and might not fully reflect true behavior.
        # The frontend's 'Next Step' button is designed for a single time unit, so we'll treat all runs as single steps.
        
        if gantt_chart and gantt_chart[-1]['id'] == current_process['id']:
            gantt_chart[-1]['end'] += 1
        else:
            gantt_chart.append({'id': current_process['id'], 'start': current_time, 'end': current_time + 1, 'color': current_process['color']})
        
        current_process['remainingBurstTime'] -= 1

        if current_process['remainingBurstTime'] <= 0:
            current_process['completionTime'] = current_time + 1
            current_process['turnaroundTime'] = current_process['completionTime'] - current_process['arrivalTime']
            current_process['waitingTime'] = current_process['turnaroundTime'] - current_process['burstTime']
            completed_processes.append(ready_queue.pop(0))
        elif algorithm == 'round-robin' and (current_time + 1) % quantum == 0:
            # Time quantum is up, move to the end of the queue
            ready_queue.append(ready_queue.pop(0))
            
    # Advance time
    state['currentTime'] += 1
    
    # Add new arrivals to the ready queue for the next step, as some algorithms need this for preemption
    new_arrivals = [p for p in processes if p['arrivalTime'] == state['currentTime']]
    for p in new_arrivals:
        if p not in ready_queue: # prevent duplicates
            ready_queue.append(p)

    return state

# --- Flask API Endpoints ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/start-simulation', methods=['POST'])
def start_simulation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    processes = data.get('processes', [])
    algorithm = data.get('algorithm')
    quantum = data.get('quantum', 2)

    processes, error_msg = sanitize_processes(processes)
    if processes is None:
        return jsonify({"error": error_msg}), 400

    # Initialize a new simulation state and assign colors on the backend
    sim_id = str(uuid.uuid4())
    simulations[sim_id] = {
        'processes': [
            {**p, 'remainingBurstTime': p['burstTime'], 'hasStarted': False, 'responseTime': -1, 'color': generate_random_color()}
            for p in sorted(processes, key=lambda p: p['arrivalTime'])
        ],
        'algorithm': algorithm,
        'quantum': int(quantum) if isinstance(quantum, (int, str)) and int(quantum) > 0 else 2,
        'currentTime': 0,
        'readyQueue': [],
        'completedProcesses': [],
        'ganttChart': [],
    }

    return jsonify({"simulationId": sim_id})

@app.route('/step-simulation', methods=['POST'])
def step_simulation():
    data = request.get_json()
    sim_id = data.get('simulationId')
    
    if sim_id not in simulations:
        return jsonify({"error": "Invalid or expired simulation ID."}), 404

    state = simulations[sim_id]

    if len(state['completedProcesses']) == len(state['processes']):
        # All processes are complete, return final metrics
        metrics = calculate_metrics(state['completedProcesses'])
        return jsonify({
            "isComplete": True,
            "metrics": metrics,
            "ganttChart": state['ganttChart'],
        })
    
    # Run one step of the simulation
    new_state = run_step_scheduler(state)
    simulations[sim_id] = new_state
    
    metrics = calculate_metrics(new_state['completedProcesses'])
    
    return jsonify({
        "isComplete": False,
        "metrics": metrics,
        "ganttChart": new_state['ganttChart'],
        "completedProcesses": new_state['completedProcesses'] # Send back all process info for tooltips
    })

@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    processes = data.get('processes', [])
    algorithm = data.get('algorithm')
    quantum = data.get('quantum', 2)
    
    processes, error_msg = sanitize_processes(processes)
    if processes is None:
        return jsonify({"error": error_msg}), 400

    # The full run will be simulated by starting a session and stepping until completion
    sim_id = str(uuid.uuid4())
    # Initialize a new simulation state and assign colors
    simulations[sim_id] = {
        'processes': [
            {**p, 'remainingBurstTime': p['burstTime'], 'hasStarted': False, 'responseTime': -1, 'color': generate_random_color()}
            for p in sorted(processes, key=lambda p: p['arrivalTime'])
        ],
        'algorithm': algorithm,
        'quantum': int(quantum) if isinstance(quantum, (int, str)) and int(quantum) > 0 else 2,
        'currentTime': 0,
        'readyQueue': [],
        'completedProcesses': [],
        'ganttChart': [],
    }

    state = simulations[sim_id]
    while len(state['completedProcesses']) < len(state['processes']):
        state = run_step_scheduler(state)
        
    metrics = calculate_metrics(state['completedProcesses'])
    
    # Cleanup the simulation state after completion
    del simulations[sim_id]
    
    return jsonify({
        "ganttChart": state['ganttChart'],
        "metrics": metrics,
        "completedProcesses": state['completedProcesses'],
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
