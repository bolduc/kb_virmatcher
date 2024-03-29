'''
Miscellaneous functions to handle kb_VirMatcher that do not fall within GTDB-Tk or VirMatcher proper
'''

from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils
from installed_clients.WorkspaceClient import Workspace
from installed_clients.KBaseReportClient import KBaseReport
import pandas as pd
from pprint import pprint
import os
import uuid
import logging
from Bio import SeqIO
import shutil
from pathlib import Path
from string import Template
from pyparsing import Literal, SkipTo


def process_kbase_objects(host_ref, virus_ref, shared_folder, callback, workspace, token):
    """
    Convert KBase object(s) into usable files for VirMatcher
    :param host_ref: Putative host / microbial genomes with KBase '#/#/#' used to describe each object
    :param virus_ref: Viral genomes with KBase '#/#/#' used to describe each object
    :param shared_folder: KBase job node's "working" directory, where actual files exist
    :param callback:
    :param workspace: Workspace name
    :param token: Job token
    :return:
    """

    dfu = DataFileUtil(callback, token=token)

    ws = Workspace(workspace, token=token)

    mgu = MetagenomeUtils(callback, token=token)

    au = AssemblyUtil(callback, token=token)

    # Need to determine KBase type in order to know how to properly proceed
    host_type = ws.get_object_info3({'objects': [{'ref': host_ref}]})['infos'][0][2].split('-')[0]
    virus_type = ws.get_object_info3({'objects': [{'ref': virus_ref}]})['infos'][0][2].split('-')[0]

    logging.info(f'Potential hosts identified as: {host_type}')
    logging.info(f'Viruses identified as: {virus_type}')

    # Create new directory to house virus and host files
    host_dir = Path(shared_folder) / 'host_files'
    if not host_dir.exists():
        os.mkdir(host_dir)

    host_count = 0

    if host_type == 'KBaseGenomeAnnotations.Assembly':  # No info about individual genomes, so treat each as organism
        host_fps = au.get_assembly_as_fasta({'ref': host_ref})['path']  # Consists of dict: path + assembly_name

        logging.info(f'Identified {host_type}. Each sequence will be treated as a separate organism.')

        records = SeqIO.parse(host_fps, 'fasta')

        for record in records:
            host_count += 1
            tmp_fp = host_dir / f'{record.id}.fasta'  # TODO Illegal filenames?
            SeqIO.write([record], tmp_fp, 'fasta')

    elif host_type == 'KBaseGenomes.Genomes':  # TODO Genomes?!
        genome_data = ws.get_objects2({'objects': [
            {'ref': host_ref}]})['data'][0]['data']
        genome_data.get('contigset_ref') or genome_data.get('assembly_ref')

    # elif host_type == 'KBaseSets.GenomeSet'

    elif host_type == 'KBaseSets.AssemblySet':
        obj_data = dfu.get_objects({'object_refs': [host_ref]})['data'][0]

        for subobj in obj_data['data']['items']:
            host_fp = au.get_assembly_as_fasta({'ref': subobj['ref']})['path']

            if os.path.splitext(host_fp)[-1] != 'fasta':
                # Ensure extension always = fasta
                target_fn = os.path.splitext(os.path.basename(host_fp))[0].strip('_') + '.fasta'
            else:
                target_fn = os.path.basename(host_fp).strip('_')

            shutil.copyfile(host_fp, host_dir / target_fn)
            host_count += 1

    elif host_type == 'KBaseMetagenomes.BinnedContigs':  # This is what we want!
        host_kbase_dir = mgu.binned_contigs_to_file(
            {'input_ref': host_ref, 'save_to_shock': 0})['bin_file_directory']  # Dict of bin_file_dir and shock_id

        for (dirpath, dirnames, fns) in os.walk(host_kbase_dir):  # Dirnames = all folders under dirpath
            for fn in fns:
                if os.path.splitext(fn)[-1] != 'fasta':
                    fn = os.path.splitext(fn)[0] + '.fasta'
                fp = Path(dirpath) / fn
                shutil.copy(fp, host_dir)
                host_count += 1

    else:
        raise ValueError(f'{host_type} is not supported.')

    logging.info(f'{host_count} potential host genomes were identified.')

    virus_count = 0

    if virus_type == 'KBaseGenomeAnnotations.Assembly':
        virus_fps = au.get_assembly_as_fasta({'ref': virus_ref})['path']

        records = SeqIO.parse(virus_fps, 'fasta')
        virus_count = len(list(records))

        # for record in records:
        #     virus_count += 1
            # tmp_fp = virus_dir / f'{record.id}.fasta'
            # SeqIO.write([record], tmp_fp, 'fasta')

    else:
        raise ValueError(f'{virus_type} is not supported.')

    logging.info(f'{virus_count} potential viral genomes were identified.')

    # TODO Do we even need any of this data? We don't care about what the sequences are called

    # host_data = dfu.get_objects({'object_refs': [host_ref]})['data'][0]
    # virus_data = dfu.get_objects({'object_refs': [virus_ref]})['data'][0]

    return host_dir, virus_fps


def generate_report(callback_url, token, workspace_name, shared_folder: Path, virmatcher_output: Path):
    """
    :param callback_url:
    :param token: Job token
    :param workspace_name: Workspace name
    :param shared_folder: KBase working directory on the node, used to save the HTML file
    :param virmatcher_output: VirMatcher proper final results directory, should have the summary file
    :return:
    """
    html_template = Template("""<!DOCTYPE html>
    <html lang="en">
      <head>

        <link href="https://netdna.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.datatables.net/1.10.22/css/jquery.dataTables.min.css" rel="stylesheet">
        <link href="https://cdn.datatables.net/buttons/1.5.2/css/buttons.dataTables.min.css" rel="stylesheet">

        <link href="https://cdn.datatables.net/searchpanes/1.2.0/css/searchPanes.dataTables.min.css" rel="stylesheet">
        <link href="https://cdn.datatables.net/select/1.3.1/css/select.dataTables.min.css" rel="stylesheet">

        <script src="https://code.jquery.com/jquery-3.5.1.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.4/js/dataTables.buttons.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.4/js/buttons.flash.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js" type="text/javascript"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.4/js/buttons.html5.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.4/js/buttons.print.min.js" type="text/javascript"></script>

        <script src="https://cdn.datatables.net/searchpanes/1.2.0/js/dataTables.searchPanes.min.js" type="text/javascript"></script>
        <script src="https://cdn.datatables.net/select/1.3.1/js/dataTables.select.min.js" type="text/javascript"></script>

        <style>
        tfoot input {
            width: 100%;
            padding: 3px;
            box-sizing: border-box;
        }
        </style>

      </head>

      <body>

        <div class="container">
          <div>
            ${html_table}
          </div>
        </div>

        <script type="text/javascript">
          $$(document).ready(function() {
            $$('#my_id tfoot th').each( function () {
              var title = $$(this).text();
              $$(this).html( '<input type="text" placeholder="Search '+title+'" />' );
            });

            var table = $$('#my_id').DataTable({
              buttons: [
                'copy', 'csv', 'excel', 'pdf', 'print'],
              scrollX: true,
              dom: 'lBfrtip'  //P to B disables panes
            });

            table.columns().every( function () {
              var that = this;

              $$( 'input', this.footer() ).on( 'keyup change', function () {
                if ( that.search() !== this.value ) {
                  that
                  .search( this.value )
                  .draw();
                }
              });
            } );
          } );
        </script>

      </body>
    </html>""")

    report = KBaseReport(callback_url, token=token)
    dfu = DataFileUtil(callback_url, token=token)

    virmatcher_fp = virmatcher_output / 'VirMatcher_Summary_Predictions.tsv'

    virmatcher_df = pd.read_csv(virmatcher_fp, header=0, index_col=None, delimiter='\t')

    # Set column ordering
    order = [
        'Original Viral population',
        'Original Host',
        'Final_score',
        'CRISPR score',
        'Prophage blast score',
        'WIsH score',
        'Number of CRISPR matches',
        'Max number of end mismatches detected in any CRISPR spacer',
        'Prophage blast percent identity',
        'Prophage blast viral contig coverage',
        'tRNA match',
        'Max number of end mismatches detected in host tRNA',
        'Non-promiscuous tRNA match score',
        'WIsH p-value',
        # 'LogLikelihood',
        'Viral population',
        'Predicted host',
    ]
    order = [ele for ele in order if ele in virmatcher_df.columns.tolist()]  # Some may not exist!
    virmatcher_df = virmatcher_df[order]

    html = virmatcher_df.to_html(index=False, classes='my_class table-striped" id = "my_id')

    # Need to file write below
    direct_html = html_template.substitute(html_table=html)

    # Find header so it can be copied to footer, as dataframe.to_html doesn't include footer
    start_header = Literal("<thead>")
    end_header = Literal("</thead>")

    text = start_header + SkipTo(end_header)

    new_text = ''
    for data, start_pos, end_pos in text.scanString(direct_html):
        new_text = ''.join(data).replace(' style="text-align: right;"', '').replace('thead>',
                                                                                    'tfoot>\n  ') + '\n</tfoot>'

    # Get start and end positions to insert new text
    end_tbody = Literal("</tbody>")
    end_table = Literal("</table>")

    insertion_pos = end_tbody + SkipTo(end_table)

    final_html = ''
    for data, start_pos, end_pos in insertion_pos.scanString(direct_html):
        final_html = direct_html[:start_pos + 8] + '\n' + new_text + direct_html[start_pos + 8:]

    output_dir = shared_folder / str(uuid.uuid4())

    os.mkdir(output_dir)

    html_fp = output_dir / 'index.html'

    with open(html_fp, 'w') as html_fh:
        html_fh.write(final_html)

    report_shock_id = dfu.file_to_shock({
        'file_path': str(output_dir),
        'pack': 'zip'
    })['shock_id']

    html_report = [{
        'shock_id': report_shock_id,
        'name': 'index.html',
        'label': 'index.html',
        'description': 'Summary report for VirMatcher'
    }]

    report_params = {'message': 'Basic message to show in the report',
                     'workspace_name': workspace_name,
                     'html_links': html_report,
                     'direct_html_link_index': 0,
                     'report_object_name': f'VirMatcher_report_{str(uuid.uuid4())}',
                     }

    report_output = report.create_extended_report(report_params)

    return report_output
