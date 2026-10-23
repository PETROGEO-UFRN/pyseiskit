from bokeh.palettes import Greys256, viridis, turbo, plasma, magma, inferno, RdBu as bokeh_RdBu
from colorcet import rainbow4, rainbow

from .getFadingPalette import getFadingPalette
from .jet import getJetPalette
from .getCubehelixPalette import getCubehelixPalette
from .getInterpolatedPalette import getInterpolatedPalette

# Remaining empirical scientific colormaps (require complex CAM02-UCS transformations, must be hardcoded)
from .batlow import batlow
from .nipy_spectral import nipy_spectral

PALETTES = {
    "Greys256": Greys256,
    "FadingGreys": getFadingPalette(Greys256),
    "viridis": viridis(256),
    "rainbow": rainbow4,
    
    # Generated analytically via math functions
    "jet": getJetPalette(256),
    "cubehelix_perceptual_rainbow": getCubehelixPalette(256, start=0, rot=-1.5, hue=1.5, gamma=1.0),
    "cubehelix_purple": getCubehelixPalette(256, start=2.8, rot=0.1, hue=1.0, gamma=1.0),
    "RdBu": getInterpolatedPalette(bokeh_RdBu[11], 256),
    
    # Natively loaded from Bokeh (already in use)
    "turbo": turbo(256),
    "plasma": plasma(256),
    "magma": magma(256),
    "inferno": inferno(256),
    
    # Natively loaded from ColorCET (already in use)
    "cet-rainbow": rainbow,
    
    # Lookup tables for perceptually uniform scientific maps lacking simple analytical definitions
    "batlow": batlow,
    "nipy_spectral": nipy_spectral,
}
