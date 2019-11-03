#!/usr/bin/env python3
"""
src/web-blast.py - See DESC constant below

Documentation: https://biopython-tutorial.readthedocs.io/en/latest/notebooks/07%20-%20Blast.html

Author: Christiam Camacho (christiam.camacho@gmail.com)
Created: Sun Nov  3 09:34:23 2019
"""
import argparse
from Bio import SeqIO
from io import StringIO
from Bio.Blast import NCBIWWW
import logging
import configparser
from contextlib import closing

VERSION = '0.1'
DFLT_LOGFILE = 'web-blast.log'
DFLT_DB = 'nt'
DFLT_CFG = 'etc/config.ini'
DESC = r"""Program to submit BLAST searches to BLAST-GCP system"""


def main():
    """ Entry point into this program. """
    parser = create_arg_parser()
    args = parser.parse_args()
    config_logging(args)

    config = configparser.ConfigParser()
    config.read(args.cfg)

    queries = None
    with args.query as f:
        queries = f.read()
    
    result_handle = NCBIWWW.qblast('blastn', args.dbname, queries, megablast=True, format_type="Tabular")
    if args.ami:
        result_handle = NCBIWWW.qblast('blastn', args.dbname, queries, megablast=True, base_url=config['blast-ami']['service-address'], format_type="Tabular")
    logging.info("Connected to NCBI BLAST web service")

    with closing(result_handle), result_handle:
        print(result_handle.read())

    return 0


def create_arg_parser():
    """ Create the command line options parser object for this script. """
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument("query", type=argparse.FileType('r'))
    parser.add_argument("-db", default=DFLT_DB, dest="dbname",
                        help="BLAST database name to search, default: " + DFLT_DB)
    parser.add_argument("-cfg", default=DFLT_CFG,
                        help="Config file path, default: " + DFLT_CFG)
    parser.add_argument("-logfile", default=DFLT_LOGFILE,
                        help="Default: " + DFLT_LOGFILE)
    parser.add_argument("-loglevel", default='INFO',
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + VERSION)
    parser.add_argument("-ami", action='store_true',
                        help="Send BLAST searches to a running BLAST AMI (as configured in the config file)")
    return parser


def config_logging(args):
    if args.logfile == 'stderr':
        logging.basicConfig(level=str2ll(args.loglevel),
                            format="%(asctime)s %(message)s")
    else:
        logging.basicConfig(filename=args.logfile, level=str2ll(args.loglevel),
                            format="%(asctime)s %(message)s", filemode='w')
    logging.logThreads = 0
    logging.logProcesses = 0
    logging._srcfile = None


def str2ll(level):
    """ Converts the log level argument to a numeric value.

    Throws an exception if conversion can't be done.
    Copied from the logging howto documentation
    """
    retval = getattr(logging, level.upper(), None)
    if not isinstance(retval, int):
        raise ValueError('Invalid log level: %s' % level)
    return retval


if __name__ == "__main__":
    import sys, traceback
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

