import pandas as pd
from pathlib import Path

LEAGUES = [
    'lnb',
    'sweden',
    'finland',
    'prob',
    'proa_germany',
    'aba',
    'hungary',
    'slovakia'
]


def read_adv(path, league):
    df = pd.read_csv(path, sep=';', skiprows=1, decimal=',')
    keep = ['Player', 'Team', 'TS%', 'ORB%', 'DRB%', 'STL%']
    df = df[keep].copy()
    df['League'] = league.upper()
    for col in ['TS%', 'ORB%', 'DRB%', 'STL%']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def read_box(path, league):
    df = pd.read_csv(path, sep=';', decimal=',')
    if 'Player' not in df.columns:
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)
    keep = ['Player', 'Team', 'MPG', '3P%', '3PA', 'ORB', 'DRB', 'SPG']
    df = df[keep].copy()
    df['League'] = league.upper()
    for col in ['MPG', '3P%', '3PA', 'ORB', 'DRB', 'SPG']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def main():
    data_dir = Path('data')
    merged_all = []

    for league in LEAGUES:
        adv_file = data_dir / f'{league}_advanced.csv'
        box_file = data_dir / f'{league}_box.csv'
        if not adv_file.exists() or not box_file.exists():
            print(f'Pomijam {league}: brak pary plików')
            continue

        adv = read_adv(adv_file, league)
        box = read_box(box_file, league)
        merged = adv.merge(box, on=['Player', 'Team', 'League'], how='inner')
        merged_all.append(merged)

    if not merged_all:
        raise ValueError('Brak plików advanced + box w folderze data/')

    df = pd.concat(merged_all, ignore_index=True)

    filtered = df[
        (df['TS%'] > 0.56) &
        (df['3P%'] > 0.35) &
        (df['3PA'] >= 3) &
        (df['MPG'] >= 20) &
        (df['ORB'] >= 1) &
        (df['DRB'] >= 3) &
        (df['SPG'] >= 1)
    ].copy()

    filtered = filtered.sort_values(['TS%', '3P%', 'SPG'], ascending=False)

    Path('output').mkdir(exist_ok=True)
    filtered.to_csv('output/europe_3d_targets.csv', index=False)
    print(filtered.head(30).to_string(index=False))
    print(f'\nZnaleziono {len(filtered)} graczy')


if __name__ == '__main__':
    main()