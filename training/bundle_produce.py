"""Bundle prepared produce files for Colab, preserving original split layout."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from dataset_io import file_sha256

PROJECT = Path(__file__).resolve().parents[1]
root = PROJECT / 'datasets' / 'fruits_vegetables'
prepared = root / 'prepared'

def main():
    summary = json.loads((PROJECT / 'datasets' / 'reports' / 'produce-summary.json').read_text())
    output = root / 'timpla-produce-colab.zip'
    partial = output.with_suffix('.zip.part')
    with ZipFile(partial, 'w', compression=ZIP_STORED, allowZip64=True) as archive:
        files = sorted(p for p in prepared.rglob('*') if p.is_file())
        for path in files:
            archive.write(path, str(Path('timpla_produce') / path.relative_to(prepared)))
        for path in (root / 'SOURCE_README.md', root / 'SOURCE_LICENSE', root / 'class-remap.json', PROJECT / 'datasets' / 'reports' / 'produce-summary.json'):
            archive.write(path, str(Path('timpla_produce') / 'provenance' / path.name))
    with ZipFile(partial) as archive:
        assert archive.testzip() is None
        for split, expected in summary['prepared_images'].items():
            actual = sum(name.startswith(f'timpla_produce/images/{split}/') for name in archive.namelist())
            assert actual == expected, (split, actual, expected)
    partial.replace(output)
    digest = file_sha256(output)
    manifest = {'file': output.name, 'bytes': output.stat().st_size, 'sha256': digest, 'training_config_after_extraction': 'timpla_produce/data.yaml', 'manual_label_review': 'sample_only_not_exhaustive'}
    (root / 'bundle.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2), flush=True)

if __name__ == '__main__':
    main()
