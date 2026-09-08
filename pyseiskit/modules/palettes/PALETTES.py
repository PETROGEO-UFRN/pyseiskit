from bokeh.palettes import Greys256, viridis
from colorcet import rainbow4

from .getFadingPalette import getFadingPalette
from .jet import getJetPalette

PALETTES = {
	"Greys256": Greys256,
	"FadingGreys": getFadingPalette(Greys256),
	"viridis": viridis(256),
	"rainbow": rainbow4,
    "jet": getJetPalette(256),
}
