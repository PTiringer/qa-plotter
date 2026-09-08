from pathlib import Path
from unittest.mock import patch

import pytest
import requests
from nomad.client import normalize_all
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.data import EntryData
from nomad.parsing.parser import ArchiveParser

from qa_plotter.normalizers import MRIQANormalizerEntryPoint
from qa_plotter.schema_packages.schema_package import MRIQAPlot
from qa_plotter.scraper import Measurement

MEASUREMENTS = [
    Measurement('2025-03-05T10:00:00', 10.0, 'QA', 'Head'),
    Measurement('2025-03-05T12:00:00', 20.0, 'QA other', 'Other coil'),
]
FETCH = 'qa_plotter.normalizers.normalizer.fetch_measurements'


def test_refresh_replaces_all_arrays():
    archive = EntryArchive(data=MRIQAPlot())
    from nomad import normalizing

    assert list(normalizing.normalizers)[0].normalizer_level == -1
    normalizer = MRIQANormalizerEntryPoint(
        base_url='http://test:3000', timeout=5
    ).load()
    with patch(FETCH, return_value=MEASUREMENTS) as fetch:
        normalizer.normalize(archive)
        normalizer.normalize(archive)
    fetch.assert_called_with(
        base_url='http://test:3000',
        scanner='MAGNETOM Terra.X',
        collection='QA_7T',
        timeout=5,
    )
    assert list(archive.data.roi_snr) == [10.0, 20.0]
    assert list(archive.data.datetime) == [item.timestamp for item in MEASUREMENTS]
    assert list(archive.data.description) == ['QA', 'QA other']
    assert list(archive.data.coil) == ['Head', 'Other coil']


def test_unrelated_entries_never_fetch():
    normalizer = MRIQANormalizerEntryPoint().load()
    with patch(FETCH) as fetch:
        normalizer.normalize(EntryArchive())
        normalizer.normalize(EntryArchive(data=EntryData()))
    fetch.assert_not_called()


def test_failed_refresh_preserves_arrays():
    archive = EntryArchive(
        data=MRIQAPlot(datetime=['old'], roi_snr=[1], description=['old'], coil=['old'])
    )
    with patch(FETCH, side_effect=requests.Timeout('MANATI unavailable')):
        with pytest.raises(requests.Timeout):
            MRIQANormalizerEntryPoint().load().normalize(archive)
    assert list(archive.data.roi_snr) == [1]
    assert list(archive.data.datetime) == ['old']


def test_empty_refresh_clears_previous_values():
    archive = EntryArchive(data=MRIQAPlot(datetime=['old'], roi_snr=[1]))
    with patch(FETCH, return_value=[]):
        MRIQANormalizerEntryPoint().load().normalize(archive)
    assert list(archive.data.roi_snr) == []
    assert list(archive.data.datetime) == []


def test_yaml_schema_fetches_before_plotting():
    example = (
        Path(__file__).parents[2]
        / 'src/qa_plotter/example_uploads/manati_qa/mri_qa.archive.yaml'
    )
    archive = EntryArchive(metadata=EntryMetadata())
    ArchiveParser().parse(str(example), archive)
    if archive.metadata is None:
        archive.metadata = EntryMetadata()
    with patch(FETCH, return_value=MEASUREMENTS) as fetch:
        normalize_all(archive)
    fetch.assert_called_once()
    assert list(archive.data.roi_snr) == [10.0, 20.0]
    assert len(archive.data.figures) == 1
    trace = archive.data.figures[0].figure['data']
    assert trace['y'] == '#roi_snr'
    assert list(archive.data.m_resolve(trace['y'][1:])) == [10.0, 20.0]
    assert trace['x'] == '#datetime'
    assert list(archive.data.m_resolve(trace['x'][1:])) == [
        item.timestamp for item in MEASUREMENTS
    ]
