#!/usr/bin/env python3
"""
src/blast-gcp.py - See DESC constant below

Author: Christiam Camacho (christiam.camacho@gmail.com)
Created: Sun Nov  3 07:34:23 2019
"""
import argparse
#import json
#import time
from ncbi_cloudblast_api.api_client import APIClient
from Bio import SeqIO
from io import StringIO
import logging
import configparser

VERSION = '0.1'
DFLT_LOGFILE = 'blast-gcp.log'
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

    client_ip = config['blast-gcp']['service-address']
    logging.info(f"Connected to BLAST-GCP on {client_ip}")
    client = APIClient(client_ip)
    print(client)

    # Sanity check: make sure the BLASTDB requested is supported
    supported_dbs = [ 'nt', 'nt_v5' ]
    #supported_dbs = client.dblist()
    #print (f"Database names: {[db.name for db in res.db]}")
    #found = any([args.dbname in db.name for db in res.db])
    found = any([args.dbname in db for db in supported_dbs])
    if not found:
        print(f"{args.dbname} is not supported by the BLAST-GCP system at {client_ip}")
        return 1

    queries = None
    with args.query as f:
        queries = f.read()

    #descriptions_and_job_ids = [(s.description,
    #                         client.submit(verbatim_seq=str(s.seq)))
    #                         for s in SeqIO.parse(StringIO(queries), "fasta")]
    #descriptions_and_results = [(description,
    #                         client.wait(job_id))
    #                         for description, job_id in descriptions_and_job_ids]
    # This doesn't work
    #res = client.search(verbatim_query=queries)

    rids = [ client.submit(verbatim_seq=str(s.seq)) for s in SeqIO.parse(StringIO(queries), "fasta") ]
    results = [ client.wait(r) for r in rids ]
    for r in results:
        if len(r.errors):
            print('Search job finished with status: FAILED')
            for error in r.errors:
                print(f'Error message: {error}')
        else:
            df = res.as_dataframe()["qaccver", "saccver", "pident", "length", "mismatch", "gapopen", "qstart", "qend", "sstart", "send", "evalue", "bitscore"]
            print(df.to_csv(sep="\t"))


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

