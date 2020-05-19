import numpy as np
from spta.distance.dtw import DistanceByDTW
from spta.util import log as log_util
from spta.util import arrays as arrays_util
from spta.util import error as error_util

from .spatial import SpatialDecorator


class ErrorRegion(SpatialDecorator):
    '''
    A spatial region where each value represents the forecast error of a model.
    Uses the decorator pattern to allow integration with new subclasses of SpatialRegion.

    Here we don't work with forecast/observation regions, subclasses will.
    '''
    def __init__(self, decorated_region, **kwargs):
        super(ErrorRegion, self).__init__(decorated_region, **kwargs)

    @property
    def overall_error(self):
        '''
        Calculate a single value for the forecast error in the region.
        We use Root Mean Squared to find the RMSE value.
        '''
        error_list = []

        # this iterator will iterate over all the valid points in the region
        for point, error_at_point in self:
            error_list.append(error_at_point)

        # single RMSE value for region
        return arrays_util.root_mean_squared(error_list)

    def point_with_min_error(self):
        '''
        Searches the errors in the region for the smallest. Returns the (x, y) coordinates as
        region.Point (2d)

        Uses the instance iterator, cannot be used inside another iteration over itself!
        '''
        # save the min value
        min_value = np.Inf
        min_point = None

        # use the iterator, should work as expected for subclasses of SpatialRegion
        for (point, value) in self:
            if value < min_value:
                min_value = value
                min_point = point

        return min_point

    def __next__(self):
        '''
        Use the decorated iteration, which may be more interesting than the default iteration
        from SpatialRegion.
        '''
        return self.decorated_region.__next__()


class ErrorRegionMASE(ErrorRegion):
    '''
    A spatial region where each value represents the forecast error of a model using MASE
    (Mean Absolute Scaled Error).

    In addition to observation values, MASE requires values in the training region (Yi) to scale
    the forecast error:

    qt = et / [(1 / n-1) * sum(| Y_i - Y_{i-1}|, i=2, i=n)
    MASE = mean(|qt|)
    '''
    # def __init__(self, decorated_region, **kwargs):
    #     super(ErrorRegionMASE, self).__init__(decorated_region, **kwargs)

    # def create_from_forecast(cls, forecast_region, observation_region, training_region):
    def __init__(self, forecast_region, observation_region, training_region):
        '''
        Create an instance of ErrorRegionMASE, by aplying MASE to each point in the forecast
        region. The instance will be region with the MASE error in each point.
        This requires not only the forecast and observation regions, but also the training region.
        '''
        (forecast_len, f_x_len, f_y_len) = forecast_region.shape
        (observation_len, o_x_len, o_y_len) = observation_region.shape
        (training_len, t_x_len, t_y_len) = training_region.shape

        # sanity check: all have the same 2D region
        assert (f_x_len, f_y_len) == (o_x_len, o_y_len)
        assert (f_x_len, f_y_len) == (t_x_len, t_y_len)

        # sanity check: forecasts and observations have the same length
        assert forecast_len == observation_len
        log_msg = 'Forecast: <{}> Observation: <{}>'
        self.logger.debug(log_msg.format(forecast_region.shape, observation_region.shape))

        # tell forecast region to create a new region, this way we get behavior from subclasses
        # of SpatialRegion
        decorated_region = forecast_region.empty_region_2d()
        error_region_np = decorated_region.as_numpy

        # iterate over the forecast points
        for (point_ij, forecast_series_ij) in forecast_region:

            # corresponding observation and training series at Point(i, j)
            observation_series_ij = observation_region.series_at(point_ij)
            training_series_ij = training_region.series_at(point_ij)

            # calculate MASE for Point(i, j)
            error_ij = error_util.mase(forecast_series_ij, observation_series_ij,
                                       training_series_ij)
            error_region_np[point_ij.x, point_ij.y] = error_ij

        # finally create the instance of this class: the decorated region contains the data,
        # we wrap around this region to get ErrorRegion methods
        super(ErrorRegionMASE, self).__init__(decorated_region)


class ErrorRegionOld(SpatialDecorator):
    '''
    A spatial region where each value represents the forecast error of a model.
    It is created by measuring the distance between a forecast region and a test region.

    Uses the decorator pattern to allow integration with new subclasses of SpatialRegion.
    '''

    def __init__(self, decorated_region, distance_measure, **kwargs):
        super(ErrorRegionOld, self).__init__(decorated_region, **kwargs)
        self.distance_measure = distance_measure

    @property
    def combined_error(self):

        # iterate over all elements to get error array, then combine the errors
        errors = []
        for point, error_at_point in self:
            errors.append(error_at_point)
        return self.distance_measure.combine(errors)

    def point_with_min_error(self):
        '''
        Searches the errors in the region for the smallest. Returns the (x, y) coordinates as
        region.Point (2d)

        Uses the instance iterator, cannot be used inside another iteration over itself!
        '''
        # save the min value
        min_value = np.Inf
        min_point = None

        # use the iterator, should work as expected for subclasses of SpatialRegion
        for (point, value) in self:
            if value < min_value:
                min_value = value
                min_point = point

        return min_point

    def __next__(self):
        '''
        Use the decorated iteration, which may be more interesting than the "default" from
        SpatialCluster.
        '''
        return self.decorated_region.__next__()

    @classmethod
    def create_from_forecasts(cls, forecast_region, test_region,
                              distance_measure=DistanceByDTW()):

        (series1_len, x1_len, y1_len) = forecast_region.shape
        (series2_len, x2_len, y2_len) = test_region.shape

        logger = log_util.logger_for_me(cls.create_from_forecasts)
        logger.debug('Forecast: <{}> Test: <{}>'.format(forecast_region.shape, test_region.shape))

        # we need them to be about the same region and same series length
        assert((series1_len, x1_len, y1_len) == (series2_len, x2_len, y2_len))

        # # work with lists, each element is a time series
        # forecast_as_list = forecast_region.as_list
        # test_as_list = test_region.as_list

        # # Use list comprehension and zip to iterate over the two lists at the same time.
        # # This will combine the forecast and test series of the same point, for each point.
        # error_list = [
        #     distance_measure.measure(forecast_series, test_series)
        #     for (forecast_series, test_series)
        #     in zip(forecast_as_list, test_as_list)
        # ]

        # # recreate the region
        # error_numpy_dataset = reshape_1d_to_2d(error_list, x1_len, y1_len)
        # return ErrorRegion(error_numpy_dataset, distance_measure)

        # create SpatialRegion now, this will work when using a subclass too
        decorated_region = forecast_region.empty_region_2d()
        error_region_np = decorated_region.as_numpy

        # iterate over the forecast points
        for (point_ij, forecast_series_ij) in forecast_region:

            # corresponding test series
            test_series_ij = test_region.series_at(point_ij)

            # calculate the forecast error for this point
            error_ij = distance_measure.measure(forecast_series_ij, test_series_ij)
            error_region_np[point_ij.x, point_ij.y] = error_ij

        # wrap the data around the ErrorRegion decorator to get its methods
        return ErrorRegion(decorated_region, distance_measure)
