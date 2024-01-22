import serial


def parse_gps_data(data):
    # Split the input data into lines
    lines = data.split('\n')
    #print(lines)
    latitude = None
    longitude = None

    for line in lines:
        if line.startswith('$GPGLL'):
            fields = line.split(',')
            if len(fields) >= 5:
                # Extract latitude and longitude from the $GPGLL sentence
                latitude = fields[1].strip()
                longitude = fields[3].strip()

    # Validation: Ensure that latitude and longitude are not empty
    if latitude and longitude:
        return latitude, longitude
    else:
        return None, None


def get_gps_coordinates(gps_node):  # TODO might use multithreading and storing last position as backup to enhance speed
    try:
        gps = serial.Serial(gps_node, baudrate=9600)
        latitude = longitude = None
        while True:
            ser_bytes = gps.readline()
            decoded_bytes = ser_bytes.decode("utf-8")
            latitude, longitude = parse_gps_data(decoded_bytes)
            if latitude is not None and longitude is not None:
                #print("latlong: " + latitude, longitude)
                break

        return latitude, longitude

    except Exception as e:
        print("There's no GPS connected.")
        print(f"Error: {e}")
    finally:
        gps.close()
