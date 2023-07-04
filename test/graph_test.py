import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np

# Function to update the graph with new data
def update_graph(x, y, lines):
    for i, line in enumerate(lines):
        line.set_data(x, y[i])
    plt.draw()

# Generate random data
num_lines = 5
num_points = 100
x = np.linspace(0, 1, num_points)
y = np.random.rand(num_lines, num_points)

# Initialize the plot
plt.ion()
fig, ax = plt.subplots()

# Create an empty list to store line objects
lines = []

# Create line objects and plot the initial data
for i in range(num_lines):
    line, = ax.plot(x, y[i])
    lines.append(line)

# Continuously update the graph with new data
while True:
    # Generate new random data
    y = np.random.rand(num_lines, num_points)

    # Update the graph
    update_graph(x, y, lines)
    plt.pause(0.001)
