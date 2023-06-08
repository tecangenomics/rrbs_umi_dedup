"""
Code to process RRBS reads with UMIs sequenced by MGI
Requires:
    python 3.x
    docker
"""
import argparse
import dataclasses
import glob
import os
import subprocess
import sys



def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--genome',
                        help='Path to reference genome folder')
    parser.add_argument('-r', '--reads',
                        help='Reads directory')
    parser.add_argument('o', '--out',
                        help='Output directory')
    parser.add_argument('--index',
                        help='Set flag if reference needs to be indexed',
                        action='store_true')
    parser.add_argument('--pull_docker',
                        help='Pull required docker containers if not yet done',
                        action='store_true')
    return parser.parse_args()


@dataclasses.dataclass
class RRBS_analysis:
    r1: str # read 1 filename (not path)
    r2: str # read 2 filename (not path)
    reference: str # path to reference genome folder
    read_path: str # path to reads directory
    result_path: str # output directory to hold all results
    pipeline_path: str = os.path.dirname(os.path.abspath(__file__))

    def __post_init__(self):
        self.r1 = self.r1.split('/')[-1] # in case a path is provided
        self.r2 = self.r2.split('/')[-1] # in case a path is provided
        #self.sample_name = ''.join(''.join(self.r1.split('R1')).split('.')[:-1])
        self.pipeline_status = self.run_pipeline()

    def __rename_file(self, path: str, name: str, suffix: str) -> str:
        """
        Creates a new file name + path + extension
        Input:
            path: the new path of the file
            name: the file name; will be basenamed, so path doesn't matter
            suffix: the new file suffx e.g. '_suffix.extension'
        """
        base_name = ''.join(os.path.basename(name).split('.')[:-1])
        return path + '/' + base_name + suffix

    def __extract_umi(self):
        """
        Step_1: Moves umi from read 2 to new fastq file
        Change options in source code if needed
        Input:
            r1, r2, sample_name
        New Attributes
            r2_new: path to the R2 file without umi
            umi_fq: path to the umi file
        """
        print('Starting step 1: umi extraction')
        # initialzie output directory for this step
        step_1_output = 's1_extract-umi'
        os.makedirs(self.result_path + '/' + step_1_output, exist_ok=True)
        # create new attributes for the class
        self.re_new = self.__rename_file(step_1_output, self.r2, '_umi-removed.fq')
        self.umi_fq = self.__rename_file(''.join(self.r1.split('R1')), '_umi.fq')
        # run command
        bash_script = ['./src/shift_bases.sh']
        mount_directories = [self.pipeline_path, self.result_path, self.read_path]
        docker_inputs = [self.r2, self.umi_fq, self.r2_new]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 1: umi extraction')
        return

    def __trim_adapter_diversity(self):
        """
        Step_2: Trim adapters
        Change options in source code if needed
        Input:
            r1, r2_new
        New Attributes:
            r1_trimmed: trimmed r1 file
            r2_trimmed: trimmed r2 file
        """
        # initialize output directory
        print('Starting step2: trimming reads')
        step_2_output = 's2_trim_adapter_diversity'
        os.makedirs(self.result_path + '/' + step_2_output, exist_ok=True)
        # do ilmn adapter trimming
        print('\tStarting step 2a: trimming universal adapters')
        bash_script = ['./src/trim_adapter_ilmn.sh']
        mount_directories = [self.read_path, self.result_path]
        docker_inputs = [step_2_output, self.r1, self.r2_new]
        result_trim_ilmn = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result_trim_ilmn.returncode != 0:
            sys.exit('\tFailed step 2a: trimming universal adapter')
        r1_trim_ilmn = self.__rename_file(step_2_output, self.r1, '_val_1.fq')
        r2_trim_ilmn = self.__rename_file(step_2_output, self.r2_new, '_val_2.fq')
        # do diversity adapter trimming
        print('\tStarting step2b: trimming diversity sequence')
        bash_script = ['./src/trim_adapter_diversity.sh']
        mount_directories = [self.pipeline_path, self.result_path]
        docker_inputs = [r1_trim_ilmn, r2_trim_ilmn]
        result_trim_diverse = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result_trim_diverse.returncode != 0:
            sys.exit('\tFailed step2a: trimming diversity sequence')
        # create_new attributes for the class
        self.r1_trimmed = self.__rename_file(step_2_output, r1_trim_ilmn, '_trimmed.fq')
        self.r2_trimmed = self.__rename_file(step_2_output, r2_trim_ilmn, '_trimmed.fq')
        return
    
    def __add_umi(self):
        """
        Adds UMI back to the beginning of R1
        Change options in source code if needed
        Input:
            self.r1_trimmed: destination
            self.umi_fq: source sequence
        New Attributes:
            self.r1_umi
        """
        print('Starting step 3: add umi to R1')
        step_3_output = 's3_add_umi'
        os.makedirs(self.result_path + '/' + step_3_output, exist_ok=True)
        # move umis now
        self.r1_umi = self.__rename_file(step_3_output, self.r1_trimmed, '_umi-added.fq')
        bash_script = ['./src/move_back_umi.sh']
        mount_directories = [self.pipeline_path, self.result_path]
        docker_inputs = [self.umi_fq, self.r1_trimmed, self.r1_umi]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 3: add umi to R1')
        return
    
    def __umi_extract(self):
        """
        Runs umi-tools to extract UMI
        Change options in source code if needed
        Input:
            self.r1_umi
            self.r2_trimmed
        New Attributes
            self.r1_umi_extract
            self.r2_umi_extract
        """
        print('Starting step 4: run umi extract')
        step_4_output = 's4_umi_extract'
        os.makedirs(self.result_path + '/' + step_4_output, exist_ok=True)
        # create attributes to feed into command
        self.r1_umi_extract = self.__rename(step_4_output, self.r1_umi, '_umi-extract.fq')
        self.r2_umi_extract = self.__rename(step_4_output, self.r1_umi, '_umi-extract.fq')
        # run umi extract now
        bash_script = ['./src/umi_extract.sh']
        mount_directories = [self.result_path]
        docker_inputs = [self.r1_umi, self.r2_trimmed, self.r1_umi_extract, self.r2_umi_extract]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 4: umi extract')
        return

    def __run_bismark_alignment(self):
        """
        Runs the bismark aligner + samtools sort + bam indexing
        Input:
            self.r1_umi
            self.r2_trimmed
        Output:
            bam file
            sorted bam file
            bam index: to be a new attribute
        """
        print('Starting step 5: align with bismark')
        step_5_output = 's5_bismark_align'
        os.makedirs(self.result_path + '/' + step_5_output)
        # run bismark alignment
        print('\tStarting step 5a: alignment')
        bash_script = ['./src/bismark_align.sh']
        mount_directories = [self.result_path, self.reference]
        docker_inputs = [step_5_output, self.r1_umi_extract, self.r2_umi_extract]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 5a: align with bismark')
        bam = self.__rename_file(step_5_output, self.r1_umi_extract, '_bismark_bt2_PE.bam')
        # run samtools sort
        print('\tStarting step 5b: sort bam file')
        bash_script = ['./src/samtools_sort.sh']
        mount_directories = [self.result_path]
        docker_inputs = [bam]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 5b: sort bam file')
        self.bam_sorted = self.__rename_file(step_5_output, bam, '_sorted.bam')
        # run samtools index
        print('\tStarting step 5c: index bam file')
        bash_script = ['./src/samtools_index.sh']
        mount_directories = [self.result_path]
        docker_inputs = [self.bam_sorted]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 5c: index bam file')
        pass

    def __run_deduplication(self):
        """
        Runs teh deduplication step
        Input:
            self.bam_sorted
        Output:
            Final, deduplicated bam file
        """
        print('Starting step 6: deduplicate')
        step_6_output = 's6_deduplicate_bam'
        os.makedirs(self.result_path + '/' + step_6_output)
        # run deduplication
        bash_script = ['./src/umi_dedup.sh']
        mount_directories = [self.result_path]
        docker_inputs = [step_6_output, self.bam_sorted]
        result = subprocess.run(bash_script + mount_directories + docker_inputs)
        if result.returncode != 0:
            sys.exit('\tFailed step 6: deduplicate file')

    def run_pipeline(self):
        """
        Runs the pipeline using all defined functions
        """
        self.__extract_umi()
        self.__trim_adapter_diversity()
        self.__add_umi()
        self.__umi_extract()
        self.__run_bismark_alignment()
        self.__run_deduplication()
        return
    

def pull_docker_images():
    """
    Runs the command to pull docker images
    """
    print('Pulling required docker images')
    subprocess.call(['/.src/pull_docker_container.sh'])
    return


def bismark_index_genome(reference_dir: str) -> None:
    """
    Takes the reference folder and index with Bismark
    Inputs:
        reference_dir: directory where reference genome is located
    Creates:
        Bisulfite Genome Indices for the reference
    """
    print(f'Indexing {reference_dir} with bismark')
    subprocess.call(['./src/bismark_index.sh', reference_dir])
    print('Indexing complete')
    return


def main():
    # get arguments
    args = get_arguments()
    # pull dockers if needed
    if args.pull_docker:
        pull_docker_images()
    # index genome if needed
    if args.index:
        bismark_index_genome()
    # perform analysis on per sample basis
    for r1 in glob.glob(args.reads + '/*R1*'):
        r2 = r1.split('R1')[0] + 'R2' + r1.split('R1')[1]
        analysis = RRBS_analysis(r1, r2, args.reference, args.reads, args.out)
        print(analysis.pipeline_status)
    return


if __name__ == '__main__':
    main()