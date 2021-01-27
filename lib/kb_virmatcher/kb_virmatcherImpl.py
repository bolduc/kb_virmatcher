# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
from pathlib import Path
import psutil

from kb_virmatcher.kb_virmatcher_utils.virmatcher_utils import process_kbase_objects, process_gtdbtk, generate_report
from kb_virmatcher.kb_virmatcher_utils.gtdbtk_runner import run_gtdbtk
from kb_virmatcher.kb_virmatcher_utils.virmatcher_runner import run_virmatcher
#END_HEADER


class kb_virmatcher:
    '''
    Module Name:
    kb_virmatcher

    Module Description:
    A KBase module: kb_virmatcher
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/bolduc/kb_virmatcher.git"
    GIT_COMMIT_HASH = "fc3d276ccf74ea01be3123e4e3d80bb3babc69d4"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = Path(config['scratch'])
        self.ws_url = config['workspace-url']
        alt_cpu = psutil.cpu_count(logical=False)
        self.cpus = alt_cpu if alt_cpu < 32 else 32
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass

    def run_kb_virmatcher(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_virmatcher

        logging.info('Getting input file parameters from KBase workspace for GTDB-Tk...')

        virus_ref = params.get('viral_genomes')
        if type(virus_ref) != str:
            raise ValueError('input_object_ref is required and must be a string')

        host_ref = params.get('host_genomes')
        if type(host_ref) != str:
            raise ValueError('input_object_ref is required and must be a string')

        logging.info('Processing input files')
        host_dir, virus_fp = process_kbase_objects(host_ref, virus_ref,
                                                   self.shared_folder,
                                                   self.callback_url, self.ws_url, ctx['token'])

        logging.info('Running GTDB-Tk classify...')
        gtdbtk_outdir = self.shared_folder / 'gtdbtk_output'
        gtdbtk_df = run_gtdbtk(host_dir, gtdbtk_outdir, self.cpus)

        logging.info('Parsing GTDB-Tk results and passing to VirMatcher')
        # Convert the dataframe and host files into the appropriate archaea/bacteria folder with taxonomy-formatted
        archaea_dir, archaea_fp, bacteria_dir, bacteria_fp = process_gtdbtk(host_dir, self.shared_folder, gtdbtk_df)

        logging.info('Running VirMatcher')
        virmatcher_dir = self.shared_folder / 'virmatcher_output'
        run_virmatcher(archaea_dir, archaea_fp, bacteria_dir, bacteria_fp, virus_fp, self.cpus, virmatcher_dir)

        logging.info('VirMatcher complete, sending results to KBase workspace')
        report_info = generate_report(self.callback_url, ctx['token'], self.ws_url, self.shared_folder, virmatcher_dir)

        report_output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_kb_virmatcher

        # At some point might do deeper type checking...
        if not isinstance(report_output, dict):
            raise ValueError('Method run_kb_virmatcher return value ' +
                             'output is not type dict as required.')
        # return the results
        return [report_output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
