def getInterpolatedPalette(base_colors, n_colors=256):
    """
    Linearly interpolates a discrete list of hex colors to generate a smooth 
    continuous colormap of `n_colors` length.
    """
    if len(base_colors) < 2:
        raise ValueError("At least 2 colors are required for interpolation.")
        
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        
    def rgb_to_hex(rgb):
        return f"#{int(round(rgb[0]*255)):02x}{int(round(rgb[1]*255)):02x}{int(round(rgb[2]*255)):02x}"
        
    rgb_nodes = [hex_to_rgb(c) for c in base_colors]
    n_nodes = len(rgb_nodes)
    
    palette = []
    for i in range(n_colors):
        fract = i / (n_colors - 1) if n_colors > 1 else 0
        
        # Find which two nodes this fraction falls between
        scaled_fract = fract * (n_nodes - 1)
        left_idx = int(scaled_fract)
        right_idx = min(left_idx + 1, n_nodes - 1)
        
        # Local interpolation factor between the two nodes
        local_fract = scaled_fract - left_idx
        
        left_rgb = rgb_nodes[left_idx]
        right_rgb = rgb_nodes[right_idx]
        
        interp_rgb = (
            left_rgb[0] + (right_rgb[0] - left_rgb[0]) * local_fract,
            left_rgb[1] + (right_rgb[1] - left_rgb[1]) * local_fract,
            left_rgb[2] + (right_rgb[2] - left_rgb[2]) * local_fract
        )
        palette.append(rgb_to_hex(interp_rgb))
        
    return palette
