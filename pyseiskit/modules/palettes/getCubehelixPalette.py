import math

def getCubehelixPalette(n_colors=256, start=0.5, rot=-1.5, hue=1.0, gamma=1.0):
    """
    Generates a Dave Green's cubehelix colormap dynamically.
    Instead of hardcoding hundreds of hex values, this uses the 
    analytic mathematical definition of the helix through the RGB color cube.
    """
    palette = []
    for i in range(n_colors):
        fract = i / (n_colors - 1) if n_colors > 1 else 0
        fract_gamma = fract ** gamma
        
        amplitude = hue * fract_gamma * (1 - fract_gamma) / 2.0
        angle = 2 * math.pi * (start / 3.0 + rot * fract)
        
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        r = fract_gamma + amplitude * (-0.14861 * cos_angle + 1.78277 * sin_angle)
        g = fract_gamma + amplitude * (-0.29227 * cos_angle - 0.90649 * sin_angle)
        b = fract_gamma + amplitude * ( 1.97294 * cos_angle)
        
        # Clamp strictly to 0-1 range to handle rounding/hue clipping
        r = max(0.0, min(1.0, r))
        g = max(0.0, min(1.0, g))
        b = max(0.0, min(1.0, b))
        
        palette.append(f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}")
        
    return palette
