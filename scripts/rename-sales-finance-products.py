"""Apply stable, realistic Swedish names without changing any product data."""
from pathlib import Path
import csv
import hashlib
import json

PRODUCT_NAMES = {
    1: 'Anteckningsbok A5', 2: 'Kulspetspennor 10-pack',
    3: 'Skrivbordsorganisatör', 4: 'Dokumentmapp A4',
    5: 'Häftapparat', 6: 'Musmatta med handledsstöd',
    7: 'Stekpanna 28 cm', 8: 'Vattenkokare 1,7 l',
    9: 'Skärbräda i bambu', 10: 'Matlådor 3-pack',
    11: 'Kockkniv 20 cm', 12: 'Termoskanna 1 l',
    13: 'Webbkamera Full HD', 14: 'Bildskärm 24 tum',
    15: 'Bluetoothhögtalare', 16: 'Trådlösa hörlurar',
    17: 'Robotdammsugare', 18: 'Surfplatta 10 tum',
    19: 'Vandringsryggsäck 30 l', 20: 'Tält för två personer',
    21: 'Träningsmatta', 22: 'Sovsäck',
    23: 'Hantelset 10 kg', 24: 'Vandringsstavar',
    25: 'Vattenslang 25 m', 26: 'Sekatör',
    27: 'Planteringslåda', 28: 'Trädgårdsvagn',
    29: 'Bevattningsspridare', 30: 'Trädgårdsbänk',
}


def apply_names():
    data = Path(__file__).resolve().parents[1] / 'powerbi-sales-finance/data'
    path = data / 'DimProduct.csv'
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    assert {int(r['ProductKey']) for r in rows} == set(PRODUCT_NAMES)
    assert len(set(PRODUCT_NAMES.values())) == len(rows)
    original = [{k: v for k, v in r.items() if k != 'ProductName'} for r in rows]
    for row in rows:
        row['ProductName'] = PRODUCT_NAMES[int(row['ProductKey'])]
    assert original == [{k: v for k, v in r.items() if k != 'ProductName'} for r in rows]
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    manifest_path = data / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        manifest['sha256']['DimProduct'] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Renamed 30 products; keys, categories, prices and costs preserved.')


if __name__ == '__main__':
    apply_names()
