import obd
import time
import urllib.request
import json


# contains data from queries at a certain time
class InstantData:
	def __init__(self, seconds, currentFuelLevel, currentFuelRate, currentSpeed, currentMPG, rpm):
		self.elapsedSeconds = seconds
		self.fuelLevel = currentFuelLevel
		self.fuelRate = currentFuelRate
		self.vehicleSpeed = currentSpeed
		self.instantMPG = currentMPG
		self.rpm = rpm

lastIndexSent = 0

def create_json_object(data):
	return "{"
	+"\"ELAPSED_SECONDS\":" + data.elapsedSeconds + ","
	+"\"FUEL_LEVEL\":\"" + data.fuelLevel.value.magnitude + "\","
	+"\"FUEL_RATE\":\"" + data.fuelRate.value.magnitude + "\","
	+"\"SPEED\":\"" + data.vehicleSpeed.value.magnitude + "\","
	+"\"MPG\":\"" + data.instantMPG + "\""
	"}"

def post_data():
	"""Send data from OBD2 to the server"""
	if (len(vehicleData) -1 > lastIndexSent):
		dataToSend = vehicleData[lastIndexSent+1] # create sub list starting where we left off

		# create json string
		jsonObjects = map(create_json_object, dataToSend)
		body = "[" + ",".join(jsonObjects) + "]"

		url = "http://www.testmycode.com"
		req = urllib.request.Request(url)
		req.add_header('Content-Type', 'application/json; charset=utf-8')
		jsondata = json.dumps(body)
		jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
		req.add_header('Content-Length', len(jsondataasbytes))
		#print (jsondataasbytes)
		response = urllib.request.urlopen(req, jsondataasbytes)
		lastIndexSent = len(vehicleData) - 1
		return response


# calculate MPG of instantData at a certain index
def calculateMPG(index):
	fuelRateAtIndex = vehicleData[index].fuelRate.magnitude
	speedAtIndex = vehicleData[index].vehicleSpeed.magnitude
	return speedAtIndex/fuelRateAtIndex


def calculateAverageMPG():

	return

# obd connection setup
connection = obd.OBD()  # auto-connects to USB or RF port
#cmd = obd.commands.SPEED  # select an OBD command (sensor)
print(obd.commands.has_command(obd.commands.SPEED))

# sets the amount of seconds between queries
querySpeed = 1

# dataset variables
vehicleData = []
currentIndex = 0
elapsedSeconds = 0

while True:

	# ugly code is best code
	vehicleData.insert(currentIndex, InstantData(elapsedSeconds, connection.query(obd.commands.FUEL_LEVEL),
		(connection.query(obd.commands.FUEL_RATE)), connection.query(obd.commands.SPEED), "0", connection.query(obd.commands.RPM)))

	# print data
	print("elapsedSeconds: " + str(vehicleData[currentIndex].elapsedSeconds))
	print("fuelRateGPH: " + str(vehicleData[currentIndex].fuelRate))
	print("fuelLevel: " + str(vehicleData[currentIndex].fuelLevel))
	#print("MPG: " + str(calculateMPG(currentIndex)))
	print("RPM: " + str(vehicleData[currentIndex].rpm))

	elapsedSeconds += querySpeed
	currentIndex += 1

	# delay
	time.sleep(querySpeed)
