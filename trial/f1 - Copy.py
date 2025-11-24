import fastf1

# Enable FastF1 cache
fastf1.Cache.enable_cache('./cache')


def load_session_data(season: int, gp_name: str, session_name: str):
    """
    Load session data for a given year, Grand Prix, and session type.
    """
    session = fastf1.get_session(season, gp_name, session_name)
    session.load()
    return session


def get_drivers_in_session(session):
    """
    Get a sorted list of driver codes (e.g., VER, HAM) from session laps.
    """
    drivers = session.laps['Driver'].unique().tolist()
    drivers.sort()
    return drivers


def get_fastest_lap(session, driver_code: str):
    """
    Get the fastest lap for a given driver.
    """
    driver_laps = session.laps.pick_drivers(driver_code)
    fastest_lap = driver_laps.pick_fastest()
    return fastest_lap


def get_telemetry_data(fastest_lap):
    """
    Get telemetry data for a driver's fastest lap with distance.
    """
    telemetry = fastest_lap.get_car_data().add_distance()
    return telemetry
