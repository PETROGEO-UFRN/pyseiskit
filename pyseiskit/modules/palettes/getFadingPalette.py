def getFadingPalette(base_palette):
    """
    Takes a palette (list of hex strings) and applies an alpha gradient.
    The first color becomes 100% opaque, fading to 100% transparent at the last color.
    """
    palette_length = len(base_palette)
    fading_palette = []
    
    for index, color in enumerate(base_palette):
        # *** index=0 -> alpha=255 (opaque)
        # *** index=(length-1) -> alpha=0 (transparent)
        alpha = int(255 * (1 - (index / (palette_length - 1))))
        # *** Grab just the #RRGGBB part
        #   *** in case the original palette already had alpha
        base_hex = color[:7]
        # *** Append the calculated alpha as a 2-character hex string
        fading_palette.append(f"{base_hex}{alpha:02x}")
        
    return fading_palette
