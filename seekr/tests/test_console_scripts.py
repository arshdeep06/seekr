"""These tests are treated a little like integration tests."""

import networkx
import numpy as np
import pandas as pd
import pkg_resources

from pathlib import Path

from seekr import console_scripts


class TestConsoleScripts:

    # TODO Move to integration testing or somewhere that doesn't mess with Travis
    # def test_run_download_gencode(self, tmpdir):
    #     out_path = Path(tmpdir, 'lncs.fa.gz')
    #     unzipped = Path(tmpdir, 'lncs.fa')
    #     console_scripts._run_download_gencode(biotype='lncRNA',
    #                                           species='human',
    #                                           release='20',
    #                                           out_path=str(out_path),
    #                                           unzip=True)
    #     assert not out_path.exists()
    #     assert unzipped.exists()
    #     with unzipped.open() as in_file:
    #         count = len(in_file.readlines())
    #         assert count == 48978

    def test_run_kmer_counts(self, tmpdir):
        infasta = 'tests/data/example.fa'
        infasta = pkg_resources.resource_filename('seekr', infasta)
        outfile = str(tmpdir.join('2mers.npy'))
        console_scripts._run_kmer_counts(fasta=infasta,
                                         outfile=outfile,
                                         kmer=2,
                                         binary=True,
                                         centered=True,
                                         standardized=True,
                                         log2=True,
                                         remove_labels=True,
                                         mean_vector=None,
                                         std_vector=None)
        kmers = np.load(outfile)
        expected = 'tests/data/example_2mers.npy'
        expected = pkg_resources.resource_filename('seekr', expected)
        expected = np.load(expected)
        assert np.allclose(kmers, expected)

    def test_run_kmer_counts_raw_csv(self, tmpdir):
        infasta = 'tests/data/example.fa'
        infasta = pkg_resources.resource_filename('seekr', infasta)
        outfile = str(tmpdir.join('3mers.csv'))
        console_scripts._run_kmer_counts(fasta=infasta,
                                         outfile=outfile,
                                         kmer=3,
                                         binary=False,
                                         centered=False,
                                         standardized=False,
                                         log2=False,
                                         remove_labels=True,
                                         mean_vector=None,
                                         std_vector=None)
        kmers = pd.read_csv(outfile, header=None)
        expected = 'tests/data/example_3mers_raw.csv'
        expected = pkg_resources.resource_filename('seekr', expected)
        expected = pd.read_csv(expected, header=None)
        assert np.allclose(kmers.values, expected.values)

    def test_run_kmer_counts_vectors(self, tmpdir):
        infasta = 'tests/data/example.fa'
        infasta = pkg_resources.resource_filename('seekr', infasta)
        mean_vector = 'tests/data/example_mean.npy'
        mean_vector = pkg_resources.resource_filename('seekr', mean_vector)
        std_vector = 'tests/data/example_std.npy'
        std_vector = pkg_resources.resource_filename('seekr', std_vector)
        outfile = str(tmpdir.join('2mers_vectors.npy'))
        console_scripts._run_kmer_counts(fasta=infasta,
                                         outfile=outfile,
                                         kmer=2,
                                         binary=True,
                                         centered=False,
                                         standardized=False,
                                         log2=True,
                                         remove_labels=True,
                                         mean_vector=mean_vector,
                                         std_vector=std_vector)
        kmers = np.load(outfile)
        expected = 'tests/data/example_2mers.npy'
        expected = pkg_resources.resource_filename('seekr', expected)
        expected = np.load(expected)
        assert np.allclose(kmers, expected)

    def test_run_norm_vectors(self, tmpdir):
        infasta = 'tests/data/example.fa'
        infasta = pkg_resources.resource_filename('seekr', infasta)
        mean = str(tmpdir.join('mean.npy'))
        std = str(tmpdir.join('std.npy'))
        console_scripts._run_norm_vectors(fasta=infasta,
                                          mean_vector=mean,
                                          std_vector=std,
                                          kmer=2)
        mean = np.load(mean)
        std = np.load(std)
        expected_mean = 'tests/data/example_mean.npy'
        expected_mean = pkg_resources.resource_filename('seekr', expected_mean)
        expected_mean = np.load(expected_mean)
        expected_std = 'tests/data/example_std.npy'
        expected_std = pkg_resources.resource_filename('seekr', expected_std)
        expected_std = np.load(expected_std)
        assert np.allclose(mean, expected_mean)
        assert np.allclose(std, expected_std)

    def test_run_graph(self, tmpdir):
        kmers = 'tests/data/example_2mers.npy'
        kmers = pkg_resources.resource_filename('seekr', kmers)
        kmers = np.load(kmers)
        adj = np.corrcoef(kmers) * -1  # Flip signs for fewer negatives
        names = list(range(5))
        adj = pd.DataFrame(adj, names, names)
        adj_path = str(tmpdir.join('adj.csv'))
        adj.to_csv(adj_path)
        gml_path = str(tmpdir.join('graph.gml'))
        csv_path = str(tmpdir.join('communities.csv'))
        console_scripts._run_graph(adj=adj,
                                   gml_path=gml_path,
                                   csv_path=csv_path,
                                   louvain=False,
                                   threshold=.15,
                                   resolution=1,
                                   n_comms=5,
                                   seed=0)
        in_graph = networkx.read_gml(gml_path)
        in_df = pd.read_csv(csv_path, index_col=0)
        assert list(in_graph.nodes()) == [str(i) for i in range(5)]
        expected_weight = in_graph.edges()[('0', '2')]['weight']
        assert np.isclose(expected_weight, 0.5278957407763157)
        assert np.alltrue(in_df['Group'].values == np.array([0, 1, 0, 0, 1]))

