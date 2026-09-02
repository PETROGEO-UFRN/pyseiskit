from .modules import gain
from .modules import palettes
from .modules import sourceData
from .modules import clip

# Expose the applyGains function directly at the root
from .modules.applyGains.applyGains import applyGains, GainType
