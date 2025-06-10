import csv
import os
from pathlib import Path
from typing import Union

ENCODING = 'utf-8'

def load_csv(file_path):
    with open(file_path, newline='', encoding=ENCODING) as f:
        return list(csv.DictReader(f))

def load_data(data_dir):
    internal = load_csv(os.path.join(data_dir, 'internal.csv'))
    external = load_csv(os.path.join(data_dir, 'external.csv'))
    return internal, external

def match_patients(internal, external):
    matches = []

    # Inject stable unique IDs
    for i, p in enumerate(internal):
        p['Id'] = f'int-{i}'

    for j, p in enumerate(external):
        p['Id'] = f'ext-{j}'

    # Stub match: naive 1-to-1 pairing for demo/testing
    for e_idx, e in enumerate(external):
        if e_idx < len(internal):
            matches.append({
                'external': e,
                'internal': internal[e_idx],
                'score': 1.0  # placeholder score
            })

    return matches


def write_match(data_dir, external_id, internal_id):
    path = os.path.join(data_dir, 'matches.csv')
    try:
        with open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([external_id, internal_id])
        return True
    except Exception as e:
        print(f"Error writing match: {e}")
        return False
