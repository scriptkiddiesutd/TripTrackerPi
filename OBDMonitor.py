import obd
import urllib.request
import json
import time

URL = "http://example.com"


# contains data from queries at a certain time
class InstantData:
	def __init__(self, seconds, currentFuelLevel, currentSpeed, currentMPG, rpm, maf, distDTCClear):
		self.elapsedSeconds = seconds
		self.fuelLevel = currentFuelLevel
		# self.fuelRate = currentFuelRate
		self.vehicleSpeed = currentSpeed
		self.instantMPG = currentMPG
		self.rpm = rpm
		self.maf = maf
		self.distDTCClear = distDTCClear


def create_json_object(data):
	return ("{"
		"\"ELAPSED_SECONDS\":" + str(data.elapsedSeconds) + ","
		"\"FUEL_LEVEL\":\"" + str(data.fuelLevel.value.magnitude) + "\","
		#"\"FUEL_RATE\":\"" + str(data.fuelRate.value.magnitude) + "\","
		"\"SPEED\":\"" + str(data.vehicleSpeed.value.magnitude) + "\","
		"\"MPG\":\"" + str(data.instantMPG) + "\","
		"\"RPM\":\"" + str(data.rpm.value.magnitude) + "\","
		"\"MAF\":\"" + str(data.maf.value.magnitude) + "\","
		"\"DISTANCE\":\"" + str(data.distDTCClear.value.magnitude) + "\""
		"}")


def post_data():
	"""Send data from OBD-II to the server"""
	global lastIndexSent
	if len(vehicleData) - 1 > lastIndexSent:
		dataToSend = vehicleData[lastIndexSent + 1:]  # create sub list starting where we left off

		# create json string
		jsonObjects = map(create_json_object, dataToSend)
		body = "[" + ",".join(jsonObjects) + "]"
		print("JSON body: " + body)

		req = urllib.request.Request(URL)
		req.add_header('Content-Type', 'application/json; charset=utf-8')
		jsondata = json.dumps(body)
		jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
		req.add_header('Content-Length', len(jsondataasbytes))
		#print(jsondataasbytes)
		#response = urllib.request.urlopen(req, jsondataasbytes)
		lastIndexSent = len(vehicleData) - 1
		#return response


# calculate fuel rate
def calculateFuelRate(index):
	fuelRateAtIndex = vehicleData[index].maf.value.magnitude  # maf value
	# fuelRateAtIndex = fuelRateAtIndex/14.7  # lbs/s
	# fuelRateAtIndex = fuelRateAtIndex/454  # g/s
	# fuelRateAtIndex = fuelRateAtIndex*3600  # g/h
	fuelRateAtIndex = fuelRateAtIndex*0.0805
	return fuelRateAtIndex


# calculate MPG of instantData at a certain index
def calculateMPG(index):
	fuelRateAtIndex = calculateFuelRate(index)
	# alternative calculation if vehicle supports fuel flow sensor
	# fuelRateAtIndex = vehicleData[index].fuelRate.magnitude

	speedAtIndex = vehicleData[index].vehicleSpeed.value.magnitude
	return speedAtIndex / fuelRateAtIndex


# calculates distance traveled based on delta distance since last DTC clear
def calculateDistanceTraveled(index):
	return vehicleData[index].distDTCClear-vehicleData[0].distDTCClear


# obd connection setup
connection = obd.OBD()  # auto-connects to USB or RF port
# cmd = obd.commands.SPEED  # select an OBD command (sensor)
print(obd.commands.has_command(obd.commands.SPEED))

# sets the amount of seconds between queries
querySpeed = 1

lastIndexSent = 0

# dataset variables
vehicleData = []
currentIndex = 0
elapsedSeconds = 0
lastQueryTime = time.time()

while True:
	# ugly code is best code
	vehicleData.insert(currentIndex, InstantData(elapsedSeconds, connection.query(obd.commands.FUEL_LEVEL),
	                                             connection.query(obd.commands.SPEED), "0",
	                                             connection.query(obd.commands.RPM), connection.query(obd.commands.MAF),
	                                             connection.query(obd.commands.DISTANCE_SINCE_DTC_CLEAR)))

	# print data
	print("elapsedSeconds: " + str(vehicleData[currentIndex].elapsedSeconds))
	# print("fuelRateGPH: " + str(vehicleData[currentIndex].fuelRate))
	print("fuelLevel: " + str(vehicleData[currentIndex].fuelLevel))
	print("MAF: " + str(vehicleData[currentIndex].maf))
	print("Distance: " + str(calculateDistanceTraveled(currentIndex)))
	print("MPG: " + str(calculateMPG(currentIndex)))
	print("RPM: " + str(vehicleData[currentIndex].rpm.value.magnitude))

	elapsedSeconds += time.time() - lastQueryTime
	currentIndex += 1
	lastQueryTime = time.time()

	# every 5th iteration, send the data to the server
	if currentIndex - lastIndexSent >= 5:
		post_data()

	# delay
	time.sleep(querySpeed)
