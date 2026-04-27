import os
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta

def _client():
    return InfluxDBClient(
        url=os.environ["INFLUXDB_URL"],
        token=os.environ["INFLUXDB_TOKEN"],
        org=os.environ["INFLUXDB_ORG"]
    )

def get_latest_temperature() -> float | None:
    query = '''
        from(bucket: "{bucket}")
          |> range(start: -10m)
          |> filter(fn: (r) => r._measurement == "temperature_eau" and r._field == "value")
          |> last()
    '''.format(bucket=os.environ["INFLUXDB_BUCKET"])

    with _client() as c:
        tables = c.query_api().query(query)
        for table in tables:
            for record in table.records:
                return record.get_value()
    return None

def get_latest_pump_state() -> bool | None:
    query = '''
        from(bucket: "{bucket}")
          |> range(start: -10m)
          |> filter(fn: (r) => r._measurement == "etat_pompe" and r._field == "value")
          |> last()
    '''.format(bucket=os.environ["INFLUXDB_BUCKET"])

    with _client() as c:
        tables = c.query_api().query(query)
        for table in tables:
            for record in table.records:
                return bool(record.get_value())
    return None

def get_temperature_history(hours: int = 24) -> list:
    if hours <= 24:
        every, avg_n = "1m", 7
    elif hours <= 72:
        every, avg_n = "5m", 5
    else:
        every, avg_n = "15m", 3

    query = '''
        from(bucket: "{bucket}")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r._measurement == "temperature_eau" and r._field == "value")
          |> aggregateWindow(every: {every}, fn: mean, createEmpty: false)
          |> movingAverage(n: {avg_n})
    '''.format(bucket=os.environ["INFLUXDB_BUCKET"], hours=hours, every=every, avg_n=avg_n)

    results = []
    with _client() as c:
        tables = c.query_api().query(query)
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time().isoformat(),
                    "value": round(record.get_value(), 2)
                })
    return results

def get_pump_history(hours: int = 24) -> list:
    every = "30s" if hours <= 12 else "1m" if hours <= 24 else "5m" if hours <= 72 else "15m"

    query = '''
        from(bucket: "{bucket}")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r._measurement == "etat_pompe" and r._field == "value")
          |> aggregateWindow(every: {every}, fn: max, createEmpty: true)
          |> toFloat()
          |> fill(value: 0.0)
    '''.format(bucket=os.environ["INFLUXDB_BUCKET"], hours=hours, every=every)

    results = []
    with _client() as c:
        tables = c.query_api().query(query)
        for table in tables:
            for record in table.records:
                val = record.get_value()
                results.append({
                    "time": record.get_time().isoformat(),
                    "value": int(val) if val is not None else 0
                })
    return results

def get_avg_temp_yesterday() -> float | None:
    today     = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    query = '''
        from(bucket: "{bucket}")
          |> range(start: {start}, stop: {stop})
          |> filter(fn: (r) => r._measurement == "temperature_eau" and r._field == "value")
          |> mean()
    '''.format(
        bucket=os.environ["INFLUXDB_BUCKET"],
        start=yesterday.strftime("%Y-%m-%dT%H:%M:%SZ"),
        stop=today.strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    with _client() as c:
        tables = c.query_api().query(query)
        for table in tables:
            for record in table.records:
                return round(record.get_value(), 2)
    return None