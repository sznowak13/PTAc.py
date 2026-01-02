from dataclasses import dataclass
from typing import Union

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

size = (128, 128)

MAX_WIDTH = 1200
MAX_HEIGHT = 1200

ASCII_CHARS = ['@', '&', '9', 'O', 'o', 'c', ':', '.', ' ']  # Darkest to brightest
# ASCII_CHARS = ['@', '%', '#', '*', '+', '=', '-', ':', '.', ' ']  # Darkest to brightest
ASCII_CHARS_INVERTED = list(reversed(ASCII_CHARS))  # Darkest to brightest
CHAR_NUMBER = len(ASCII_CHARS)
LUM_BREAKPOINT = 255 / CHAR_NUMBER
SCALE_FACTOR = 4

@dataclass
class ASCIIConfig:
    char_set: list[str]
    font_color: str
    bg_color: str
    name: str


ASCII_CONFIGS = {
    'normal': ASCIIConfig(ASCII_CHARS, 'black', 'white', 'normal'),
    'inverse': ASCIIConfig(ASCII_CHARS_INVERTED, 'white', 'black', 'inverse'),
    'high_contrast': ASCIIConfig(ASCII_CHARS_INVERTED, 'black', 'white', 'high_contrast'),

}


def main():
    # Use a breakpoint in the code line below to debug your script.
    outfile = "output/output.thumbnail"
    try:
        with Image.open("images/phoenix.jpg") as im:
            width, height = im.size
            if width > MAX_WIDTH or height > MAX_HEIGHT:
                print("Resizing before transformations due to large image resolution.")
                im.thumbnail((MAX_HEIGHT, MAX_WIDTH))
                print(f"New size: {im.size}")
                width, height = im.size
            downsized = im.resize((width // SCALE_FACTOR, height // SCALE_FACTOR)).convert("L")
            ascii_metadata = []
            for y in range(downsized.height):
                indices = []
                for x in range(downsized.width):
                    char_index = int((downsized.getpixel((x, y)) // LUM_BREAKPOINT))
                    if char_index >= CHAR_NUMBER:
                        char_index = CHAR_NUMBER - 1
                    downsized.putpixel((x, y), int(char_index * LUM_BREAKPOINT))
                    indices.append(char_index)
                ascii_metadata.append(indices)
            upsized = downsized.resize((width, height), Resampling.NEAREST)
            # im.thumbnail(size)
            upsized.save(outfile, "JPEG")
            ascii_config = ASCII_CONFIGS['normal']
            save_ascii_txt(ascii_metadata, ascii_config)
            save_ascii_image(ascii_metadata, 'normal', height, width)
            save_ascii_image(ascii_metadata, 'high_contrast', height, width)
            save_ascii_image(ascii_metadata, 'inverse', height, width)
    except OSError as e:
        print("cannot create thumbnail for input")
        raise e


def save_ascii_txt(ascii_metadata: list[list[int]], ascii_config: ASCIIConfig):
    print("Started saving ascii text")
    with open("output/ascii.txt", "w") as f:
        for line in ascii_metadata:
            f.writelines(list(map(lambda i: ascii_config.char_set[i], line)))
            f.write("\n")
    print("ascii text saved")


def save_ascii_image(ascii_data: list[list[int]], ascii_config: Union[str, ASCIIConfig], height: int, width: int):
    print("Started saving ascii image")
    if isinstance(ascii_config, str):
        ascii_config = ASCII_CONFIGS[ascii_config]
    elif isinstance(ascii_config, ASCIIConfig):
        pass
    ascii_image = Image.new('RGB', (width, height), color=ascii_config.bg_color)
    draw = ImageDraw.Draw(ascii_image)
    for y in range(len(ascii_data)):
        for x in range(len(ascii_data[y])):
            draw.text((x * SCALE_FACTOR, y * SCALE_FACTOR), ascii_config.char_set[ascii_data[y][x]],
                      font=ImageFont.truetype(
                          'arial.ttf', SCALE_FACTOR, layout_engine='raqm'), fill=ascii_config.font_color)
    ascii_image.save(f"output/ascii_{ascii_config.name}.jpeg", "JPEG")
    print("ascii image saved")


if __name__ == '__main__':
    main()

## This comment is not important.
