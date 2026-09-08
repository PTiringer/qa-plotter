from unittest.mock import Mock

import pytest
import requests

from qa_plotter.scraper import (
    Measurement,
    combine_date_time,
    fetch_measurements,
    read_csv,
    write_csv,
)


@pytest.mark.parametrize(
    ('date', 'time', 'expected'),
    [
        (20250305, '104119.703000', '2025-03-05T10:41:19.703000'),
        ('20250305', '419.2', '2025-03-05T00:04:19.200000'),
        (20250305, 0, '2025-03-05T00:00:00'),
        (20250305, '104119.1234567', '2025-03-05T10:41:19.123456'),
    ],
)
def test_timestamp(date, time, expected):
    assert combine_date_time(date, time) == expected


@pytest.mark.parametrize('time', ['240000', '12.bad', '', '-1'])
def test_invalid_timestamp(time):
    with pytest.raises(ValueError):
        combine_date_time('20250305', time)


def response(data=None, status=200):
    result = Mock(status_code=status)
    result.json.return_value = data
    if status >= 400:
        result.raise_for_status.side_effect = requests.HTTPError(str(status))
    return result


def test_fetch_filters_skips_missing_and_sorts():
    session = Mock()
    series = [
        dict(id=i, Description='QA', Coil='Head', Date=20250305, Time=time)
        for i, time in [(1, '120000'), (2, '100000'), (3, '110000')]
    ]
    session.get.side_effect = [
        response(
            [{'id': 0, 'Scanner': 'Other'}, {'id': 1, 'Scanner': 'MAGNETOM Terra.X'}]
        ),
        response(series),
        response({'ROI_SNR': 20}),
        response(status=404),
        response({'ROI_SNR': '10.5'}),
    ]
    values = fetch_measurements(session=session)
    assert [item.roi_snr for item in values] == [10.5, 20.0]
    assert session.get.call_count == 5
    session.get.assert_any_call('http://manati:3000/api/studies/1/series', timeout=30.0)


@pytest.mark.parametrize('status', [401, 500])
def test_qa_errors_are_not_silently_skipped(status):
    session = Mock()
    session.get.side_effect = [
        response([{'id': 1, 'Scanner': 'MAGNETOM Terra.X'}]),
        response([{'id': 2}]),
        response(status=status),
    ]
    with pytest.raises(requests.HTTPError):
        fetch_measurements(session=session)


def test_timeout_propagates():
    session = Mock()
    session.get.side_effect = requests.Timeout('unavailable')
    with pytest.raises(requests.Timeout):
        fetch_measurements(session=session)


def test_csv_roundtrip_and_order(tmp_path):
    later = Measurement('2025-03-05T12:00:00', 5.5, 'QA, scan', 'Head ü')
    earlier = Measurement('2025-03-05T10:00:00', 2.5, 'QA', 'Coil')
    output = tmp_path / 'mri_qa.csv'
    write_csv([later, earlier], output)
    assert read_csv(output) == [earlier, later]
    write_csv([], output)
    assert read_csv(output) == []


def test_failed_write_preserves_existing_export(tmp_path):
    output = tmp_path / 'mri_qa.csv'
    output.write_text('previous export')
    invalid = Mock(timestamp='2025-03-05')
    invalid.as_row.side_effect = ValueError('bad row')
    with pytest.raises(ValueError):
        write_csv([invalid], output)
    assert output.read_text() == 'previous export'
    assert list(tmp_path.iterdir()) == [output]


@pytest.mark.parametrize(
    'row',
    [
        'bad,1,QA,Head',
        '2025-03-05T10:00:00,nan,QA,Head',
        '2025-03-05T10:00:00,1,QA',
    ],
)
def test_invalid_csv(tmp_path, row):
    output = tmp_path / 'bad.csv'
    output.write_text('datetime,ROI_SNR,Description,Coil\n' + row + '\n')
    with pytest.raises(ValueError, match='line 2'):
        read_csv(output)
