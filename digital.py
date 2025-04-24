import simpy
import random
import matplotlib.pyplot as plt

# Constants
ASSEMBLY_TIME = 5       # Minutes per engine at each stage
TEST_TIME = 3           # Time to test an engine
FAILURE_PROB = 0.1      # 10% chance machine fails
REPAIR_TIME = 4         # Time to repair a machine
NUM_WORKERS = 3         # Number of technicians available
SIM_DURATION = 100      # Total simulation time in minutes

# Tracking
assembled_engines = 0
machine_downtime = 0
repair_count = 0

# Time-series data for dashboard
time_points = []
engine_count_series = []
downtime_series = []
repair_series = []

def engine_assembly(env, worker, machine):
    global assembled_engines

    while True:
        with worker.request() as req:
            yield req
            yield env.timeout(ASSEMBLY_TIME)

        # Simulate failure
        if random.random() < FAILURE_PROB:
            env.process(repair_machine(env, machine))

        yield env.timeout(TEST_TIME)
        assembled_engines += 1

        # Record data
        time_points.append(env.now)
        engine_count_series.append(assembled_engines)
        downtime_series.append(machine_downtime)
        repair_series.append(repair_count)

        print(f"[{env.now} min] Engine assembled. Total: {assembled_engines}")

def repair_machine(env, machine):
    global machine_downtime, repair_count

    with machine.request() as req:
        yield req
        print(f"[{env.now} min] Machine failure! Starting repair...")
        start = env.now
        yield env.timeout(REPAIR_TIME)
        duration = env.now - start
        machine_downtime += duration
        repair_count += 1
        print(f"[{env.now} min] Repair complete. Downtime: {duration} min")

def run_simulation():
    global assembled_engines, machine_downtime, repair_count

    env = simpy.Environment()
    worker = simpy.Resource(env, capacity=NUM_WORKERS)
    machine = simpy.Resource(env, capacity=1)

    for _ in range(2):
        env.process(engine_assembly(env, worker, machine))

    env.run(until=SIM_DURATION)

    print("\nSimulation Summary:")
    print(f"Engines Assembled: {assembled_engines}")
    print(f"Total Machine Downtime: {machine_downtime} minutes")
    print(f"Number of Repairs: {repair_count}")
    print(f"Avg. Time Between Failures: {SIM_DURATION / max(repair_count, 1):.2f} minutes")

    # Plot the dashboard
    plot_dashboard()

def plot_dashboard():
    plt.figure(figsize=(12, 6))

    # Subplot 1: Engine Count
    plt.subplot(3, 1, 1)
    plt.plot(time_points, engine_count_series, label="Engines Assembled", color='green')
    plt.ylabel("Engines")
    plt.title("Engine Assembly Progress Over Time")
    plt.grid(True)

    # Subplot 2: Downtime
    plt.subplot(3, 1, 2)
    plt.plot(time_points, downtime_series, label="Total Downtime", color='red')
    plt.ylabel("Minutes")
    plt.title("Cumulative Machine Downtime")
    plt.grid(True)

    # Subplot 3: Repairs
    plt.subplot(3, 1, 3)
    plt.plot(time_points, repair_series, label="Repairs", color='blue')
    plt.xlabel("Simulation Time (min)")
    plt.ylabel("Repair Count")
    plt.title("Number of Machine Repairs")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()
