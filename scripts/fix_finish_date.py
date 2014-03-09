"""Run this script to copy Finish Date from all processes from the stage LIMS
to the production LIMS. It expects a file finish_dates.txt containing the original
finish dates. The format should be, per line:

    "process_id: (run_id, finish_date)", i.e
    "24-8480: ('130423_SN7001298_0135_AH0A9YADXX', datetime.date(2013, 4, 24))"

WARNING: Run this script with caution! And make sure that the file finish_dates.txt
is correctly formated and contains the original Finish Run dates before running
this script in production.
"""
import datetime
import logbook

from logbook import Logger
from argparse import ArgumentParser

from genologics import lims
from genologics.config import BASEURI, USERNAME, PASSWORD
from genologics.entities import Process

log =  Logger("Fix-Finish_date", level=logbook.INFO)

def main(lims, flowcells):
    # Go through all processes, fetch them from production stage, change Finish Date
    # and put the changes
    for p_id, date in flowcells:
        fc_lims = Process(lims, id=p_id)
        log.info("Fetched process {}. Modifying wrong Finish date ({}) with correct " \
                 "Finish Date ({})...".format(p_id, fc_lims.udf['Finish Date'], str(date)))
        fc_lims.udf['Finish Date'] = date
        fc_lims.put()
        log.info('Done')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('finish_date_file', help = 'File with original Finish Dates')
    args = parser.parse_args()

    lims = lims.Lims(BASEURI, USERNAME, PASSWORD)

    flowcells = []
    with open(args.finish_date_file, 'r') as f:
        for line in f:
            #Parse the process id and the Finish Date so it is easier to treat afterwards
            p_id, flowcell = line.split(':')
            #This regex will pick uo yeat, month and day of the Finish Date
            finish_date = flowcell[flowcell.find("e(")+2:flowcell.find(")")]
            finish_date = finish_date.replace(' ', '')
            y, m, d = finish_date.split(',')
            flowcells.append((p_id.lstrip().rstrip(), datetime.date(int(y), int(m), int(d))))
    main(lims, flowcells)
