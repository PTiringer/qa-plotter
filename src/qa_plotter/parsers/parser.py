from pathlib import Path

from nomad.parsing.parser import MatchingParser

from qa_plotter.schema_packages.schema_package import MRIQA, MRISeries
from qa_plotter.scraper import read_csv


class MRIQAParser(MatchingParser):
    def parse(self, mainfile, archive, logger, child_archives=None):
        measurements = read_csv(mainfile)
        data = MRIQA(
            source_file=Path(mainfile).name, measurement_count=len(measurements)
        )
        groups = {}
        for measurement in measurements:
            key = (measurement.description, measurement.coil)
            groups.setdefault(key, []).append(measurement)
        for (description, coil), values in groups.items():
            data.series.append(
                MRISeries(
                    description=description,
                    coil=coil,
                    datetime=[value.timestamp for value in values],
                    roi_snr=[value.roi_snr for value in values],
                )
            )
        archive.data = data
