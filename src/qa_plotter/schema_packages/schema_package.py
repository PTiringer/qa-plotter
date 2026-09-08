from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.metainfo import MSection, Quantity, SchemaPackage, SubSection

configuration = config.get_plugin_entry_point(
    'qa_plotter.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class NewSchemaPackage(Schema):
    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )
    message = Quantity(type=str)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        logger.info('NewSchema.normalize', parameter=configuration.parameter)
        self.message = f'Hello {self.name}!'


class MRISeries(MSection):
    """Measurements belonging to one MANATI description and coil."""

    description = Quantity(type=str)
    coil = Quantity(type=str)
    datetime = Quantity(
        type=str,
        shape=['*'],
        description='ISO 8601 acquisition local times; MANATI supplies no timezone.',
    )
    roi_snr = Quantity(type=float, shape=['*'], description='Dimensionless ROI SNR.')


class MRIQA(Schema):
    """Imported MANATI QA export, grouped for subsequent time-series plotting."""

    source_file = Quantity(type=str)
    measurement_count = Quantity(type=int)
    series = SubSection(sub_section=MRISeries, repeats=True)


class MRIQAPlot(Schema, PlotSection):
    """Base for plotting schemas that refresh MANATI data during normalization."""

    datetime = Quantity(
        type=str,
        shape=['*'],
        description='ISO 8601 acquisition local time, with no inferred timezone.',
    )
    roi_snr = Quantity(
        type=float, shape=['*'], description='ROI signal-to-noise ratio.'
    )
    description = Quantity(type=str, shape=['*'], description='MRI series description.')
    coil = Quantity(type=str, shape=['*'], description='MRI coil identifier.')


m_package.__init_metainfo__()
