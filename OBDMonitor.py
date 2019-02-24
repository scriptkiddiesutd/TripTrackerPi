import obd
import time


class InstantData:
	def __init__(self, seconds, currentFuelLevel, currentFuelRate, currentSpeed):
		self.elapsedSeconds = seconds
		self.fuelLevel = currentFuelLevel
		self.fuelRateGPH = currentFuelRate
		self.vehicleSpeed = currentSpeed


# obd connection setup
connection = obd.OBD()  # auto-connects to USB or RF port
cmd = obd.commands.SPEED  # select an OBD command (sensor)

# sets the amount of seconds between queries
querySpeed = 5

vehicleData = []
elapsedSeconds = 0

while True:
	elapsedSeconds += querySpeed

	vehicleData.append(InstantData(elapsedSeconds, connection.query("FUEL_LEVEL"), connection.query("FUEL_RATE"), connection.query("SPEED")))

	# print data
	print("elapsedSeconds: " + vehicleData[elapsedSeconds].fuelLevel)
	print("fuelRateLPH: " + vehicleData[elapsedSeconds].fuelLevel)
	# print("fuelRateGPH: " + vehicleData[elapsedSeconds].fuelLevel.value.to("gph"))
	print("fuelLevel: " + vehicleData[elapsedSeconds].fuelLevel)

	# delay
	time.sleep(querySpeed)
