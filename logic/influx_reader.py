import os
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient

def get_avg_temp_yesterday() -> float | None:
    try:
        today     = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        client = InfluxDBClient(
            url=os.environ["INFLUXDB_URL"],
            token=os.environ["INFLUXDB_TOKEN"],
            org=os.environ["INFLUXDB_ORG"]
        )
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

        tables = client.query_api().query(query)
        for table in tables:
            for record in table.records:
                return round(record.get_value(), 2)
        client.close()
    except Exception as e:
        print(f"[WARN] Could not fetch avg temp: {e}")
    return None