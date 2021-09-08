#!/usr/bin/env python

from pathlib import Path
import subprocess
import logging


def run_virmatcher(gtdbtk_indir: Path, gtdbtk_outdir: Path, virus_fp: Path, host_cpu_count, output_dir: Path):
    """

    Note - does not require decoy virus info because it is now embedded in package
    :param gtdbtk_indir:
    :param gtdbtk_outdir:
    :param virus_fp:
    :param host_cpu_count:
    :param output_dir:
    :return:
    """
    virmatcher_cmd = ['VirMatcher', '--preparer', '-v', virus_fp,
                      '--gtdbtk-in-dir', gtdbtk_indir, '--gtdbtk-out-dir', gtdbtk_outdir,
                      '--threads', str(host_cpu_count), '-o', output_dir, '--python-aggregator']

    ret = subprocess.run(virmatcher_cmd, check=True)

    if ret.returncode != 0:
        logging.error(f'There was an issue during VirMatcher execution: {ret.stderr}')
        exit(1)
