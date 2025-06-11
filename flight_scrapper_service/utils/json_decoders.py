import json
from datetime import datetime, time, timedelta
from decimal import Decimal


class FlightsJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # as a string (preserves precision)
            return str(obj)
        if isinstance(obj, datetime):
            # ISO 8601
            return obj.isoformat()
        if isinstance(obj, time):
            # 24-hour HH:MM:SS
            return obj.strftime("%H:%M:%S")
        if isinstance(obj, timedelta):
            # total seconds as int or float
            return obj.total_seconds()
        return super().default(obj)