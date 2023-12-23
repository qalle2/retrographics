# convert an image into a retro-style PNG

import argparse, collections, itertools, os, sys, time
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://python-pillow.org")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Convert an image into a retro-style PNG."
    )

    # TODO: one cell color must be first entry of master palette
    parser.add_argument("--cellwidth", type=int, default=8)
    parser.add_argument("--cellheight", type=int, default=8)
    parser.add_argument("--cellcolors", type=int, default=2)
    parser.add_argument(
        "--masterpal", choices=("rgb3", "rgb6", "cga"), default="rgb3"
    )
    parser.add_argument("inputfile")
    parser.add_argument("outputfile")

    args = parser.parse_args()

    if not 8 <= args.cellwidth <= 64:
        sys.exit("Cell width argument is not valid.")
    if not 1 <= args.cellheight <= 64:
        sys.exit("Cell height argument is not valid.")
    if not 0 <= args.cellcolors <= 16:
        sys.exit("Cell colors argument is not valid.")

    if not os.path.isfile(args.inputfile):
        sys.exit("Input file not found.")
    if os.path.exists(args.outputfile):
        sys.exit("Output file already exists.")

    return args

def create_master_palette(masterPal):
    if masterPal == "rgb3":
        return tuple(
            tuple(((i >> s) & 1) * 255 for s in (2, 1, 0))
            for i in range(8)
        )
    if masterPal == "rgb6":
        return tuple(
            tuple(((i >> s) & 3) * 255 for s in (4, 2, 0))
            for i in range(64)
        )
    if masterPal == "cga":
        # IRGB except 6th color is (170,85,0) instead of (170,170,0)
        return tuple(
            (
                (i >> 3) * 85 + ((i >> 2) & 1) * 170,
                (i >> 3) * 85 + ((i >> 1) & 1) * (85 if i == 6 else 170),
                (i >> 3) * 85 + ( i       & 1) * 170,
            )
            for i in range(16)
        )
    sys.exit("Unexpected error.")

def get_color_diff(rgb1, rgb2):
    # get the difference of two (R, G, B) colors
    return (
        2 * abs(rgb1[0] - rgb2[0])
        + 3 * abs(rgb1[1] - rgb2[1])
        + abs(rgb1[2] - rgb2[2])
    )

def find_nearest_color(color, palette):
    # find nearest color in palette for one color
    # color: (R, G, B)
    # palette: tuple of (R, G, B) tuples
    # return: color as (R, G, B)

    smallestDiff = 10**6
    for palColor in palette:
        diff = get_color_diff(palColor, color)
        if diff < smallestDiff:
            smallestDiff = diff
            bestColor = palColor
    return bestColor

def find_best_cell_colors(cell, colorCnt, palette):
    # find best colors from master palette for a cell
    # cell: pixels as (R, G, B)
    # colorCnt: max number of colors
    # palette: master palette as (R, G, B) tuples
    # return: tuple of colorCnt (R, G, B) tuples

    colorCounts = collections.Counter(cell)

    # speed optimization
    cellColors = set(find_nearest_color(c, palette) for c in colorCounts)
    if len(cellColors) <= colorCnt:
        return tuple(sorted(cellColors))

    smallestDiff = 10**9
    bestColors = ()
    for palColors in itertools.combinations(palette, r=colorCnt):
        diff = sum(
            min(get_color_diff(oc, pc) for pc in palColors) * colorCounts[oc]
            for oc in colorCounts
        )
        if diff < smallestDiff:
            smallestDiff = diff
            bestColors = palColors
    return bestColors

def worsen_cell(cell, masterPal, args):
    # cell: tuple of (R, G, B) tuples
    # masterPal: tuple of (R, G, B) tuples
    # return: cell with worse quality

    if args.cellcolors == 0:
        cellColors = masterPal  # unlimited
    else:
        cellColors = find_best_cell_colors(cell, args.cellcolors, masterPal)

    cell = list(cell)
    for i in range(len(cell)):
        cell[i] = find_nearest_color(cell[i], cellColors)
    return tuple(cell)

def convert_image(srcImg, args):
    # validate source image and convert into RGB
    if srcImg.width == 0 or srcImg.width % args.cellwidth:
        sys.exit("Image width is not a multiple of cell width.")
    if srcImg.height == 0 or srcImg.height % args.cellheight:
        sys.exit("Image height is not a multiple of cell height.")
    if srcImg.mode in ("L", "P"):
        srcImg = srcImg.convert("RGB")
    elif srcImg.mode != "RGB":
        sys.exit("Unrecognized pixel format (try removing the alpha channel).")

    # create destination and temporary image
    dstImg = Image.new("RGB", (srcImg.width, srcImg.height))
    cellImage = Image.new("RGB", (args.cellwidth, args.cellheight))

    masterPal = create_master_palette(args.masterpal)

    # copy data from source to destination image
    for y in range(0, srcImg.height, args.cellheight):
        for x in range(0, srcImg.width, args.cellwidth):
            cell = tuple(
                srcImg.crop((x, y, x + args.cellwidth, y + args.cellheight))
                .getdata()
            )
            cell = worsen_cell(cell, masterPal, args)
            cellImage.putdata(cell)
            dstImg.paste(cellImage, (x, y))

    return dstImg

def main():
    startTime = time.time()
    args = parse_arguments()

    try:
        with open(args.inputfile, "rb") as source, \
        open(args.outputfile, "wb") as target:
            # open source image
            source.seek(0)
            srcImg = Image.open(source)
            # create destination image
            dstImg = convert_image(srcImg, args)
            # save destination image
            target.seek(0)
            dstImg.save(target, "png")

    except OSError:
        sys.exit("Error reading/writing files.")

    print("Wrote {} in {:.1f} s".format(
        os.path.basename(args.outputfile), time.time() - startTime
    ))

main()
