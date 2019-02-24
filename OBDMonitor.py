import obd
import urllib.request
import json
import time

URL = "http://trip-tracker.net/trips/updateTrip"


# contains data from queries at a certain time
class InstantData:
	def __init__(self, seconds, currentFuelLevel, currentSpeed, currentMPG, rpm, maf, distDTCClear, distance, temperature, duration):
		self.elapsedSeconds = seconds
		self.fuelLevel = currentFuelLevel
		# self.fuelRate = currentFuelRate
		self.vehicleSpeed = currentSpeed
		self.instantMPG = currentMPG
		self.rpm = rpm
		self.maf = maf
		self.distDTCClear = distDTCClear
		self.distance = distance
		self.temperature = temperature
		self.duration = duration


def create_json_object(data):
	return ("{"
		"\"ELAPSED_SECONDS\":" + str(data.elapsedSeconds) + ","
		"\"FUEL_LEVEL\":\"" + str(data.fuelLevel.value.magnitude) + "\","
		#"\"FUEL_RATE\":\"" + str(data.fuelRate.value.magnitude) + "\","
		"\"SPEED\":\"" + str(data.vehicleSpeed.value.magnitude) + "\","
		"\"MPG\":\"" + str(data.instantMPG) + "\","
		"\"RPM\":\"" + str(data.rpm.value.magnitude) + "\","
		"\"MAF\":\"" + str(data.maf.value.magnitude) + "\","
		"\"DISTANCE\":\"" + str(data.distance) + "\","
		"\"DISTANCE_SINCE_DTC_CLEAR\":\"" + str(data.distDTCClear.value.magnitude) + "\","
		"\"COOLANT_TEMP\":\"" + str(data.temperature.value.magnitude) + "\","
		"\"DURATION\":\"" + str(data.duration.value.magnitude) + "\""
		"}")


def post_data():
	"""Send data from OBD-II to the server"""
	global lastIndexSent
	try:
		if len(vehicleData) - 1 > lastIndexSent:
			dataToSend = vehicleData[lastIndexSent + 1:]  # create sub list starting where we left off

			# create json string
			jsonObjects = map(create_json_object, dataToSend)
			body = "{\"license\":\"KBG7614\", \"tripId\":\"3\",\"points\":[" + ",".join(jsonObjects) + "]}"
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
	except:
		print("An error occurred while creating and sending post request")


# calculate fuel rate
def calculateFuelRateFromIndex(index):
	fuelRateAtIndex = vehicleData[index].maf.value.magnitude  # maf value
	# fuelRateAtIndex = fuelRateAtIndex/14.7  # lbs/s
	# fuelRateAtIndex = fuelRateAtIndex/454  # g/s
	# fuelRateAtIndex = fuelRateAtIndex*3600  # g/h
	fuelRateAtIndex = fuelRateAtIndex*0.0805
	return fuelRateAtIndex


def calculateFuelRate(maf):
	fuelRateAtIndex = maf*0.0805*connection.query(obd.commands.COMMANDED_EQUIV_RATIO)
	return fuelRateAtIndex


# calculate MPG of instantData at a certain index
def calculateMPGFromIndex(index):
	fuelRateAtIndex = calculateFuelRateFromIndex(index)
	# alternative calculation if vehicle supports fuel flow sensor
	# fuelRateAtIndex = vehicleData[index].fuelRate.magnitude

	speedAtIndex = vehicleData[index].vehicleSpeed.value.magnitude
	return speedAtIndex / fuelRateAtIndex


# calculate MPG of instantData at a certain index
def calculateMPG(maf, speed):
	fuelRateAtIndex = calculateFuelRate(maf)
	# alternative calculation if vehicle supports fuel flow sensor
	# fuelRateAtIndex = vehicleData[index].fuelRate.magnitude

	#speedAtIndex = vehicleData[index].vehicleSpeed.value.magnitude
	return speed / fuelRateAtIndex


# calculates distance traveled based on delta distance since last DTC clear
def calculateDistanceTraveled(currentDistance):
	return currentDistance.value.magnitude-firstDTCSeen.value.magnitude


# obd connection setup
connection = obd.OBD()  # auto-connects to USB or RF port
# cmd = obd.commands.SPEED  # select an OBD command (sensor)
print(obd.commands.has_command(obd.commands.SPEED))

# sets the amount of seconds between queries
querySpeed = 1

lastIndexSent = -1

# dataset variables
vehicleData = []
currentIndex = 0
elapsedSeconds = 0
lastQueryTime = time.time()
firstDTCSeen = connection.query(obd.commands.DISTANCE_SINCE_DTC_CLEAR)

while True:
	# only logs data if rpm > 10
	if connection.query(obd.commands.RPM.value.magnitude) > 10:
		# ugly code is best code
		speed = connection.query(obd.commands.SPEED)
		maf = connection.query(obd.commands.MAF)
		totalDistance = connection.query(obd.commands.DISTANCE_SINCE_DTC_CLEAR)
		vehicleData.insert(currentIndex, InstantData(elapsedSeconds, connection.query(obd.commands.FUEL_LEVEL),
		                                             speed, calculateMPG(maf.value.magnitude, speed.value.magnitude),
		                                             connection.query(obd.commands.RPM), maf,
		                                             totalDistance,
		                                             calculateDistanceTraveled(totalDistance),
		                                             connection.query(obd.commands.COOLANT_TEMP),
		                                             connection.query(obd.commands.RUN_TIME)))

		# print data
		print("elapsedSeconds: " + str(vehicleData[currentIndex].elapsedSeconds))
		# print("fuelRateGPH: " + str(vehicleData[currentIndex].fuelRate))
		print("fuelLevel: " + str(vehicleData[currentIndex].fuelLevel))
		print("MAF: " + str(vehicleData[currentIndex].maf))
		print("Distance: " + str(calculateDistanceTraveled()))
		print("MPG: " + str(calculateMPGFromIndex(currentIndex)))
		print("RPM: " + str(vehicleData[currentIndex].rpm.value.magnitude))

		elapsedSeconds += time.time() - lastQueryTime
		currentIndex += 1
		lastQueryTime = time.time()

		# every 5th iteration, send the data to the server
		if currentIndex - lastIndexSent >= 5:
			post_data()

	# delay
	time.sleep(querySpeed)
