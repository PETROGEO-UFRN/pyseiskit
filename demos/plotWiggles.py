from bokeh.plotting import figure
from pyseiskit.modules import sourceData

def plotWiggles(gatherData, timeSamples, traceOffsets, title, width=450):
    """
    Shared utility for generating a Bokeh figure of seismic wiggle traces.
    """
    plotFigure = figure(
        width=width,
        height=600,
        title=title,
        x_axis_label="Offset (m)",
        y_axis_label="Time (s)",
        y_range=(timeSamples[-1], timeSamples[0])
    )
    
    scaledGatherData = sourceData.rescaleDataForWiggle(
        gatherData,
        traceOffsets,
        overlap=1.5
    )
    lineData = sourceData.wiggleLinesDataFactory(
        scaledGatherData,
        traceOffsets,
        timeSamples
    )
    patchData = sourceData.wigglePatchesDataFactory(
        scaledGatherData,
        traceOffsets,
        timeSamples,
        fillMode='positive'
    )
    
    plotFigure.multi_line(xs=lineData['amplitudeCoordinates'], ys=lineData['timeCoordinates'], color='black', line_width=0.5)
    plotFigure.patches(xs=patchData['amplitudeCoordinates'], ys=patchData['timeCoordinates'], color='black', line_width=0)

    plotFigure.xgrid.grid_line_color = None
    plotFigure.ygrid.grid_line_color = None
    return plotFigure
