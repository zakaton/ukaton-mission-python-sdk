import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Function to generate random data


def generate_data():
    return np.random.rand()


# Number of values to display
N = 100

# Create initial data array
data = np.zeros(N)

# Create a figure and an axis
fig, ax = plt.subplots()

# Create an empty line object
line, = ax.plot([], [])

# Set the axis limits
ax.set_xlim(0, N)
ax.set_ylim(0, 1)

# Initialize time
t = [0]  # Use a mutable object

# Function to update the plot


def update_plot(frame):
    t[0] += 20  # Increment time

    # Update the data array with new value
    data[:-1] = data[1:]
    data[-1] = generate_data()

    # Update the line data
    line.set_data(np.arange(N), data)

    return line,

# Function to initialize the plot


def init():
    # Update the x-axis labels
    num_ticks = 5  # Number of desired ticks
    tick_positions = np.linspace(0, N - 1, num_ticks, dtype=int)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([str(t[0] - (N - i - 1) * 20) for i in tick_positions])

    return line,


# Create the animation
ani = animation.FuncAnimation(
    fig, update_plot, init_func=init, frames=200, interval=20, blit=True)

# Show the plot
plt.show()
