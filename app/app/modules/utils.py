import csv
import time
import subprocess
from pdfkit import from_file
from pathlib import Path
import re

from datetime import timedelta, timezone, datetime
from os import stat, path
from shutil import copyfile
from pystache import Renderer

# Globals
SECRETS_DIR = 'secrets/'
TEMPLATE_DIR = '../template/'
PUBLIC_DIR = '../static/'
PRIVATE_DIR = '../private/'
TMP_DIR = '../tmp/'
REPORT_DIR = '../report/'
INDEX_FILE = 'index.html'


def check_db():
    """ Check DB and return the last line or False """
    db_path = 'private/iterations.db'
    my_file = Path(db_path)
    if my_file.is_file() and stat(my_file).st_size != 0:
        return subprocess.check_output(['tail', '-1', 'private/iterations.db']).rstrip()
    else:
        return False

def print_csv(dictList):
    """ Print to CSV file """
    with open(PUBLIC_DIR + 'report.csv', mode='w') as report_file:
        fieldnames = ['title', 'state', 'url', 'created_by', 'created_at', 'assignee',
                 'assigned_on', 'delta_triage', 'no_triage', 'delta_res',
                 'late_triage', 'labels', 'comments','sol_fine',
                 'last_comment', 'last_comment_by',
                'last_update', 'last_update_by', 'last_update_at', 'closed_at']
        writer = csv.DictWriter(report_file, fieldnames=fieldnames)
        writer.writeheader()
        for d in dictList:
            writer.writerow(d)

def tpl_render(dict_list, no_triage, late_triage, sol_fine, since):
    """ Render and save to tmp """
    renderer = Renderer()
    match = re.search(r'\d{4}-\d{2}-\d{2}', since) 
    since = datetime.strptime(match.group(), '%Y-%m-%d').date()
    output = renderer.render_path(
        'template/index.mustache', {
            'lista' : dict_list,
            'no-triage' : no_triage,
            'late-triage' : late_triage,
            'sol-fine' : sol_fine,
            'start-date' : since,
            'end-date' :  time.strftime("%Y-%m-%d")
        })

    my_path = path.abspath(path.dirname(__file__))
    with open(path.join(my_path, TMP_DIR + "index.html"), 'w') as html_file:
        html_file.write(output)
        html_file.close()

def move_files():
    """ Backup old files, move new index to public folder """
    name = check_db()
    my_path = path.abspath(path.dirname(__file__))
    # Backup old
    if name != False:
        name = str(name, 'utf-8')
        final_name = PRIVATE_DIR + name + '.html'
        original_path = path.join(my_path, PUBLIC_DIR + INDEX_FILE)
        dest_path = path.join(my_path, final_name)
        copyfile(original_path, dest_path)

     # Copy new
    new_index = path.join(my_path, TMP_DIR + INDEX_FILE) 
    dest_path = path.join(my_path, PUBLIC_DIR + INDEX_FILE) 
    copyfile(new_index, dest_path)

def export_pdf():
    """ Function to export the HTML file to PDF """
    if check_db() != False:
        name = str(name, 'utf-8')
        from_file(dest_path, REPORT_DIR + name)


