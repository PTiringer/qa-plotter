"""Export MANATI MRI QA measurements without requiring a running NOMAD instance."""

import argparse
import csv
import math
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from urllib.parse import quote

import requests

DATE_DIGITS = 8
TIME_DIGITS = 6

FIELDS = ['datetime', 'ROI_SNR', 'Description', 'Coil']


def combine_date_time(date_value, time_value):
    """Convert MANATI date/time values to ISO local time (timezone unknown)."""
    date_str = str(date_value).strip()
    time_main, separator, fraction = str(time_value).strip().partition('.')
    if (
        len(date_str) != DATE_DIGITS
        or not date_str.isdigit()
        or not time_main.isdigit()
        or len(time_main) > TIME_DIGITS
        or (separator and not fraction.isdigit())
    ):
        raise ValueError(f'Invalid MANATI timestamp: {date_value!r} {time_value!r}')
    value = datetime.strptime(date_str + time_main.zfill(6), '%Y%m%d%H%M%S')
    if fraction:
        value = value.replace(microsecond=int((fraction + '000000')[:6]))
    return value.isoformat()


@dataclass(frozen=True)
class Measurement:
    timestamp: str
    roi_snr: float
    description: str
    coil: str

    def __post_init__(self):
        datetime.fromisoformat(self.timestamp)
        if not math.isfinite(self.roi_snr):
            raise ValueError('ROI_SNR must be finite')
        if not isinstance(self.description, str) or not isinstance(self.coil, str):
            raise ValueError('Description and Coil must be strings')

    def as_row(self):
        return dict(
            zip(FIELDS, (self.timestamp, self.roi_snr, self.description, self.coil))
        )


def fetch_measurements(
    base_url='http://manati:3000',
    scanner='MAGNETOM Terra.X',
    collection='QA_7T',
    timeout=30.0,
    session=None,
):
    """Fetch matching studies. Only a missing QA collection (404) is skipped."""
    if timeout <= 0 or not math.isfinite(timeout):
        raise ValueError('Timeout must be a positive finite number')
    if session is None:
        with requests.Session() as client:
            return fetch_measurements(base_url, scanner, collection, timeout, client)

    missing = object()

    def fetch(path, optional=False):
        response = session.get(f'{base_url.rstrip("/")}/api/{path}', timeout=timeout)
        if optional and response.status_code == HTTPStatus.NOT_FOUND:
            return missing
        response.raise_for_status()
        return response.json()

    def segment(value):
        return quote(str(value), safe='')

    measurements = []
    for study in fetch('studies'):
        if study['Scanner'] != scanner:
            continue
        for series in fetch(f'studies/{segment(study["id"])}/series'):
            qa = fetch(
                f'series/{segment(series["id"])}/col/{segment(collection)}',
                optional=True,
            )
            if qa is missing:
                continue
            measurements.append(
                Measurement(
                    combine_date_time(series['Date'], series['Time']),
                    float(qa['ROI_SNR']),
                    series['Description'],
                    series['Coil'],
                )
            )
    return sorted(measurements, key=lambda item: item.timestamp)


def write_csv(measurements, output_file):
    """Replace the destination only after the complete CSV has been written."""
    output = Path(output_file)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            newline='',
            encoding='utf-8',
            dir=output.parent,
            prefix=f'.{output.name}.',
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(
                item.as_row()
                for item in sorted(
                    measurements,
                    key=lambda item: item.timestamp,
                )
            )
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_csv(mainfile):
    """Read and validate the export before assigning any NOMAD archive data."""
    with open(mainfile, newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError(f'Expected CSV columns: {", ".join(FIELDS)}')
        measurements = []
        for row in reader:
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError('Incorrect number of columns')
                measurements.append(
                    Measurement(
                        datetime.fromisoformat(row['datetime']).isoformat(),
                        float(row['ROI_SNR']),
                        row['Description'],
                        row['Coil'],
                    )
                )
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f'Invalid QA CSV record at line {reader.line_num}: {exc}'
                ) from exc
    return sorted(measurements, key=lambda item: item.timestamp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://manati:3000')
    parser.add_argument('--scanner', default='MAGNETOM Terra.X')
    parser.add_argument('--collection', default='QA_7T')
    parser.add_argument('--timeout', type=float, default=30.0)
    parser.add_argument('--output', default='mri_qa.csv')
    args = parser.parse_args()
    try:
        measurements = fetch_measurements(
            args.base_url,
            args.scanner,
            args.collection,
            args.timeout,
        )
        write_csv(measurements, args.output)
    except (requests.RequestException, ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'QA export failed: {exc}\n')
    print(f'Wrote {len(measurements)} measurements to {args.output}')
    for measurement in measurements[:5]:
        print(measurement.as_row())


if __name__ == '__main__':
    main()
