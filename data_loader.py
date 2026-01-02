import pandas as pd
import re


def parse_duration_to_minutes(duration_str):
    """
    Parses strings like '2h', '2 hours', '30s', '90m', '1.5h' into minutes (float).
    """
    if pd.isna(duration_str) or duration_str == '':
        return 0

    d = str(duration_str).lower().replace(' ', '')
    try:
        if 'h' in d:
            val = re.findall(r"(\d+(?:\.\d+)?)", d)[0]
            return float(val) * 60
        elif 'm' in d and 's' not in d:
            val = re.findall(r"(\d+(?:\.\d+)?)", d)[0]
            return float(val)
        elif 's' in d:
            val = re.findall(r"(\d+(?:\.\d+)?)", d)[0]
            return float(val) / 60
        else:
            return 0
    except Exception:
        return 0


## New: Specific parser for Length (handles "25km", "3000m", "5.2 km")
def parse_length_to_km(length_str):
    if pd.isna(length_str) or length_str == '':
        return 0

    val_str = str(length_str).lower().replace(' ', '')
    try:
        # Extract number
        number = float(re.findall(r"(\d+(?:\.\d+)?)", val_str)[0])

        # Normalize to KM
        if 'm' in val_str and 'km' not in val_str:
            return number / 1000  # Convert meters to km
        return number  # Assume km if just number or 'km'
    except Exception:
        return 0


##

def load_data(filepath_or_url):

    try:
        # 1. Try Loading as Excel
        excel_url = filepath_or_url
        if "output=csv" in filepath_or_url:
            excel_url = filepath_or_url.replace("output=csv", "output=xlsx")

        all_sheets = pd.read_excel(excel_url, sheet_name=None)
        df = pd.concat(all_sheets.values(), ignore_index=True)

        # Normalize headers immediately so downstream code finds 'date', 'activity', etc.
        df.columns = df.columns.str.lower().str.strip()

    except Exception as e:
        print(f"Warning: Excel load failed ({e}). Falling back to CSV.")
        try:
            df = pd.read_csv(filepath_or_url)
        except Exception as e2:
            print(f"Error loading data: {e2}")
            return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    try:
        # Clean Data
        df['date_obj'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

        if 'activity' in df.columns:
            df['activity'] = df['activity'].astype(str).str.lower().str.strip()

        df['duration_mins'] = df['duration'].apply(parse_duration_to_minutes)

        ## New: Apply length parser
        if 'length' in df.columns:
            df['length'] = df['length'].apply(parse_length_to_km)
        else:
            df['length'] = 0
        ##

        # Fill NaNs for other metrics
        cols_to_fill = ['reps', 'sets', 'weight', 'elevation']
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['month'] = df['date_obj'].dt.strftime('%Y-%m')
        df['week'] = df['date_obj'].dt.isocalendar().week

        return df.sort_values('date_obj')

    except Exception as e:
        print(f"Error cleaning data: {e}")
        return pd.DataFrame()