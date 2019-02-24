import obd
import time


# contains data from queries at a certain time
class InstantData:
	def __init__(self, seconds, currentFuelLevel, currentFuelRate, currentSpeed, currentMPG):
		self.elapsedSeconds = seconds
		self.fuelLevel = currentFuelLevel
		self.fuelRate = currentFuelRate
		self.vehicleSpeed = currentSpeed
		self.instantMPG = currentMPG


# calculate MPG of instantData at a certain index
def calculateMPG(index):
	fuelRateAtIndex = vehicleData[index].fuelRate
	speedAtIndex = vehicleData[index].vehicleSpeed
	return speedAtIndex/fuelRateAtIndex


def calculateAverageMPG():

	return


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

	# ugly code is best code
	vehicleData.insert(currentIndex, InstantData(elapsedSeconds, connection.query("FUEL_LEVEL"),
		(connection.query("FUEL_RATE")).value.to("gph"), (connection.query("SPEED").value.to("mph"))))

	# print data
	print("elapsedSeconds: " + vehicleData[currentIndex].elapsedSeconds)
	print("fuelRateGPH: " + vehicleData[currentIndex].fuelRate)
	print("fuelLevel: " + vehicleData[currentIndex].fuelLevel)
	print("MPG: " + calculateMPG(currentIndex))

	elapsedSeconds += querySpeed
	currentIndex += 1

	# delay
	time.sleep(querySpeed)
