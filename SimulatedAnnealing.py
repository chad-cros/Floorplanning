DEBUG = 0
'''
    0 to turn off debug
    1   debug Edge
    2   debug Vertex
    4   debug Point
    8   debug Block
    16  debug load_netlist
    32  debug load_pio
    64  debug create_blocks
    128 debug main
'''

# ---- Objects ----


class Edge(object):
    """ Edge object. Essentially another name for a net. Connects two & only two vertices together. This class is only
            used to parse files (load_matrix()), and link Vertex objects to each other.

    """
    def __init__(self, left, right):
        self.left_id = left
        self.right_id = right

    @property
    def left(self):
        return self.left_id

    @left.setter
    def left(self, new_left):
        self.left_id = new_left

    @property
    def right(self):
        return self.right_id

    @right.setter
    def right(self, new_right):
        self.right_id = new_right


class Vertex(object):
    def __init__(self, input_id):
        if DEBUG & 2 == 2:
            print("Creating node {0}\n".format(input_id))
        # integer id value
        self.id_val = input_id
        # Array of other vertices this vertex is connected to
        self.connections = []

    @property
    def id(self):
        return self.id_val

    @property
    def edges(self):
        return self.connections

    def add_vertex(self, new_connection):
        """ Function append a vertex to the list of vertices the vertex is connected to

        Args:
            new_connection (Vertex): a vertex object

        Returns:
            None.
        """

        if new_connection not in self.connections:
            self.connections.append(new_connection)

    def dump_connections(self):
        """Function to dump the id values of the connections to the given vertex

        Returns:
            None.
        """
        for x in self.connections:
            print(x.id, end=',')


class Point(object):
    def __init__(self, x, y):
        """ Creates a point from given x and y coordinates

        Args:
            x (int): An x coordinate
            y (int): A y coordinate

        """
        if type(x) is not int:
            raise ValueError("Coordinate must be an integer")
        if type(y) is not int:
            raise ValueError("Coordinate must be an integer")

        self.x_coordinate = x
        self.y_coordinate = y

    @property
    def x(self):
        return self.x_coordinate

    @x.setter
    def x(self, new_x):
        if type(new_x) is not int:
            raise ValueError("Coordinate must be an integer")

        self.x_coordinate = new_x

    @property
    def y(self):
        return self.y_coordinate

    @y.setter
    def y(self, new_y):
        if type(new_y) is not int:
            raise ValueError("Coordinate must be an integer")

        self.y_coordinate = new_y

    def point(self):
        return self.x, self.y


class Block(object):
    def __init__(self, vertex, is_input_output=False):
        # List of points occupied by this block
        self.coordinates = []
        # A node object this block is linked with. The node object keeps track of net connections
        self.node = vertex
        # A boolean to signify if this block is an I/O block
        self.io = is_input_output
        # A boolean to signify if this block has been rotated or not
        self.orientation = False

    def add_coordinate(self, in_point):
        self.coordinates.append(in_point)

    def sort_coordinates_x(self, low_to_high):
        """

        Args:
            low_to_high (bool): Sorts list low to high if true.

        Returns:
            None.
        """
        self.coordinates.sort(key=lambda point: point.x, reverse=low_to_high)

    def sort_coordinates_y(self, low_to_high):
        """

        Args:
            low_to_high (bool): Sorts list low to high if true.

        Returns:
            None.
        """
        self.coordinates.sort(key=lambda point: point.y, reverse=low_to_high)

    @property
    def pio(self):
        return self.io

    @pio.setter
    def pio(self, state):
        self.io = state

    @property
    def id(self):
        return self.node.id

    @property
    def width(self):
        """ Function to get the width of the object

        Returns:
            int: An integer of the width of the block
        """
        smallest = self.coordinates[0].x
        largest = self.coordinates[0].x

        for point in self.coordinates:
            if point.x < smallest:
                smallest = point.x
            if point.x > largest:
                largest = point.x

        return largest - smallest

    @property
    def height(self):
        """ Function to return the height of an object

        Returns:
            int: An integer value of the height of an object
        """
        smallest = self.coordinates[0].y
        largest = self.coordinates[0].y

        for point in self.coordinates:
            if point.y < smallest:
                smallest = point.y
            if point.y > largest:
                largest = point.y

        return largest - smallest

    @property
    def area(self):
        """ Function to return the area of an object

        Returns:
            int: An integer value of the area of the object
        """
        return self.width * self.height

    @property
    def origin(self):
        """Function to return the lowest, leftmost point the object takes up.

        Returns:
            Point: A point object giving the coordinates the object starts at
        """
        lowest_left = self.coordinates[0]

        for point in self.coordinates:
            if point.x < lowest_left.x and point.y < lowest_left.y:
                lowest_left = point

        return lowest_left

    def rotate(self):
        """ Function to rotate the object 90 degrees, but maintain the same origin point.

        Returns:
            None
        """
        # Get dimensions of the module before erasing data
        width = self.width
        height = self.height
        origin = self.origin

        # Clear coordinate list
        self.coordinates.clear()

        if self.orientation:
            # If the object is not in its default position, rotate it 90 degrees to return it to normal.
            self.orientation = False

            for x_coord in range(origin.x, origin.x + width + 1):
                for y_coord in range(origin.y, origin.y + height + 1):
                    self.add_coordinate(Point(x_coord, y_coord))
        else:
            # Else, rotate the object 90 degrees to
            self.orientation = True

            for x_coord in range(origin.x, origin.x + height + 1):
                for y_coord in range(origin.y, origin.y + width + 1):
                    self.add_coordinate(Point(x_coord, y_coord))

    def move(self, x_dir=0, y_dir=0):
        """ Function to move a module in a certain direction

        Args:
            x_dir (int): amount to move module, negative to move left, positive to move right
            y_dir (int): amount to move module, negative to move down, positive to move up

        Returns:
            None
        """

        for it in range(len(self.coordinates)):
            point = self.coordinates.pop(it)
            self.coordinates.append(Point(point.x + x_dir, point.y + y_dir))

    def move_to_point(self, point):
        x_dir = point.x - self.origin.x
        y_dir = point.y - self.origin.y
        self.move(x_dir, y_dir)

    def _dump_coords(self):
        for point in self.coordinates:
            print('{0},{1}'.format(point.x, point.y))

# -------------------
# ---- Functions ----


def load_netlist(filename):
    """ Function to load in a txt file, and create arrays for the algorithm to process

    Args:
        filename (str): A file to read from

    Returns:
        Array: An array of vertex types, all of which are linked to each other according to the given netlist
    """

    with open(filename) as f:
        # Local array. Used to check uniqueness of vertex objects.
        vertex_ids = []
        # Local array. Used to create a 1 to 1 list of a netlist.
        current_edges = []
        # Total output. Edges are the actual connections, and vertices are the nodes.
        edges = []
        vertices = []

        # Row by row, read off nets from file
        for row in f:
            '''
                Here what we want to do is two things. Create a list of connections, and create a list of nodes (vertex)
                Directly below is the handling of nodes. We'll split apart the netlist, and create unique vertex types
                    and push them to the array labeled "vertices"
                In the loop immediately after, we'll deal with printing out connections from the given net.
            '''
            counter = 0
            for x in row.split(' '):
                # Iterate through each number in the line, separated by a space
                if counter == 0:
                    # If this is the first element in the list (the net number) skip it.
                    counter += 1
                    continue

                # Write the current connections we're dealing with to an array, so we can link them after creating the
                #       vertices.
                current_edges.append(int(x))
                # Check if this node has already been created here. If not, create it. We'll deal with linking the node
                #   to other nodes later.
                if int(x) not in vertex_ids:
                    vertex_ids.append(int(x))
                    vertices.append(Vertex(int(x)))

            # Iterate through the net and connect all nodes together with the Edge() function
            for y in current_edges:
                for connection in range(current_edges.index(y) + 1, len(current_edges)):
                    # Add new connection to the edges array
                    edges.append(Edge(y, current_edges[connection]))

            current_edges.clear()

    # Local pointer variable used in the following for loop
    vertex_pointer = None
    '''
        The following loop runs through the given vertices, and looks for connections in the edges array.
    '''
    for vertex in vertices:
        # Iterate through vertex, then iterate through edges to link the objects together
        for edge in edges:
            if vertex.id is edge.left:
                # Add connection with the right value of the edge

                # Iterate through the list of vertices and find the vertex that matches the id of the right value
                for inner_vertex in vertices:
                    if edge.right is inner_vertex.id:
                        vertex_pointer = inner_vertex

                # Link the found edge to the current vertex, and reset the pointer
                vertex.add_vertex(vertex_pointer)
                vertex_pointer = None

            elif vertex.id is edge.right:
                # Add connection with the left value of the edge

                # Iterate through the list of vertices and find the vertex that matches the id of the left value
                for inner_vertex in vertices:
                    if edge.left is inner_vertex.id:
                        vertex_pointer = inner_vertex

                # Link the found edge to the current vertex, and reset the pointer
                vertex.add_vertex(vertex_pointer)
                vertex_pointer = None

    return vertices


def load_pio(filename):
    """ Function to load in a txt file, and create arrays for the algorithm to process

    Args:
        filename (str): A file to read from

    Returns:
        Array: An array of int types, a list of ids which are i/o nodes
    """
    pio_list = []

    # Run through given file and pull values to a list
    with open(filename) as f:
        for id_val in f:
            pio_list.append(int(id_val))

    return pio_list


def create_blocks(vertices, pio_list, filename):
    """Function that creates a list of Block objects. Each object has a property for ID, Connections and Area

    Args:
        vertices (list): a list of Vertex types used to link blocks together
        pio_list (list): a list of node's that are primary i/o's
        filename (str): the name of the file to read for the block's area

    Returns:
        list: A list of Block objects
    """

    # List of block objects to be returned
    block_list = []

    with open(filename) as f:
        for row in f:
            # Load in the block from the module.txt file, and assign it to its vertex object
            vert_id, start_x, start_y, width, height = row.split(' ')

            # Convert elements to integer types
            vert_id = int(vert_id)
            start_x = int(start_x)
            start_y = int(start_y)
            width = int(width)
            height = int(height)

            if DEBUG & 64 == 64:
                print('Read\t{0}\t{1}\t{2}\t{3}\t{4}'.format(vert_id, start_x, start_y, width, height))

            # Create a block object with the connections formed from the netlist.
            temp_node = next((node for node in vertices if node.id == int(vert_id)), None)

            # In the case where the node isn't connected to other nodes, it'll create the object for one here.
            if temp_node is None:
                if DEBUG & 64 == 64:
                    print('No such node exists, creating one.')
                temp_node = Vertex(vert_id)

            temp_block = Block(
                                temp_node,
                                True if vert_id in pio_list else False
                              )

            # Create the list of points that the module takes up (essentially listing all points in the rectangle
            #   occupied by the module)
            for x_coord in range(start_x, start_x + width + 1):
                for y_coord in range(start_y, start_y + height + 1):
                    if DEBUG & 64 == 64 and DEBUG & 4 == 4:
                        print('Creating point: {0}, {1}'.format(x_coord, y_coord))
                    temp_block.add_coordinate(Point(x_coord, y_coord))

            # Once the block has been created, add it to the list so it can be returned to the main function
            block_list.append(temp_block)

            # Set the pointer to null
            temp_block = None
            temp_node = None

    return block_list

# --------------
# ---- Main ----


def main():
    netlist = 'venv/net.txt'

    pio = 'venv/pio.txt'

    module = 'venv/module.txt'

    vertices = load_netlist(netlist)

    io_list = load_pio(pio)

    block_list = create_blocks(vertices, io_list, module)


if __name__ == "__main__":
    main()
