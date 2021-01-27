#!/usr/bin/env python

import os
from pathlib import Path
import subprocess
import logging
import pandas as pd


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
                      '--cpu-count', host_cpu_count, '-o', output_dir]

    # VirMatcher -v /fs/project/PAS1117/ben/test_VirMatcher/selected_isog_contigs.VS_1245.min5k_95-80.fna
    # --archaea-host-dir /fs/project/PAS1117/ben/test_VirMatcher/ArchaeaLite/
    # --archaea-taxonomy /fs/project/PAS1117/ben/test_VirMatcher/GTDB_arc.tsv
    # --bacteria-taxonomy /fs/project/PAS1117/ben/test_VirMatcher/GTDB_bac.tsv
    #  /fs/project/PAS1117/ben/test_VirMatcher/BacteriaLite/
    # -o VirMatcher_Final_Installed
