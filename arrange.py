from model import Picture, Gallery, Wall, Placement
import math
import random

DEFAULT_MARGIN = 2


class Workspace(object):
    """Class on which arrangments can be performed."""

    def __init__(self, gallery_id, options):
        """Constructor from picture list."""

        pictures = Gallery.query.get(gallery_id).pictures

        self.gallery_id = gallery_id
        self.margin = options.get('margin', DEFAULT_MARGIN)

        self.pics = {}
        self.xsys = []

        for picture in pictures:
            pic = picture.picture_id
            self.pics[pic] = {}
            # Note, each side of each picture carries half the margin
            #
            #        w+m
            #     <------->
            #          w   m
            #       <----><->
            #     +--------+---------+
            #     | +----+ | +-----+ |
            #     | |    | | |     | |
            #     | +----+ | +-----+ |
            #     +--------+---------+
            #
            # Rounding here serves to avoid unnesesary treatment of fractional
            # gaps, and should simplify logic some.
            self.pics[pic]['width_mar'] = int(math.ceil(picture.width)) + self.margin
            self.pics[pic]['height_mar'] = int(math.ceil(picture.height)) + self.margin

    def get_area_queue(self):
        """Returns a list of margin padded picture areas, as tuples with id."""

        return [(self.pics[p]['width_mar'] * self.pics[p]['height_mar'], p)
                for p in self.pics]

    def arrange_grid(self):
        """Arrangment via an initial placement in a grid."""

        pics_in_grid = self.random_place_in_grid()

        self.expand_grid_to_arrangment(pics_in_grid)

    def expand_grid_to_arrangment(self, pics_in_grid):
        """From a set of grid indicies produce geometrically valid placements.

        (grid = relative psuedo locations without geometry)"""
        # print '*'*80
        grid_ordered = sorted(pics_in_grid.keys())
        cols, rows = zip(*grid_ordered)
        max_i = max(cols)

        # for column # start in the middle
            # for i in range(0)
            # for row # start in the middle

            #  if at the center just place it (consider detect even number)

            # if grid neighbor above/below place at that vertical level

            # if can move towards center do that

    def arrange_column_heuristic(self):
        """Arrange in columns by a few rules."""

        # column = {'type': None,
        #             'width': 0,
        #             'height': 0,
        #             'pics': {}
        # }

        pics_remaining = set(self.pics.keys())

        # Create a column with the single tallest picture
        tallest = sorted([(self.pics[p]['height_mar'], p) for p in pics_remaining])[-1][1]
        # print(Picture.query.get(tallest))
        columns.append[ {'type': 'tall',
                  'width': self.pics[tallest]['width_mar'],
                  'height': self.pics[tallest]['height_mar'],
                  'pics': {tallest: [0, 0]}
                  }]
        pics_remaining.remove(tallest)
       
        # Create a column with wide pic and two skinny ones
        sorted_by_width = sorted([(self.pics[p]['width_mar'], p) for p in pics_remaining])

        widest = sorted_by_width[-1][1]
        # Consider getting these not as the skinniest but in general low end of dist
        skinny1 = sorted_by_width[0][1]
        skinny2 = sorted_by_width[1][1]

        pair_width = (self.pics[skinny1]['width_mar'] +
                      self.pics[skinny2]['width_mar'])
        single_width = self.pics[widest]['width_mar']

        # if pair_width => single_width:
        #     # pair is wider

        # else:
        #     pass

        # print(Picture.query.get(tallest))
        # columns.append[ {'type': 'nested',
        #           'width': self.pics[widest]['width_mar'],
        #           'height': self.pics[tallest]['height_mar'],
        #           'pics': {tallest: [0, 0]}
        #           }]


    def random_place_in_grid(self):
        """Place pics in random grid indicies.

        Returns a dict of tuple keys of grid indicies with pic id values
        {(i,j): pic}
        """

        n_pics = len(self.pics)
        n_grid = int(math.ceil(math.sqrt(n_pics)))
        min_grid = -n_grid/2
        max_grid = min_grid + n_grid

        grid_pairs = [(i, j) for i in range(min_grid, max_grid) 
                             for j in range(min_grid, max_grid)]

        grid_sample = random.sample(grid_pairs, n_pics)

        grid_pics = {grid_sample[i]:pic for i, pic in enumerate(self.pics.keys())}

        return grid_pics

    def arrange_linear(self):
        """Arrange gallery pictures in horizontal line, vertically centered."""

        # Use areas as a rough approximation for size to create alternating
        # small large pattern
        areas_with_id = sorted(self.get_area_queue())

        areas, pics = zip(*areas_with_id)
        pics = list(pics)

        mid_index = len(pics) / 2
        smaller_pics = pics[:mid_index]
        larger_pics = pics[mid_index:]
        random.shuffle(smaller_pics)
        random.shuffle(larger_pics)

        row_width = 0

        for i in range(len(pics)):
            pic = smaller_pics.pop() if (i % 2 == 0) else larger_pics.pop()
            x1 = row_width
            x2 = row_width+self.pics[pic]['width_mar']
            y1 = -self.pics[pic]['height_mar']/2
            y2 = self.pics[pic]['height_mar']-self.pics[pic]['height_mar']/2

            self.xsys.append([x1, x2, y1, y2, pic])
            row_width = x2


    def realign_to_origin(self):
        """Shift all placements to positive quadrant with origin upper left."""

        x1s, x2s, y1s, y2s, pics = zip(*self.xsys)

        x_shift = -min(x1s)
        y_shift = -min(y1s)

        self.xsys = [[x1s[i] + x_shift,
                      x2s[i] + x_shift,
                      y1s[i] + y_shift,
                      y2s[i] + y_shift,
                      pics[i]] for i in range(len(pics))]

        # for i in range(len(pics)):
        #     self.xsys[i][0] += x_shift
        #     self.xsys[i][1] += x_shift
        #     self.xsys[i][2] += y_shift
        #     self.xsys[i][3] += y_shift

    def get_wall_size(self):
        """Assgins as attributes the total wall height and width."""

        x1s, x2s, y1s, y2s, pics = zip(*self.xsys)

        # If already adjusted to origin the second term of each expression is unnecesary
        self.width = max(x2s) - min(x1s)
        self.height = max(y2s) - min(y1s)

    def produce_placements(self):
        """Convert coordinates: remove rounding and margins used for placement."""

        self.placements = {}

        for xsys in self.xsys:
            pic = xsys[4]
            picture = Picture.query.get(pic)
            self.placements[pic] = {}
            width_fine = (math.ceil(picture.width) - picture.width) / 2
            height_fine = (math.ceil(picture.height) - picture.height) / 2
            self.placements[pic]['x'] = xsys[0] + self.margin/2 + width_fine
            self.placements[pic]['y'] = xsys[2] + self.margin/2 + height_fine


# Functions

def arrange_gallery_1(gallery_id, arrange_options):
    """Calls methods in order for arrangment steps - shakedown testing. """

    # Instantiates object for working on the arrangment
    wkspc = Workspace(gallery_id, arrange_options)

    # This call creates the arrangment itself, will eventually have various
    # functions availible passed in options
    wkspc.arrange_linear()
    # wkspc.arrange_grid()
    # wkspc.arrange_column_heuristic()

    # These calls readjust the workspace to the origin, calculate precise
    # placments for wall hanging, and save other information for display
    wkspc.realign_to_origin()
    wkspc.get_wall_size()
    wkspc.produce_placements()

    return [wkspc.placements, wkspc.width, wkspc.height]
