import numpy as np
import numpy.typing as np_types

def __calculateChannelIntensity(
    normalizedRange: np_types.NDArray,
    phaseOffset: float
) -> np_types.NDArray:
    """
    Computes the triangular intensity wave for a given color channel.
    """
    channel = np.clip(
        1.5 - np.abs(4.0 * normalizedRange - phaseOffset),
        0.0,
        1.0
    )
    return channel

def getJetPalette(numberColors: int = 256) -> list[str]:
    """
    The classic 'jet' colormap (dark blue -> cyan -> yellow -> dark red).
    """
    normalizedRange = np.linspace(0.0, 1.0, numberColors)

    redChannel = __calculateChannelIntensity(normalizedRange, 3.0)
    greenChannel = __calculateChannelIntensity(normalizedRange, 2.0)
    blueChannel = __calculateChannelIntensity(normalizedRange, 1.0)

    rgbArray = (
        np.stack([redChannel, greenChannel, blueChannel], axis=1) * 255.0
    ).round().astype(int)

    rgbHexCodes = [f"#{red:02x}{green:02x}{blue:02x}" for red, green, blue in rgbArray]
    return rgbHexCodes
