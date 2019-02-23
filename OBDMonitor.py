import obd
import time

#class InstantData:



# obd connection setup
connection = obd.OBD()  # auto-connects to USB or RF port
cmd = obd.commands.SPEED  # select an OBD command (sensor)

# sets the speed
querySpeed = 5

elapsedSeconds = 0
distanceTraveled = 0
#vehicleData = []

while True:
    elapsedSeconds += querySpeed

    # query vehicle for data
    fuelLevel = connection.query("FUEL_LEVEL")
    fuelRateLPH = connection.query("FUEL_RATE")
    vehicleSpeed = connection.query("SPEED")

    # print data
    print(elapsedSeconds)
    print(fuelLevel.value)  # returns unit-bearing values thanks to Pint
    print(fuelRateLPH.value.to("gph"))  # user-friendly unit conversions

    # write data to list

    # delay
    time.sleep(querySpeed)
