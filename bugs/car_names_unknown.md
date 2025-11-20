I am still seeing car names as "unknown".

eg:
2025-11-20_17-26_sebring-international-raceway_gt3_unknown_felicio-tamaja_lap2_t127s

I suspect we are having trouble matching the metadata we retrieve to the lookup from the rest api.

## FIXED

**Root Cause:**
The REST API integration (commit 8b32d7c) enriched opponent laps with vehicle metadata (car_model, car_class, etc.) but did NOT enrich player laps. This caused two issues:

1. **Missing Player Enrichment**: Player lap filenames didn't include car model information because `example_app.py` only called `get_session_info()` without enriching it from REST API data
2. **Version Suffix Mismatch**: REST API cache includes version numbers (e.g., "Team #123:CODE 1.42") but shared memory returns names without versions (e.g., "Team #123:CODE"), causing lookup failures

**Solution:**

1. **Added REST API enrichment for player laps** (`example_app.py`):
   - After getting session_info, look up vehicle metadata from REST API
   - Add car_model, car_class, manufacturer, team_name to session_info
   - Falls back gracefully if REST API unavailable

2. **Implemented fuzzy matching** (`src/lmu_rest_api.py`):
   - Updated `lookup_vehicle()` to handle version suffix mismatches
   - Tries exact match first, then prefix matching (e.g., "Team #123:CODE" matches "Team #123:CODE 1.42")

**Result:**
- When REST API available: Filenames now use car model and class (e.g., "lmp2-elms_oreca-07_player_lap2.csv")
- When REST API unavailable: Falls back to team entry name (e.g., "team-name-#123_player_lap2.csv")
- No more "unknown" car names in filenames
