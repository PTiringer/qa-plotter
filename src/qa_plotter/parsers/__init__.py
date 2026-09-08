from nomad.config.models.plugins import ParserEntryPoint


class MRIQAParserEntryPoint(ParserEntryPoint):
    def load(self):
        from qa_plotter.parsers.parser import MRIQAParser

        return MRIQAParser(**self.model_dump())


parser_entry_point = MRIQAParserEntryPoint(
    name='MANATI MRI QA CSV',
    description='Import MANATI ROI SNR measurements grouped by description and coil.',
    mainfile_name_re=r'.*\.csv',
    mainfile_contents_re=r'^\ufeff?datetime,ROI_SNR,Description,Coil\r?\n',
)
