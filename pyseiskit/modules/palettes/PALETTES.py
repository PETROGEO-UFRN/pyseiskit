from bokeh.palettes import Greys256, viridis
from colorcet import rainbow4


from .getFadingPalette import getFadingPalette

PALETTES = {
	"Greys256": Greys256,
	"FadingGreys": getFadingPalette(Greys256),
	"viridis": viridis(256),
	"rainbow": rainbow4,
}
