import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# --- Individual Feature Scorers ---

def score_short_interest(si):
    # Cap at 30% (very high)
    return min(si / 0.3, 1.0)


def score_days_to_cover(dtc):
    # Lower is better (fast squeeze potential)
    # Cap at 10 days
    return 1 - min(dtc / 10.0, 1.0)


def score_short_volume_ratio(ratio):
    # Cap at 60%
    return min(ratio / 0.6, 1.0)


def score_call_oi_near_price(call_oi):
    # Scale based on meaningful OI threshold
    # Adjust later depending on your dataset
    return min(call_oi / 100000, 1.0)


def score_call_put_ratio(cp_ratio):
    # Favor call-heavy positioning
    return min(cp_ratio / 2.0, 1.0)


def score_gamma_distance(dist_pct):
    # Closer to gamma ramp is better
    return 1 - min(dist_pct / 0.2, 1.0)


def score_free_float(free_float_pct):
    # Lower float = higher score
    return 1 - min(free_float_pct / 1.0, 1.0)


# --- Main Absolute Scoring Function ---

def compute_short_score_absolute(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    scores = []

    for _, row in df.iterrows():
        s = (
            0.3 * score_short_interest(row['short_interest_short_interest']) +
            0.25 * score_days_to_cover(row['short_interest_days_to_cover']) +
            0.1 * score_short_volume_ratio(row['short_volume_short_volume_ratio']) +
            0.15 * score_call_oi_near_price(row['options_data_call_oi_within_10pct']) +
            0.1 * score_call_put_ratio(row['options_data_call_put_oi_ratio']) +
            0.05 * score_gamma_distance(row['options_data_distance_to_gamma_strike_pct']) +
            0.05 * score_free_float(row['float_free_float_percent'])
        )
        scores.append(s)

    df['short_score_absolute'] = scores

    return df

# --- Main Relative Scoring Function ---

def compute_short_score_relative(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()

    features = [
        'short_interest_short_interest',
        'short_interest_days_to_cover',
        'short_volume_short_volume_ratio',
        'options_data_call_oi_within_10pct',
        'options_data_call_put_oi_ratio',
        'options_data_distance_to_gamma_strike_pct',
        'float_free_float_percent'
    ]

    scaler = MinMaxScaler()
    df_norm = pd.DataFrame(
        scaler.fit_transform(df[features]),
        columns=features,
        index=df.index
    )

        # Inversions (important signals)
    df_norm['short_interest_days_to_cover'] = 1 - df_norm['short_interest_days_to_cover']
    df_norm['options_data_distance_to_gamma_strike_pct'] = 1 - df_norm['options_data_distance_to_gamma_strike_pct']
    df_norm['float_free_float_percent'] = 1 - df_norm['float_free_float_percent']

    weights = {
        'short_interest_short_interest': 0.3,
        'short_interest_days_to_cover': 0.25,
        'short_volume_short_volume_ratio': 0.1,
        'options_data_call_oi_within_10pct': 0.15,
        'options_data_call_put_oi_ratio': 0.1,
        'options_data_distance_to_gamma_strike_pct': 0.05,
        'float_free_float_percent': 0.05
    }

    df['short_score'] = sum(df_norm[f] * w for f, w in weights.items())

    return df

def get_top_n(df: pd.DataFrame, n: int = 50) -> pd.DataFrame:
    return df.sort_values(by='short_score', ascending=False).head(n).reset_index(drop=True)