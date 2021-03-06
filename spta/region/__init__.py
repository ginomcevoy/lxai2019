import numpy as np

from collections import namedtuple

Point = namedtuple('Point', 'x y')
Region = namedtuple('Region', 'x1, x2, y1, y2')
TimeInterval = namedtuple('TimeInterval', 't1 t2')


def reshape_1d_to_2d(list_1d, x, y):
    return np.array(list_1d).reshape(x, y)

# these are after the Point / Region / TimeInterval
# from .spatial import SpatialRegion, SpatialCluster
# from .temporal import SpatioTemporalRegion, SpatioTemporalRegionMetadata, SpatioTemporalCluster


# def transpose_region(numpy_region_dataset):
#     '''
#     Instead of [time_series, x, y], work with [x, y, time_series]
#     '''
#     (series_len, x_len, y_len) = numpy_region_dataset.shape

#     # 'Fortran-style' will gather time_series points when flattening ('transpose')
#     flattened = numpy_region_dataset.ravel('F')
#     return flattened.reshape(x_len, y_len, series_len)


# Adding to __all__ is triggering this warning
# best to avoid this and import from each submodule
# /usr/lib64/python3.6/runpy.py:125: RuntimeWarning: 'spta.region.temporal' found in sys.modules
# after import of package 'spta.region', but prior to execution of 'spta.region.temporal'; this
# may result in unpredictable behaviour
#   warn(RuntimeWarning(msg))


# __all__ = [
#     'Point', 'Region', 'TimeInterval', 'reshape_1d_to_2d', 'SpatialRegion', 'SpatioTemporalRegion',
#     'SpatioTemporalRegionMetadata', 'SpatialCluster', 'SpatioTemporalCluster'
# ]
