#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

######### DEFAULT VALUES #########

defaults = {
    "size": ([21.0, 29.7], "the size of the marker in cm"),
    "resolution": (100, "the resolution (pixel per cm)"),

    "text_size": (6, "the maximal height of the text (cm)"),
    "text_offset_side": (1, "the minimal border at the sides for the text (cm)"),
    "text_offset_top": (1, "the offset from the top to the text (cm)"),

    "box_offset_side": (2, "the minimal border at the sides for the box (cm)"),
    "box_offset_top": (8, "the offset from the top to the box (cm)"),
    "box_space_between": (1, "the space between two circles (cm)"),
    "box_padding_vertical": (0.5, "the padding on top and bottom of the circles (inside the box) (cm)"),
    "box_padding_horizontal": (0.5, "the padding on the sides of the circles (inside the box) (cm)"),
    "box_height": (5, "the height of the box (cm)"),
    "box_circle_count": (4, "the amount of circles (least significant bits of the number)"),
    
    "marker_size": (15, "the size of the marker (cm)"),
    "marker_offset_top": (14, "the offset from the top to the marker (cm)"),

    "background_color": ([255, 255, 255, 255], "the backgroundcolor of the texture"),
    "text_color": ([0, 0, 0, 255], "the color of the text"),
    "box_color": ([0, 200, 50, 255], "the color of the box"),
    "circle_color": ([255, 0, 0, 255], "the color of the circles"),
}

def getC(config, key):
    """helper function to easier get the configuration parameter
    
    Arguments:
        config {dict} -- the configuration dictionary
        key {str} -- the parameter to look up in the confiugration dictionary
    
    Returns:
        [type] -- the parameter from the configuration dictionary if it exist, else it will return the default value
    """
    return config.get(key, defaults[key][0])

#########

def generater_marker_image(number_of_marker, size):
    """generates the black and white marker with the script of the ar_track_alvar package (make sure to install it first)
    
    Arguments:
        number_of_marker {int} -- the number of the marker which has to be generated
        size {int} -- the size of the square marker in pixel
    
    Returns:
        Image -- the generated marker
    """
    # use /tmp folder as temporary place to generate and load the marker
    temp_marker_path = '/tmp/MarkerData_' + str(number_of_marker) + '.png'

    # generate the marker with the ar_track_alvar package (-u = resolution per unit) (-s = size in units) -> therefore the marker will have the pixel resoltion of size
    os.system('cd /tmp; rosrun ar_track_alvar createMarker -u ' + str(size) + ' -s 1 ' + str(number_of_marker))
    marker = Image.open(temp_marker_path)

    # delete temporary file from /tep folder
    os.remove(temp_marker_path)

    return marker

def draw_centered_text_inside_rectangle(context, text, color, font_path, x, y, width, height):
    """generate a text inside a bounding box. It will be maximized such tat the text will use as much space it can.
    The text will be centered horizontaly and vertically.

    Arguments:
        context {ImageDraw} -- the PIL context to draw to
        text {str} -- the text to write
        color {()} -- the color of the text (r, g, b, a) (0-255)
        font_path {str} -- path to the ttf font file
        x {float} -- upper left corners x position (pixel)
        y {float} -- upper left corners y position (pixel)
        width {float} -- width of the bounding box (pixel)
        height {float} -- height of the bounding box (pixel)
    """

    # probe the text to find the correct text height so that the text fits the bounding box
    probe_height = 10000
    font = ImageFont.truetype(font_path, probe_height)
    (text_width, text_height), (_,_) = font.font.getsize(text)

    # calculate the correct text heights based on the probed aspect ratios (only works if the font scaling works linearly)
    new_height_based_on_width = float(width) / float(text_width) * probe_height
    new_height_based_on_height = float(height) / float(text_height) * probe_height

    # use the smaller text size so that the text is totaly within the bounding box
    new_height = int(round(min(new_height_based_on_width, new_height_based_on_height)))
    
    # create the font with the correct size
    font = ImageFont.truetype(font_path, new_height)
    (text_width, text_height), (offset_x, offset_y) = font.font.getsize(text)

    # calculate offsets
    x_pos = x + width / 2.0 - text_width / 2.0 - offset_x
    y_pos = y + height / 2.0 - text_height / 2.0 - offset_y

    # draw text
    context.text((x_pos, y_pos), text, font=font, fill=color)


def draw_bit_circles_inside_rectangle(context, number, color, x, y, width, height, bits, space_between):
    """Draws the bit pattern and it will adjust the circle radius to fit all the circles inside the bounding box and with the specified space_between them
    The circle pattern will be centered horizontaly and vertically.

    Arguments:
        context {ImageDraw} -- the PIL context to draw to
        number {int} -- the number from where the last few bits will be represented
        color {()} -- the color of the circles (r, g, b, a) (0-255)
        x {float} -- upper left corners x position (pixel)
        y {float} -- upper left corners y position (pixel)
        width {float} -- width of the bounding box (pixel)
        height {float} -- height of the bounding box (pixel)
        bits {int} -- number of least significant bits to display
        space_between {float} -- space between two circles (edge to edge) (pixel)
    """

    # calculate the radii based on the bounding box
    radius_based_on_width = (width - (bits-1) * space_between) / (2.0 * bits)
    radius_based_on_height = height / 2.0

    # use the smaller one to ensure that all of them are in the bounding box
    radius = min(radius_based_on_width, radius_based_on_height)

    # draw the circles
    for i in range(bits):
        # only draw circle if bit at this position is set
        if number & (1 << i):
            # calculate correct center point
            x_pos = x + width / 2.0  + ((bits-1) / 2.0 - i) * (2 * radius + space_between)
            y_pos = y + height / 2.0

            # generate the necessary top-left and bottom right coordinates (local offsets + position of center) 
            points = np.array(((-radius, -radius), (radius, radius)))
            points += np.array((x_pos, y_pos))
            
            # draw circle
            context.ellipse(list(points.flatten().astype(int)), fill=color)

def draw_bit_circles_centered_around(context, number, color, x, y, radius, bits, space_between):
    """Draws the bit pattern with a fixed circle radius. The circle pattern will be centered horizontaly and vertically around the point (x, y).
    
    Arguments:
        context {ImageDraw} -- the PIL context to draw to
        number {int} -- the number from where the last few bits will be represented
        color {()} -- the color of the circles (r, g, b, a) (0-255)
        x {float} -- x of center of pattern (pixel)
        y {float} -- y of center of pattern (pixel)
        radius {float} -- radius of the circles (pixel)
        bits {int} -- number of least significant bits to display
        space_between {float} -- space between two circles (edge to edge) (pixel)
    """

    # calculate the bounding box given the radius
    width = bits * 2 * radius + (bits-1) * space_between
    height = 2 * radius   
    
    # use draw_bit_circles_inside_rectangle to draw the circles
    draw_bit_circles_inside_rectangle(context, number, color, x-width/2.0, y-height/2.0, width, height, bits, space_between) 

def create_texture(number_of_marker, output_file_path, font_path, config = {}):
    """generates a texture like the landmarks of the ERC
    Arguments:
        number_of_marker {int} -- the number of the marker, which will be generated
        output_file_path {str} -- path of the output file
        font_path {str} -- path to the font which should be used
    
    Keyword Arguments:
        config {dict} -- dictionary with more custmization variables (more information in the script or by calling it with --help) (default: {{}})
    """

    # get the size and resolution
    size = np.array(getC(config, "size"))
    resolution = getC(config, "resolution")

    # calculate real size in pixel
    image_size = size * resolution
    page_width, page_height = image_size

    # create canvas with correct size
    img = Image.new('RGBA', tuple(image_size.astype(int)), tuple(getC(config, "background_color")))

    # get a drawing context
    d = ImageDraw.Draw(img)
    
    # get text parameters and convert to pixels
    text_size = getC(config, "text_size") * resolution
    text_offset_side = getC(config, "text_offset_side") * resolution
    text_offset_top = getC(config, "text_offset_top") * resolution

    # draw the decibal number
    draw_centered_text_inside_rectangle(
        d, 
        str(number_of_marker), 
        tuple(getC(config, "text_color")), 
        font_path, 
        text_offset_side, 
        text_offset_top, 
        page_width - 2 * text_offset_side, 
        text_size
    )

    # get box and bit parameters and convert to pixels
    box_offset_side = getC(config, "box_offset_side") * resolution
    box_offset_top = getC(config, "box_offset_top") * resolution
    box_space_between = getC(config, "box_space_between") * resolution
    box_padding_vertical = getC(config, "box_padding_vertical") * resolution
    box_padding_horizontal = getC(config, "box_padding_horizontal") * resolution
    box_height = getC(config, "box_height") * resolution
    box_circle_count = getC(config, "box_circle_count")

    # draw box around circle counter
    box = [
        box_offset_side, 
        box_offset_top, 
        page_width - box_offset_side, 
        box_offset_top + box_height
    ]
    d.rectangle(box, fill=tuple(getC(config, "box_color")))

    # draw binary circle counter
    draw_bit_circles_inside_rectangle(
        d, 
        number_of_marker, 
        tuple(getC(config, "circle_color")), 
        box_offset_side + box_padding_horizontal, 
        box_offset_top + box_padding_vertical, 
        page_width - 2 * (box_offset_side + box_padding_horizontal), 
        box_height - 2 * box_padding_vertical, 
        box_circle_count, 
        box_space_between
    )

    # get marker parameters and convert to pixels
    marker_size = getC(config, "marker_size") * resolution
    marker_offset_top = getC(config, "marker_offset_top") * resolution

    # generate marker and draw to canvas
    marker = generater_marker_image(number_of_marker, marker_size)
    img.paste(marker, (int((page_width - marker_size) / 2.0), int(marker_offset_top)))

    # save the texture
    img.save(output_file_path)

if __name__ == '__main__':
    
    from argparse import ArgumentParser

    # get path of package
    from rospkg import RosPack
    rospack = RosPack()
    rover_sim_dir = rospack.get_path('rover_sim')
    # get default font path
    font_path = os.path.join(rover_sim_dir, 'resources/marker/Roboto-Bold.ttf')

    # parse command line arguments
    parser = ArgumentParser(
        description="""
            generates a texture like the landmarks of the ERC
        """)
    parser.add_argument("number", type=int, help="the number of the marker to generate")
    parser.add_argument("-o", "--output", type=str, help="the output file and path to the texture which will be created in this process", default="terrain.png")
    parser.add_argument("-f", "--font", type=str, help="path to the font (ttf)", default=font_path)
    parser.add_argument("-c", "--config", type=str, help="path to a json config file with the following possible parameters (they will be overritten if given here explicitly)")

    # generate arguments for all the layout parameters
    for key, element in defaults.iteritems():
        value, arg_help = element
        # ensure that list (like colors) need more parameters (use the length of the default valuess)
        if type(value) is list:
            parser.add_argument("--" + key, help=arg_help, type=type(value[0]), nargs=len(value))
        else:
            parser.add_argument("--" + key, help=arg_help, type=type(value))

    args = parser.parse_args()

    # read the parameters from the config file 
    config = {}
    if args.config:
        import json
        with open(args.config) as fp:
            config = json.load(fp)

    # add and override config-file parameters with command-line parameters
    for key, value in args.__dict__.iteritems():
        if value:
            config[key] = value

    # generate texture
    create_texture(args.number, args.output, args.font, config)