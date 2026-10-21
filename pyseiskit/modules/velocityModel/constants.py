"""Constants used across velocity model building functions."""

# *** Velocity models follow the gather layout [2D: samples x cdps]
TIME_AXIS = 0
CDP_AXIS = 1

# *** SU velconv floor for the squared Dix interval velocity, relative to the first squared RMS velocity
DIX_MINIMUM_SQUARED_VELOCITY_RATIO = 0.00001
