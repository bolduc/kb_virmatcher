#!/usr/bin/env python

import os
from pathlib import Path
import subprocess
import logging
import pandas as pd


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

    gtdbtk_res = process_gtdbtk_outputs(output_dir)

    return gtdbtk_res


def process_gtdbtk_outputs(output_dir: Path):

    """
    :param output_dir: (Previously used) output folder for GTDB-Tk results, a bit of a misnomer
    """

    gtdbtk_fns = ['gtdbtk.ar122.summary.tsv',
                  'gtdbtk.bac120.summary.tsv'
                  ]

    gtdbtk_fps = [output_dir / gtdbtk_fn for gtdbtk_fn in gtdbtk_fns]

    gtdbtk_dfs = []
    for gtdbtk_fp in gtdbtk_fps:
        domain = gtdbtk_fp.name.split(".")[1]
        if not gtdbtk_fp.is_file():
            logging.info(f'GTDB-Tk {domain} not found. This may be fine.')
        else:
            # Just need the taxonomy
            with open(gtdbtk_fp, 'r') as gtdbtk_fh:  # I need to know
                for line in gtdbtk_fh:
                    print(line)
            gtdbtk_df = pd.read_csv(gtdbtk_fp, header=0, index_col=False, sep=r"\s+")
            gtdbtk_df['genus'] = gtdbtk_df['classification'].apply(lambda x: x.split(';')[5])
            gtdbtk_df['domain'] = domain

            gtdbtk_dfs.append(gtdbtk_df)

    if len(gtdbtk_dfs) > 1:  # It can't be anything other than 0-2
        gtdbtk_df = pd.concat(gtdbtk_dfs, ignore_index=True)
    else:
        gtdbtk_df = gtdbtk_dfs,

    return gtdbtk_df
