'''
Adapted from: https://colab.research.google.com/github/paulgb/notebooks/blob/master/source/l-systems/Fractal%20Generation%20with%20L-Systems.ipynb
'''
import matplotlib.pyplot as plt
from math import pi, sin, cos
DEGREES_TO_RADIANS = pi / 180
plt.style.use('bmh')  # Use some nicer default colors

def plot_coords(coords, bare_plot=False):
		if bare_plot:
				# Turns off the axis markers.
				plt.axis('off')
		# Ensures equal aspect ratio.
		plt.axes().set_aspect('equal', 'datalim')
		# Converts a list of coordinates into 
		# lists of X and Y values, respectively.
		X, Y = zip(*coords)
		# Draws the plot.
		plt.plot(X, Y);
		plt.show()

def turtle_to_coords(turtle_program, turn_amount=45):
		# The state variable tracks the current location and angle of the turtle.
		# The turtle starts at (0, 0) facing up (90 degrees).
		state = (0.0, 0.0, 90.0)
		
		# Throughout the turtle's journey, we "yield" its location. These coordinate
		# pairs become the path that plot_coords draws.
		yield (0.0, 0.0)
		
		# Loop over the program, one character at a time.
		for command in turtle_program:
				x, y, angle = state
				
				if command in 'Ff':      # Move turtle forward
						state = (x - cos(angle * DEGREES_TO_RADIANS),
										 y + sin(angle * DEGREES_TO_RADIANS),
										 angle)
						
						if command == 'f':
								# Insert a break in the path so that
								# this line segment isn't drawn.
								yield (float('nan'), float('nan'))
								
						yield (state[0], state[1])
												
				elif command == '+':     # Turn turtle clockwise without moving
						state = (x, y, angle + turn_amount)
						
				elif command == '-':     # Turn turtle counter-clockwise without moving
						state = (x, y, angle - turn_amount)
						
				# Note: We silently ignore unknown commands

def transform_sequence(sequence, transformations):
		return ''.join(transformations.get(c, c) for c in sequence)

def transform_multiple(sequence, transformations, iterations):
		for _ in range(iterations):
				sequence = transform_sequence(sequence, transformations)
		return sequence

plot_coords(turtle_to_coords(transform_multiple('F', {'F': '+F+F--F+F'}, 5)))