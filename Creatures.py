### COMPSCI 130, Summer School 2019
### Project Two - Creatures
import turtle
import hashlib
from collections import Counter

## This class represents a creature
class Creature:

    ## A creature stores its position and direction and its "DNA" - the list of instructions it follows
    def __init__(self, row, col, dna, direction, name):
        self.direction = direction
        self.row = row
        self.col = col
        self.dna = dna
        self.name = name
        self.next_instruction = 1
        self.ahead = None

    ## Returns a string representation of the creature
    def __str__(self):
        return str(self.get_species() + ' ' + str(self.row) + ' ' +
                   str(self.col) + ' ' + str(self.direction))

    ## A creature draws itself using the colour specified as part of its dna
    ## the size of the grid squares, and the position of the top-left pixel are provided as input
    def draw(self, grid_size, top_left_x, top_left_y):

        ## Compute the position of the top left hand corner of the cell this creature is in
        x = top_left_x + (self.col - 1) * grid_size
        y = top_left_y - (self.row - 1) * grid_size

        ## Draw the creature

        # Overwrite everything in the cell
        turtle.goto(x, y)
        turtle.pendown()
        turtle.begin_fill()
        turtle.color("white")
        turtle.goto(x + grid_size, y)
        turtle.goto(x + grid_size, y - grid_size)
        turtle.goto(x, y - grid_size)
        turtle.goto(x, y)  # This one is redundant
        turtle.end_fill()
        turtle.penup()

        turtle.color(self.dna[0].split(":")[1])

        # Draw a triangle in the direction this creature is facing
        if self.direction == 'North':
            turtle.goto(x + (grid_size / 2), y)
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x, y - grid_size)
            turtle.goto(x + grid_size, y - grid_size)

        elif self.direction == 'East':
            turtle.goto(x + grid_size, y - (grid_size / 2))
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x, y)
            turtle.goto(x, y - grid_size)

        elif self.direction == 'South':
            turtle.goto(x + (grid_size / 2), y - grid_size)
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x, y)
            turtle.goto(x + grid_size, y)

        else:  # West
            turtle.goto(x, y - (grid_size / 2))
            turtle.pendown()
            turtle.begin_fill()
            turtle.goto(x + grid_size, y)
            turtle.goto(x + grid_size, y - grid_size)

        turtle.end_fill()
        turtle.penup()

        turtle.color("black")

    ## Returns the name of the species for this creature
    def get_species(self):
        return self.dna[0].split(":")[0]

    ## Gets the current position of the creature 
    def get_position(self):
        return self.row, self.col

    def get_ahead_pos(self):
        ahead_row = self.row
        ahead_col = self.col
        if self.direction == 'North':
            ahead_row = ahead_row - 1
        elif self.direction == 'South':
            ahead_row = ahead_row + 1
        elif self.direction == 'East':
            ahead_col = ahead_col + 1
        elif self.direction == 'West':
            ahead_col = ahead_col - 1
        return ahead_row, ahead_col

    def op_go(self, op):
        self.next_instruction = int(op[1])

    def op_hop(self, row, col):
        if self.ahead == 'EMPTY':
            self.row = row
            self.col = col

    def op_reverse(self):
        if self.direction == 'North':
            self.direction = 'South'
        elif self.direction == 'South':
            self.direction = 'North'
        elif self.direction == 'East':
            self.direction = 'West'
        elif self.direction == 'West':
            self.direction = 'East'

    def op_ifnotwall(self, op):
        if self.ahead == 'EMPTY':
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_twist(self):
        if self.direction == 'North':
            self.direction = 'East'
        elif self.direction == 'East':
            self.direction = 'South'
        elif self.direction == 'South':
            self.direction = 'West'
        elif self.direction == 'West':
            self.direction = 'North'

    def op_ifsame(self, op):
        if isinstance(self, type(self.ahead)) and self.name == self.ahead.name:
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_ifenemy(self, op):
        if isinstance(self, type(self.ahead)) and self.name != self.ahead.name:
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_ifrandom(self, op, world):
        if world.pseudo_random():
            self.next_instruction = int(op[1])
        else:
            self.next_instruction += 1

    def op_infect(self):
        self.ahead.name = self.name
        self.ahead.dna = self.dna

    ## Execute a single move (either hop, left or right) for this creature by following the instructions in its dna
    def make_move(self, world):
        finished = False
        ahead_row, ahead_col = self.get_ahead_pos()
        self.ahead = world.get_cell(ahead_row, ahead_col)

        dispatch = {
            'go': self.op_go,
            'hop': self.op_hop,
            'reverse': self.op_reverse,
            'ifnotwall': self.op_ifnotwall,
            'twist': self.op_twist,
            'ifsame': self.op_ifsame,
            'ifenemy': self.op_ifenemy,
            'ifrandom': self.op_ifrandom,
            'infect': self.op_infect
        }

        # Operations that do not end a creature's turn
        control_ops = set(['go', 'ifnotwall', 'ifsame', 'ifenemy', 'ifrandom'])

        # Execute instructions until a non-control-flow op is run
        while not finished:
            next_op = self.dna[self.next_instruction]
            op = next_op.split()

            op_args = {
                'go': {'op': op},
                'hop': {'row': ahead_row, 'col': ahead_col},
                'ifnotwall': {'op': op},
                'ifsame': {'op': op},
                'ifenemy': {'op': op},
                'ifrandom': {'op': op, 'world': world},
            }

            try:
                dispatch[op[0]](**op_args.get(op[0], {}))
            except KeyError:
                raise ValueError(f"can't find instruction '{next_op}'.")

            if op[0] in control_ops:
                continue

            self.next_instruction += 1
            finished = True


## This class represents the grid-based world
class World:

    ## The world stores its grid-size, and the number of generations to be executed.  It also stores a creature. 4
    def __init__(self, size, max_generations):
        self.size = size
        self.generation = 0
        self.max_generations = max_generations
        self.creatures = []

    ## Adds a creature to the world
    def add_creature(self, c):
        self.creatures.append(c)

    ## Gets the contents of the specified cell.  This could be 'WALL' if the cell is off the grid
    ## or 'EMPTY' if the cell is unoccupied
    def get_cell(self, row, col):
        if row <= 0 or col <= 0 or row >= self.size + 1 or col >= self.size + 1:
            return 'WALL'

        # Check if there are any creatures in this world at the given position
        for creature in self.creatures:
            if creature.row == row and creature.col == col:
                return creature

        return 'EMPTY'

    ## Executes one generation for the world - the creature moves once.  If there are no more
    ## generations to simulate, the world is printed
    def simulate(self):
        if self.generation < self.max_generations:
            self.generation += 1
            for creature in self.creatures:
                creature.make_move(self)
            return False
        else:
            print(self)
            return True

    def __str__(self):
        """Returns a string representation of the world."""

        # Count the frequency of each creature
        counts = Counter([c.name for c in self.creatures]).most_common()

        # Sort in descending order by frequency, and then alphabetically
        counts.sort(key=lambda x: (-x[1], x[0]))

        # Convert each creature to it's string representation
        creatures = [c.__str__() for c in self.creatures]

        return f'{self.size}\n' + f'{counts}\n' + '\n'.join(creatures)

    ## Display the world by drawing the creature, and placing a grid around it
    def draw(self):

        # Basic coordinates of grid within 800x800 window - total width and position of top left corner
        grid_width = 700
        top_left_x = -350
        top_left_y = 350
        grid_size = grid_width / self.size

        # Draw the creature
        for creature in self.creatures:
            creature.draw(grid_size, top_left_x, top_left_y)

        # Draw the bounding box
        turtle.goto(top_left_x, top_left_y)
        turtle.setheading(0)
        turtle.pendown()
        for i in range(0, 4):
            turtle.rt(90)
            turtle.forward(grid_width)
        turtle.penup()

        # Draw rows
        for i in range(self.size):
            turtle.setheading(90)
            turtle.goto(top_left_x, top_left_y - grid_size * i)
            turtle.pendown()
            turtle.forward(grid_width)
            turtle.penup()

        # Draw columns
        for i in range(self.size):
            turtle.setheading(180)
            turtle.goto(top_left_x + grid_size * i, top_left_y)
            turtle.pendown()
            turtle.forward(grid_width)
            turtle.penup()

    def pseudo_random(self):
        total = sum(c.row + c.col for c in self.creatures) * self.generation
        return int(hashlib.sha256(str(total).encode()).hexdigest(), 16) % 2


## This class reads the data files from disk and sets up the window
class CreatureWorld:

    ## Initialises the window, and registers the begin_simulation function to be called when the space-bar is pressed
    def __init__(self):
        self.framework = SimulationFramework(800, 800,
                                             'COMPSCI 130 Project Two')
        self.framework.add_key_action(self.begin_simulation, ' ')
        self.framework.add_tick_action(
            self.next_turn,
            100)  # Delay between animation "ticks" - smaller is faster.

    ## Starts the animation
    def begin_simulation(self):
        self.framework.start_simulation()

    ## Ends the animation
    def end_simulation(self):
        self.framework.stop_simulation()

    ## Reads the data files from disk
    def setup_simulation(self):

        ## If new creatures are defined, they should be added to this list: #6
        all_creatures = ['Hopper', 'Parry', 'Rook', 'Roomber', 'Randy', 'Flytrap']

        # Read the creature location data
        with open('world_input.txt') as f:
            world_data = f.read().splitlines()

        # Read the dna data for each creature type
        dna_dict = {}
        for creature in all_creatures:
            with open('Creatures//' + creature + '.txt') as f:
                dna_dict[creature] = f.read().splitlines()

        # Create a world of the specified size, and set the number of generations to be performed when the simulation runs
        world_size = world_data[0]
        world_generations = world_data[1]
        self.world = World(int(world_size), int(world_generations))

        for creature in world_data[2:]:
            data = creature.split()
            name = data[0]
            dna = dna_dict[name]
            row = int(data[1])
            col = int(data[2])
            direction = data[3]

            if self.world.get_cell(row, col) == 'EMPTY':
                self.world.add_creature(Creature(row, col, dna, direction, name))

        # Draw the initial layout of the world
        self.world.draw()

    ## This function is called each time the animation loop "ticks".  The screen should be redrawn each time.
    def next_turn(self):
        turtle.clear()
        self.world.draw()
        if self.world.simulate():
            self.end_simulation()

    ## This function sets up the simulation and starts the animation loop
    def start(self):
        self.setup_simulation()
        turtle.mainloop()  # Must appear last.


## This is the simulation framework - it does not need to be edited
class SimulationFramework:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.simulation_running = False
        self.tick = None  #function to call for each animation cycle
        self.delay = 100  #default is .1 second.
        turtle.title(title)  #title for the window
        turtle.setup(width, height)  #set window display
        turtle.hideturtle()  #prevent turtle appearance
        turtle.tracer(False)  #prevent turtle animation
        turtle.listen()  #set window focus to the turtle window
        turtle.mode('logo')  #set 0 direction as straight up
        turtle.penup()  #don't draw anything
        self.__animation_loop()

    def start_simulation(self):
        self.simulation_running = True

    def stop_simulation(self):
        self.simulation_running = False

    def add_key_action(self, func, key):
        turtle.onkeypress(func, key)

    def add_tick_action(self, func, delay):
        self.tick = func
        self.delay = delay

    def __animation_loop(self):
        if self.simulation_running:
            self.tick()
        turtle.ontimer(self.__animation_loop, self.delay)


cw = CreatureWorld()
cw.start()
