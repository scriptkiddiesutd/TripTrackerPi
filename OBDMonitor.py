import obd
import time

# contains data from queries at a certain time
class InstantData:
	def __init__(self, seconds, currentFuelLevel, currentFuelRate, currentSpeed, currentMPG):
		self.elapsedSeconds = seconds
		self.fuelLevel = currentFuelLevel
		self.fuelRateGPH = currentFuelRate
		self.vehicleSpeed = currentSpeed
		self.instantMPG = currentMPG


# obd connection setup
connection = obd.OBD()  # auto-connects to USB or RF port
cmd = obd.commands.SPEED  # select an OBD command (sensor)

# sets the amount of seconds between queries
querySpeed = 5

# dataset variables
vehicleData = []
currentIndex = 0
elapsedSeconds = 0

while True:

	vehicleData.insert(currentIndex, InstantData(elapsedSeconds, connection.query("FUEL_LEVEL"), connection.query("FUEL_RATE"), connection.query("SPEED")))

	# print data
	print("elapsedSeconds: " + vehicleData[currentIndex].elapsedSeconds)
	print("fuelRateLPH: " + vehicleData[currentIndex].fuelRateGPH)
	print("fuelRateGPH: " + vehicleData[currentIndex].fuelRateGPH.value.to("gph"))
	print("fuelLevel: " + vehicleData[currentIndex].fuelLevel)

	elapsedSeconds += querySpeed
	currentIndex += 1

	# delay
	time.sleep(querySpeed)
