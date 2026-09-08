from nomad.normalizing import Normalizer

from qa_plotter.scraper import fetch_measurements


class MRIQANormalizer(Normalizer):
    """Refresh explicitly opted-in QA entries before MetainfoNormalizer plots them."""

    domain = None

    def __init__(
        self,
        base_url='http://manati:3000',
        scanner='MAGNETOM Terra.X',
        collection='QA_7T',
        timeout=30.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.scanner = scanner
        self.collection = collection
        self.timeout = timeout

    def normalize(self, archive, logger=None):
        from qa_plotter.schema_packages.schema_package import MRIQAPlot

        data = archive.data
        if data is None or not any(
            definition.m_resolved() is MRIQAPlot.m_def
            for definition in [data.m_def, *data.m_def.all_base_sections]
        ):
            return
        # Fetch and validate everything first. A failure leaves existing arrays intact
        # and is reported by NOMAD's normalizer runner.
        measurements = fetch_measurements(
            base_url=self.base_url,
            scanner=self.scanner,
            collection=self.collection,
            timeout=self.timeout,
        )
        data.datetime = [value.timestamp for value in measurements]
        data.roi_snr = [value.roi_snr for value in measurements]
        data.description = [value.description for value in measurements]
        data.coil = [value.coil for value in measurements]
        if logger is not None:
            logger.info('Fetched MANATI MRI QA measurements', count=len(measurements))
