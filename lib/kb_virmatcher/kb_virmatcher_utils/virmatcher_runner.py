#!/usr/bin/env python

from pathlib import Path
import subprocess
import logging


def run_virmatcher(archaea_dir: Path, archaea_tax: Path, bacteria_dir: Path, bacteria_tax: Path,
                   virus_fp: Path, host_cpu_count, output_dir: Path):
    """

    Note - does not require decoy virus info because it is now embedded in package
    :param archaea_dir:
    :param archaea_tax:
    :param bacteria_dir:
    :param bacteria_tax:
    :param virus_fp:
    :param host_cpu_count:
    :param output_dir:
    :return:
    """
    virmatcher_cmd = ['VirMatcher', '-v', virus_fp,
                      '--archaea-host-dir', archaea_dir, '--archaea-taxonomy', archaea_tax,
                      '--bacteria-host-dir', bacteria_dir, '--bacteria-taxonomy', bacteria_tax,
                      '--threads', str(host_cpu_count), '-o', output_dir, '--python-aggregator']

    ret = subprocess.run(virmatcher_cmd, check=True)

    if ret.returncode != 0:
        logging.error(f'There was an issue during VirMatcher execution: {ret.stderr}')
        exit(1)
