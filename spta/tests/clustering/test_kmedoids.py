'''
Unit tests for spta.clustering.kmedoids module.
'''

import unittest

from spta.clustering.kmedoids import KmedoidsClusteringMetadata


class TestKmedoidsClusteringMetadata(unittest.TestCase):
    '''
    Unit tests for spta.clustering.kmedoids.KmedoidsClusteringMetadata.
    '''

    def test_constructor_default(self):
        # given
        k = 4

        # when
        metadata = KmedoidsClusteringMetadata(k)

        # then
        self.assertEqual(metadata.name, 'kmedoids')
        self.assertEqual(metadata.k, k)
        self.assertEqual(metadata.random_seed, 1)
        self.assertEqual(metadata.verbose, True)

    def test_constructor_not_default(self):
        # given
        k = 5
        random_seed = 2
        verbose = False

        # when
        metadata = KmedoidsClusteringMetadata(k, random_seed=random_seed, verbose=verbose)

        # then
        self.assertEqual(metadata.name, 'kmedoids')
        self.assertEqual(metadata.k, k)
        self.assertEqual(metadata.random_seed, random_seed)
        self.assertEqual(metadata.verbose, verbose)

    def test_repr(self):
        # given
        k = 5
        random_seed = 2
        metadata = KmedoidsClusteringMetadata(k, random_seed=random_seed)

        # when
        r = '{!r}'.format(metadata)

        # then
        self.assertEqual('kmedoids_k5_seed2', r)

    def test_repr_with_initial_medoids(self):
        # given
        k = 3
        random_seed = 2
        initial_medoids = [1, 2, 3]
        metadata = KmedoidsClusteringMetadata(k, random_seed=random_seed,
                                              initial_medoids=initial_medoids)

        # when
        r = '{!r}'.format(metadata)

        # then
        self.assertEqual('kmedoids_k3_seed2_im1-2-3', r)

    def test_str(self):
        # given
        k = 5
        random_seed = 2
        metadata = KmedoidsClusteringMetadata(k, random_seed=random_seed)

        # when
        s = '{}'.format(metadata)

        # then
        self.assertEqual('Kmedoids: k=5 seed=2', s)
