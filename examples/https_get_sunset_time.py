import json
import urllib.request
from TaskTonic import ttTonic, ttCatalyst, ttFormula, ttLog
from TaskTonic.ttTonicStore import ttTimerEveryDay


'''
Demo fetching the sunset en rise time from https://api.sunrise-sunset.org

I doesn't use the networking module because of https
I implements u call from urllib in a separate catalyst that prevents the
main catalyst from blocking in a time consuming operation (you see time DURATION warning in the logs!!)
'''


class ApiWorker(ttCatalyst):
    """
    A dedicated worker catalyst for blocking API calls.
    This prevents the main UI or application from freezing during the HTTPS request.
    """

    def ttsc__fetch_sun_times(self, lat, lng):
        self.log("Fetching data from API (blocking thread...)")
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=0"

        try:
            # Create a Request object and spoof a standard browser User-Agent
            # to prevent getting a 403 Forbidden error from the API's bot protection.
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )

            # Pass the Request object to urlopen instead of the raw url string
            with urllib.request.urlopen(req, timeout=5.0) as response:
                response_text = response.read().decode('utf-8')
                data = json.loads(response_text)

                if data.get("status") == "OK":
                    self.base.ttse__on_sun_data_received(data['results'])
                else:
                    self.base.ttse__on_api_error(data.get("status"))

        except Exception as e:
            self.base.ttse__on_api_error(str(e))


class SunTracker(ttTonic):
    """
    The main Tonic that orchestrates the daily updates and stores the state.
    """

    def ttse__on_start(self):
        # Coordinates for Den Haag (The Hague)
        self.lat = 52.0705
        self.lng = 4.3007

        # Spawn the dedicated worker for safe HTTPS requests
        self.worker = ApiWorker(name="HttpsWorker")

        # Schedule the update to run every day at 01:00 AM
        ttTimerEveryDay(hour=1, name='daily_fetch')

        # Fetch immediately on startup
        self.ttsc__update_now()

    def ttsc__update_now(self):
        self.to_state('fetching')
        self.worker.ttsc__fetch_sun_times(self.lat, self.lng)

    def ttse_fetching__on_sun_data_received(self, results):
        self.to_state('idle')

        sunrise = results.get('sunrise')
        sunset = results.get('sunset')

        self.log(f"Sunrise in Den Haag: {sunrise}")
        self.log(f"Sunset in Den Haag: {sunset}")

        # Store the data centrally so other Tonics or the UI can react to it
        if self.ledger.formula:
            with self.ledger.formula.group():
                self.ledger.formula.set('weather/den_haag/sunrise', sunrise)
                self.ledger.formula.set('weather/den_haag/sunset', sunset)

    def ttse_fetching__on_api_error(self, error_msg):
        self.to_state('idle')
        self.log(f"Failed to fetch sun data: {error_msg}")

    def ttse_idle__on_tm_daily_fetch(self, info):
        self.log("Daily timer fired, fetching new sun times...")
        self.ttsc__update_now()


class WeatherApp(ttFormula):
    def creating_formula(self):
        return {
            'tasktonic/project/name': 'Weather Fetcher',
            'tasktonic/log/to': 'screen',
            'tasktonic/log/default': ttLog.FULL,
        }

    def creating_starting_tonics(self):
        SunTracker(name="SunTracker")


if __name__ == "__main__":
    WeatherApp()