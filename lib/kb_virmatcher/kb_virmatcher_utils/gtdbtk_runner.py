#!/usr/bin/env python

import os
from pathlib import Path
import subprocess
import logging


def run_gtdbtk(input_dir: Path, output_dir: Path, cpu_count):

    """
    Run GTDB-Tk on a directory of sequences in FASTA format.

    :param input_dir: Folder for GTDB-Tk input, consisting of genome-specific FASTA files
    :param output_dir: Folder for GTDB-Tk output, only a few files will be used from it. Everything else will be
        discarded when the job completes
    :param cpu_count: number of available CPUs
    :return:
    """

    gtdbtk_cmd = [
        'gtdbtk',
        'classify_wf',
        '--extension', 'fasta',
        '--genome_dir', str(input_dir),
        '--out_dir', str(output_dir),
        '--pplacer_cpus', '1' if cpu_count <= 4 else str(cpu_count),
        '--cpus', str(cpu_count)]

    logging.info('Starting Command:\n' + ' '.join(gtdbtk_cmd))

    ret = subprocess.run(gtdbtk_cmd, check=True)

    if ret.returncode != 0:
        logging.error(f'There was an issue during GTDB-Tk execution: {ret.stderr}')
        exit(1)

