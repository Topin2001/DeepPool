import os
from influxdb_client import InfluxDBClient

def get_avg_temp_yesterday() -> float | None:
    try:
        client = InfluxDBClient(
            url=os.environ["INFLUXDB_URL"],
            token=os.environ["INFLUXDB_TOKEN"],
            org=os.environ["INFLUXDB_ORG"]
        )
        query = '''
            import "timezone"
            option location = timezone.location(name: "Europe/Paris")
            from(bucket: "{bucket}")
              |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
              |> filter(fn: (r) => r._measurement == "temperature_eau" and r._field == "value")
              |> aggregateWindow(
                  every: 1d,
                  fn: mean,
                  createEmpty: false,
                  offset: 0h
              )
        '''.format(bucket=os.environ["INFLUXDB_BUCKET"])

        tables = client.query_api().query(query)
        for table in tables:
            for record in table.records:
                return round(record.get_value(), 2)
        client.close()
    except Exception as e:
        print(f"[WARN] Could not fetch avg temp: {e}")
    return None