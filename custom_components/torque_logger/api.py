"""Torque Logger API Client/DataView."""

import logging
import pint
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import callback
from homeassistant.util import slugify
from .coordinator import TorqueLoggerCoordinator

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

API_PATH = "/api/torque-logger"

ureg = pint.UnitRegistry()

imperalUnits = {"km": "mi", "°C": "°F", "km/h": "mph", "m": "ft"}

prettyPint = {
    "degC": "°C",
    "degF": "°F",
    "mile / hour": "mph",
    "kilometer / hour": "km/h",
    "mile": "mi",
    "kilometer": "km",
    "meter": "m",
    "foot": "ft",
}

assumedUnits = {
    "04": "%",
    "05": "°C",
    "0c": "rpm",
    "0d": "km/h",
    "0f": "°C",
    "11": "%",
    "1f": "km",
    "21": "km",
    "2f": "%",
    "31": "km",
    "ff1001": "km/h",
    "ff1006": "°",
    "ff1005": "°",
    "ff1239": "m",
    "ff1010": "m",
    "ff1007": "°",
    "ff123a": "",
    "ff1237": "km/h"
}

assumedShortName = {
    "04": "engine_load",
    "05": "coolant_temp",
    "0c": "engine_rpm",
    "0d": "speed",
    "0f": "intake_temp",
    "11": "throttle_pos",
    "1f": "run_since_start",
    "21": "dis_mil_on",
    "2f": "fuel",
    "31": "dis_mil_off",
    "ff1001": "gps_spd",
    "ff1006": "gpslat",
    "ff1005": "gpslon",
    "ff1239": "gps_acc",
    "ff1010": "gps_height",
    "ff1007": "gps_brng",
    "ff123a": "gps_sat",
    "ff1237": "spd_diff"
}

assumedFullName = {
    "04": "Engine Load",
    "05": "Coolant Temperature",
    "0c": "Engine RPM",
    "0d": "Vehicle Speed",
    "0f": "Intake Air Temperature",
    "11": "Throttle Position",
    "1f": "Distance Since Engine Start",
    "21": "Distance with MIL on",
    "2f": "Fuel Level",
    "31": "Distance with MIL off",
    "ff1001": "Vehicle Speed (GPS)",
    "ff1006": "GPS Latitude",
    "ff1005": "GPS Longitude",
    "ff1239": "GPS Accuracy",
    "ff1010": "GPS Altitude",
    "ff1007": "GPS Bearing",
    "ff123a": "GPS Satellites",
    "ff1237": "GPS vs OBD Speed difference"
}

class TorqueReceiveDataView(HomeAssistantView):
    """Handle data from Torque requests."""

    url = API_PATH
    name = "api:torque-logger"
    coordinator: TorqueLoggerCoordinator

    def __init__(self, data: dict[str, str], email: str, imperial: bool):
        """Initialize a Torque view."""
        self.data = data
        self.email = email
        self.imperial = imperial
        self.email = email

    @callback
    def get(self, request):
        """Handle Torque data GET request."""
        # hass = request.app["hass"]

        session = self.parse_fields(request.query)
        if session is not None:
            self._async_publish_data(session)
        return "OK!"

    def parse_fields(self, qdata):  # noqa
        """Handle Torque data request."""

        session: str = qdata.get("session")
        if session is None:
            raise Exception("No Session")

        if session not in self.data:
            self.data[session] = {
                "profile": {},
                "unit": {},
                "defaultUnit": {},
                "fullName": {},
                "shortName": {},
                "value": {},
                "unknown": [],
                "time": 0,
            }

        for key, value in qdata.items():
            if key.startswith("userUnit"):
                continue
            if key.startswith("userShortName"):
                item = key[13:]
                self.data[session]["shortName"][item] = value
                continue
            if key.startswith("userFullName"):
                item = key[12:]
                self.data[session]["fullName"][item] = value
                continue
            if key.startswith("defaultUnit"):
                item = key[11:]
                self.data[session]["defaultUnit"][item] = value
                continue
            if key.startswith("k"):
                item = key[1:]
                if len(item) == 1:
                    item = "0" + item
                self.data[session]["value"][item] = value
                continue
            if key.startswith("profile"):
                item = key[7:]
                self.data[session]["profile"][item] = value
                continue
            if key == "eml":
                self.data[session]["profile"]["email"] = value
                continue
            if key == "time":
                self.data[session]["time"] = value
                continue
            if key == "v":
                self.data[session]["profile"]["version"] = value
                continue
            if key == "session":
                continue
            if key == "id":
                self.data[session]["profile"]["id"] = value
                continue

            self.data[session]["unknown"].append({"key": key, "value": value})

        if (self.data[session]["profile"]["email"] == self.email
        and self.data[session]["profile"]["email"] != ""):
            return session
        raise Exception("Not configured email")

    def _get_field(self, session, key):
        name = self.data[session]["fullName"].get(key, assumedFullName.get(key, key))
        short_name = self.data[session]["shortName"].get(
            key, assumedShortName.get(key, key)
        )
        unit = self.data[session]["defaultUnit"].get(key, assumedUnits.get(key, ""))
        value = self.data[session]["value"].get(key)
        short_name = slugify(short_name)

        if self.imperial is True:
            if unit in imperalUnits:
                conv = _pretty_convert_units(float(value), unit, imperalUnits[unit])
                value = conv["value"]
                unit = conv["unit"]

        return {
            "name": name,
            "short_name": short_name,
            "unit": unit,
            "value": value,
        }


    def _get_profile(self, session: str):
        return self.data[session]["profile"]

    def _get_data(self, session: str):
        retdata = {}
        retdata["profile"] = self._get_profile(session)
        retdata["time"] = self.data[session]["time"]
        meta = {}

        for key in self.data[session]["value"].items():
            row_data = self._get_field(session, key)
            retdata[row_data["short_name"]] = row_data["value"]
            meta[row_data["short_name"]] = {
                "name": row_data["name"],
                "unit": row_data["unit"],
            }

        retdata["meta"] = meta

        return retdata

    async def _async_publish_data(self, session: str):
        session_data = self._get_data(session)
        # Do not publish until we have at least the car name
        # Why don't I use Id? Because you may have multiple
        # phones pushing data on the same car, and ids would differ.
        if "Name" not in session_data["profile"] or self.coordinator is None:
            return

        await self.coordinator.async_set_updated_data(session_data)
        await self.coordinator.add_entities(session_data)


def _pretty_units(unit):
    if unit in prettyPint:
        return prettyPint[unit]

    return unit


def _unpretty_units(unit):
    for pint_unit, pretty_unit in prettyPint.items():
        if pretty_unit == unit:
            return pint_unit

    return unit


def _convert_units(value, u_in, u_out):
    q_in = ureg.Quantity(value, u_in)
    q_out = q_in.to(u_out)
    return {"value": round(q_out.magnitude, 2), "unit": str(q_out.units)}


def _pretty_convert_units(value, u_in, u_out):
    p_in = _unpretty_units(u_in)
    p_out = _unpretty_units(u_out)
    res = _convert_units(value, p_in, p_out)
    return {"value": res["value"], "unit": _pretty_units(res["unit"])}
