import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import time


class RealtimeGraph:
    def __init__(self, num_curves=3):
        self.num_curves = num_curves
        self.data = [[] for _ in range(num_curves)]
        self.fig, self.ax = plt.subplots()
        self.lines = [self.ax.plot(
            [], [], label=f"Curve {i+1}")[0] for i in range(num_curves)]
        self.ax.legend()
        self.animation = None

    def append_data(self, new_data):
        for i, d in enumerate(new_data):
            self.data[i].append(d)

    def update_graph(self, frame):
        for i, line in enumerate(self.lines):
            line.set_data(range(len(self.data[i])), self.data[i])
        self.ax.relim()
        self.ax.autoscale_view()
        return self.lines

    def start_animation(self):
        self.animation = FuncAnimation(
            self.fig, self.update_graph, frames=range(len(self.data[0])),
            interval=100, blit=True
        )
        plt.show()


# Example usage
graph = RealtimeGraph(num_curves=3)


def generate_data():
    new_data = [random.randint(0, 10) for _ in range(graph.num_curves)]
    graph.append_data(new_data)

# Generate data every 20 milliseconds


def data_generation_loop():
    while True:
        generate_data()
        time.sleep(0.02)  # Delay for 20 milliseconds (0.02 seconds)


# Start the animation
graph.start_animation()

# Start the data generation loop in a separate thread
import threading
data_thread = threading.Thread(target=data_generation_loop)
data_thread.start()
