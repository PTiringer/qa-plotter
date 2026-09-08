import logging

from nomad.datamodel import EntryArchive

from qa_plotter.parsers import parser_entry_point
from qa_plotter.scraper import Measurement, write_csv


def test_parse_file(tmp_path):
    path = tmp_path / 'mri_qa.csv'
    write_csv(
        [
            Measurement('2025-03-05T12:00:00', 20, 'QA', 'Head'),
            Measurement('2025-03-05T10:00:00', 10, 'QA', 'Head'),
            Measurement('2025-03-05T11:00:00', 15, 'QA', 'Other'),
        ],
        path,
    )
    parser = parser_entry_point.load()
    archive = EntryArchive()
    parser.parse(str(path), archive, logging.getLogger())
    assert archive.data.measurement_count == 3
    assert archive.data.source_file == 'mri_qa.csv'
    assert len(archive.data.series) == 2
    head = archive.data.series[0]
    assert head.coil == 'Head'
    assert list(head.roi_snr) == [10, 20]
    assert list(head.datetime) == ['2025-03-05T10:00:00', '2025-03-05T12:00:00']
    assert archive.m_to_dict()['data']['series'][0]['roi_snr'] == [10, 20]


def test_empty_export(tmp_path):
    path = tmp_path / 'mri_qa.csv'
    write_csv([], path)
    archive = EntryArchive()
    parser_entry_point.load().parse(str(path), archive, logging.getLogger())
    assert archive.data.measurement_count == 0
    assert len(archive.data.series) == 0


def test_csv_detection():
    parser = parser_entry_point.load()
    header = 'datetime,ROI_SNR,Description,Coil\r\n'
    assert parser.is_mainfile('mri_qa.csv', 'text/csv', header.encode(), header)
    assert not parser.is_mainfile('other.csv', 'text/csv', b'x,y\n', 'x,y\n')
