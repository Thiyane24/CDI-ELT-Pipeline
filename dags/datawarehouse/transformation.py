from datetime import timedelta, datetime


def parse_duration(duration_str):
    duration_str = duration_str.replace("PT", "").replace("P", "")

    values = {'D': 0, 'H': 0, 'M': 0, 'S': 0}

    for component in ['D', 'H', 'M', 'S']:
        if component in duration_str:
            parts = duration_str.split(component)
            values[component] = int(parts[0])
            duration_str = parts[1]

    total_duration = timedelta(
        days=values['D'],
        hours=values['H'],
        minutes=values['M'],
        seconds=values['S']
    )
    return total_duration


def transform_data(row):
    duration_td = parse_duration(row['duration'])       # ← lowercase
    row['duration'] = (datetime.min + duration_td).time()
    row['video_type'] = 'Shorts' if duration_td.total_seconds() <= 60 else 'Normal'  # ← lowercase
    return row