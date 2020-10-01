from .factory import ClusteringMetadataFactory

from spta.util import log as log_util


class ClusteringSuite(log_util.LoggerMixin):
    '''
    Abstraction that deals with a set of clustering algorithms, generated by combinations of their
    parameters. Example: for k-medoids, use a range of ks and seeds to create a list of
    KmedoidsClusteringMetadata instances with default k-medoids parameters.
    '''

    def __init__(self, identifier, metadata_name, **parameter_combinations):
        '''
        Create an instance of ClusteringSuite.

        identifier
            A suite has an identifier created by the user

        metadata_name
            Represents which clustering algorithm to use (e.g. 'kmedoids'). The metadata_name must
            match one of the available ClusteringMetadata subtypes available, a suite cannot
            include multiple metadata subtypes.

        parameter_combinations
            A dictionary, where each key represents a parameter of a ClusteringMetadata.
            The value of each key can either be single-valued or a list. If it is an iterable,
            then  this indicates that mulitple metadata instances are desired. The parameters
            are combined using cartesian product of their values.
            Note: cannot support initial_medoids argument of k-medoids, since it is a list.
            Note: for now, only k and random_seed can be iterated, this simplifies code.

        Example of k-medoids suite:

        identifier: quick
        metadata_name: kmedoids
        parameter_combinations: {
            k: {2, 3},
            random_seed: {0, 1},
            mode: 'lite'
        }

        This will create the following suite with default values of the optional parameters:
        kmedoids_k2_seed0_lite
        kmedoids_k2_seed1_lite
        kmedoids_k3_seed0_lite
        kmedoids_k3_seed1_lite
        '''
        self.logger.debug('Creating clustering suite: {} - {}'.format(identifier, metadata_name))
        self.identifier = identifier
        self.metadata_name = metadata_name

        # used to build instances
        self.factory = ClusteringMetadataFactory()

        # create the ClusteringMetadata instances
        # TODO all suites are created inside experiments.metadata, maybe lazy instantiation here?
        self.metadatas = self.__create_metadata_instances(**parameter_combinations)

    def __create_metadata_instances(self, **parameter_combinations):
        '''
        Creates the list of metadata instances given suite parameters, called during construction.
        Uses the ClusteringMetadataFactory to achieve this.
        '''

        # required
        ks = parameter_combinations.pop('k')

        # optional
        random_seeds = (1,)   # ugly but need to iterate in regular...
        if 'random_seed' in parameter_combinations:

            # received random seed parameter, is it a list or a single value?
            random_seeds = parameter_combinations.pop('random_seed')
            if isinstance(random_seeds, int):
                # single value, convert to list
                random_seeds = (random_seeds,)

        # assume the remaining paratemeters are not to be iterated in the suite
        single_value_parameters = dict(parameter_combinations)

        instances = []
        for k in ks:
            for random_seed in random_seeds:

                # put each seed here
                single_value_parameters['random_seed'] = random_seed

                # create each instance
                instances.append(self.factory.instance(self.metadata_name, k,
                                                       **single_value_parameters))

        return instances

    def csv_dir(self, output_home, region_metadata, distance_measure):
        '''
        Directory of the output CSV when analyzing this suite.
        Example: outputs/nordeste_small_2015_2015_1spd/dtw
        '''
        region_output_dir = region_metadata.output_dir(output_home)
        return '{}/{!r}'.format(region_output_dir, distance_measure)

    def analysis_csv_filename(self):
        '''
        Name of output CSV when analyzing this suite.
        Example: clustering__kmedoids-quick.csv
        '''
        return 'clustering__{!r}.csv'.format(self)

    def analysis_csv_filepath(self, output_home, region_metadata, distance_measure):
        '''
        Full path of the output CSV when analyzing this suite.
        Example: outputs/nordeste_small_2015_2015_1spd/dtw/clustering__kmedoids-quick.csv
        '''
        csv_dir = self.csv_dir(output_home, region_metadata, distance_measure)
        return '{}/{}'.format(csv_dir, self.analysis_csv_filename())

    def min_distance_csv_filename(self, count, random_seed):
        '''
        Given N, find N random points in the region that are *not* medoids found in
        this clustering suite. For these N points, find the medoid for which the DTW distance
        between the two time series (random point, medoid), is minimized.

        Returns the CSV filename for this result (result is calculated at clustering.min_distance)
        '''
        return 'random_point_dist_medoid__{!r}_count{}_seed{}.csv'.format(self, count, random_seed)

    def min_distance_csv_filepath(self, output_home, region_metadata, distance_measure,
                                  count, random_seed):
        '''
        See random_min_csv_filename, returns the full path of the CSV.
        '''
        csv_dir = self.csv_dir(output_home, region_metadata, distance_measure)
        return '{}/{}'.format(csv_dir, self.min_distance_csv_filename(count, random_seed))

    def classifier_csv_filename(self, prediction_region, tp):
        '''
        Given a classifier that was trained with the information provided by min_distance,
        and given its output for classifying the points in a prediction region with a value of
        tp for number of past samples, return the CSV filename.

        Example:
        clustering__classifier_result__kmedoids-quick__region-0-5-0-5__tp8.csv
        '''
        # TODO make region calculate its own string
        region_str = 'region-0-5-0-5'
        tp_str = 'tp8'
        return 'clustering__classifier_result__{!r}__{}__{}.csv'.format(self, region_str, tp_str)

    def __iter__(self):
        '''
        Used for iterating over metadata instances.
        '''
        return iter(self.metadatas)

    def __repr__(self):
        return '{}-{}'.format(self.metadata_name, self.identifier)
