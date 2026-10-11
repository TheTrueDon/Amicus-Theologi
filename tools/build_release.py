"""Reproducible source ZIP build; no private user files or downloaded corpora."""
import argparse
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={'.git','.venv','__pycache__','.pytest_cache','node_modules'}
SKIP_SUFFIXES={'.pyc','.sqlite3','.db','.zip','.log'}
SKIP_NAMES={'amicus-theologi-launcher.sh','.env'}


def build(output):
    output=Path(output).resolve()
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for item in sorted(ROOT.rglob('*')):
            if not item.is_file() or SKIP_DIRS.intersection(item.relative_to(ROOT).parts):
                continue
            if item.suffix.lower() in SKIP_SUFFIXES or item.name in SKIP_NAMES:
                continue
            # Ship curated Linux desktop entries required by the Ubuntu DEB builder.
            if item.suffix == '.desktop' and item.relative_to(ROOT).parts[0] != 'linux':
                continue
            archive.write(item, 'amicus-theologi/'+item.relative_to(ROOT).as_posix())
    print(f'Erstellt: {output} ({output.stat().st_size:,} Bytes)')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('output',nargs='?',default=str(ROOT.parent/'Amicus_Theologi_v1.0.8.zip'))
    build(parser.parse_args().output)
