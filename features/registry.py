from features.short_interest_data import fetch_short_interest
from features.short_volume_data import fetch_short_volume
from features.float_data import fetch_float
from features.options_data import fetch_options_pressure  

# Scanner-ready features registry
FEATURES = {
    "short_interest": fetch_short_interest,
    "short_volume": fetch_short_volume,
    "float": fetch_float,
    "options_data": fetch_options_pressure  
}