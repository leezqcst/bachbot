import click
import subprocess

from music21 import environment

from bach_chorales import prepare_bach_chorales_mono
from constants import *


@click.group()
def cli():
    us = environment.UserSettings()
    # ~/.music21rc should be edited to support using musescore for score.show()
    # us.create()
    pass


@click.command()
@click.argument('files', nargs=-1, required=True)
@click.option('-o', '--output', type=click.File('w+'), default=SCRATCH_DIR + '/concat_corpus.txt')
def concatenate_corpus(files, output):
    """Concatenates individual files together into single corpus.

    Try `bachbot concatenate_corpus scratch/*.utf`.
    """
    for fp in files:
        with open(fp, 'rb') as fd:
            output.write(START_DELIM + '\n' + fd.read() + '\n' + END_DELIM + '\n')

@click.command()
@click.option('-i', '--infile', type=click.File('rb'), default=SCRATCH_DIR + '/concat_corpus.txt')
@click.option('-o', '--outdir', type=click.Path(exists=True), default=SCRATCH_DIR)
def make_h5(infile, outdir):
    """Encodes corpus for torch-rnn."""
    fileName=os.path.splitext(os.path.basename(infile.name))[0]

    # preprocess data (tokenize store in hdf5)
    infile_path = os.path.abspath(infile.name)
    print 'Processing corpus at: ' + infile_path
    print 'Outputting to: ' + outdir + '/' + fileName + '{h5,json}'
    subprocess.call(' '.join([
        'python',
        '~/torch-rnn/scripts/preprocess.py',
        '--input_txt', infile_path,
        '--output_h5', outdir + '/' + fileName + '.h5',
        '--output_json', outdir + '/' + fileName + '.json'
    ]), shell=True)

@click.command()
def train():
    """Trains torch-rnn model. Alias to bachbot/scripts/torchrnn/train.zsh."""
    subprocess.call(BACHBOT_DIR + '/scripts/torchrnn/train.zsh')

@click.command()
@click.argument('checkpoint', type=click.Path(exists=True), required=True)
@click.option('-t', '--temperature', type=float, default=0.9)
def sample(checkpoint, temperature):
    """Samples torch-rnn model. Calls bachbot/scripts/torchrnn/sample.zsh."""
    subprocess.call(
    BACHBOT_DIR + '/scripts/torchrnn/sample.zsh {0} {1} {2}'.format(checkpoint, temperature, START_DELIM),
    shell=True)

# instantiate the CLI
map(cli.add_command, [
    prepare_bach_chorales_mono,
    make_h5,
    train,
    sample
])
