#%% Imports
from pathlib import Path
import os
import argparse

def get_subjects(data_dir: Path):
    subjects = [subject.name for subject in data_dir.iterdir() if subject.is_dir()]
    # remove fsaverage
    subjects = [subject for subject in subjects if subject != 'fsaverage']
    return subjects

def get_asegstats2table_cmd(subjects: list, output_dir: Path, name: str):
    subjects = ' '.join(subjects)
    output_file = output_dir / f"aseg-stats_{name}.txt"
    cmd = f"asegstats2table --subjects {subjects} --meas volume --skip --tablefile {output_file}"
    return cmd

def get_aparcstats2table_cmd(subjects: list, output_dir: Path, hemi: str, name: str):
    subjects = ' '.join(subjects)
    output_file = output_dir / f"aparc-stats_{hemi}_{name}.txt"
    cmd = f"aparcstats2table --subjects {subjects} --hemi {hemi} --meas volume --skip --tablefile {output_file} --parcid-only"
    return cmd

def setup_env(subjects_dir: Path):
    os.environ['SUBJECTS_DIR'] = str(subjects_dir)

def run(cmd: str):
    os.system(cmd)

def asegstats2table(args: argparse.Namespace):
    subjects_dir = Path(args.subjects_dir)
    output_dir = Path(args.output_dir)
    name = args.name
    subjects = get_subjects(subjects_dir)
    cmd = get_asegstats2table_cmd(subjects, output_dir, name)
    setup_env(subjects_dir)
    run(cmd)
    pass

def aparcstats2table(args: argparse.Namespace):
    subjects_dir = Path(args.subjects_dir)
    output_dir = Path(args.output_dir)
    name = args.name
    subjects = get_subjects(subjects_dir)
    cmd_rh = get_aparcstats2table_cmd(subjects, output_dir, hemi='rh', name=name)
    cmd_lh = get_aparcstats2table_cmd(subjects, output_dir, hemi='lh', name=name)
    setup_env(subjects_dir)
    run(cmd_rh)
    run(cmd_lh) 
    pass

def main():
    parser = argparse.ArgumentParser(description='Run asegstats2table and aparcstats2table')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Create subparser for asegstats2table
    aseg_parser = subparsers.add_parser('asegstats2table', help='Convert aseg.stats file to a table')
    aseg_parser.add_argument('subjects_dir', help='Path to the FS subject directory')
    aseg_parser.add_argument('output_dir', help='Path to the output table file')
    aseg_parser.add_argument('--name', help='Add name to output')
    aseg_parser.set_defaults(func=asegstats2table)

    # Create subparser for aparcstats2table
    aparc_parser = subparsers.add_parser('aparcstats2table', help='Convert aparc.stats file to a table')
    aparc_parser.add_argument('subjects_dir', help='Path to the FS subject directory')
    aparc_parser.add_argument('output_dir', help='Path to the output table file')
    aparc_parser.add_argument('--name', help='Add name to output')
    aparc_parser.set_defaults(func=aparcstats2table)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    # example usage: python fs_get_summary_stats.py asegstats2table /proc_data1/brainage/Cimbi_database/Cimbi36/FS_SUBJECTS /proc_data1/brainage/Cimbi_database/Cimbi36/FS_SUBJECTS --name cimbi
    # example usage: python fs_get_summary_stats.py aparcstats2table /proc_data1/brainage/Cimbi_database/Cimbi36/FS_SUBJECTS/ /proc_data1/brainage/Cimbi_database/Cimbi36/FS_SUBJECTS --name cimbi
    main()

