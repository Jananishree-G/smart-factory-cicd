import json
import boto3
import base64
from datetime import datetime, timezone

s3 = boto3.client("s3")

BUCKET_NAME = "smart-factory-sensor-data-janani"


def lambda_handler(event, context):

    print("=== SMART FACTORY SENSOR PROCESSING ===")

    for record in event.get("Records", []):

        encoded_data = record["kinesis"]["data"]

        decoded_data = base64.b64decode(encoded_data).decode("utf-8")

        sensor = json.loads(decoded_data)

        machine_id = sensor.get("machine_id")
        temperature = sensor.get("temperature", 0)
        vibration = sensor.get("vibration", 0)
        pressure = sensor.get("pressure", 0)

        if temperature > 80 or vibration > 7:
            machine_status = "WARNING"
        else:
            machine_status = "NORMAL"

        processed_data = {
            "machine_id": machine_id,
            "temperature": temperature,
            "vibration": vibration,
            "pressure": pressure,
            "machine_status": machine_status,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

        print("Processed sensor data:")
        print(json.dumps(processed_data))

        file_name = (
            f"sensor-data/{machine_id}/"
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S-%f')}.json"
        )

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(processed_data),
            ContentType="application/json"
        )

        print(f"Historical data stored in S3: {file_name}")

    return {
        "statusCode": 200,
        "message": "Sensor events processed successfully"
    }
