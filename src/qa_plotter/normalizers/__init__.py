from nomad.config.models.plugins import NormalizerEntryPoint
from pydantic import Field


class MRIQANormalizerEntryPoint(NormalizerEntryPoint):
    base_url: str = Field('http://manati:3000', description='MANATI API server URL')
    scanner: str = Field('MAGNETOM Terra.X', description='Scanner name to select')
    collection: str = Field('QA_7T', description='MANATI QA collection')
    timeout: float = Field(
        30.0, gt=0, allow_inf_nan=False, description='HTTP timeout in seconds'
    )

    def load(self):
        from qa_plotter.normalizers.normalizer import MRIQANormalizer

        return MRIQANormalizer(**self.model_dump())


normalizer_entry_point = MRIQANormalizerEntryPoint(
    name='MANATI MRI QA scraper',
    description='Fetch QA measurements before NOMAD generates the entry plots.',
    level=-1,
)
