import pickle
import os
from Shared import LoadingBar as LoadingBar

def serializer(inputObject):
	outputObject = ""

	if inputObject == None:
		return "None"

	elif type(inputObject) is bytes:
		outputObject = "b("
		for loop in range(len(inputObject)):
			outputObject += str(inputObject[loop])
			if loop < len(inputObject)-1:
				outputObject +=","

		return outputObject + ")"
	
	elif type(inputObject) is str:
		return "'"+inputObject+"'"

	elif hasattr(inputObject, "__len__"):
		outputObject = []
		for loop in range(len(inputObject)):
			outputObject += [serializer(inputObject[loop])]

		outputObject = ", ".join(outputObject)
		return "["+outputObject+"]"
	else:
		return str(inputObject)
def deserializer(inputString):

	if inputString.startswith("b("):
		subInputString = inputString[2:-1]
		byteArray = list(map(int, subInputString.split(",")))
		outputObject = bytes(byteArray)

	elif inputString.startswith("["):
		lastIndex = inputString.rfind("]")
		inputString = inputString[1:lastIndex]

		stringList = []
		if inputString.count("[") == 0:
			stringList = inputString.split(", ")

		else:
			index = 0
			while index < len(inputString):
				if inputString.startswith(", "):
					inputString = inputString[2:]
				index = inputString.find("]")+1
				stringList += [inputString[0:index]]
				inputString = inputString[index:]


		outputObject = list(map(deserializer, stringList))

	elif inputString == "None":
		outputObject = None

	elif inputString == "True":
		outputObject = True

	elif inputString == "False":
		outputObject = False

	elif inputString.startswith("'"):
		outputObject = inputString.replace("'", "")

	elif "." in inputString:
		outputObject = float(inputString)

	else:
		try:
		    outputObject = int(inputString)
		except:
		    outputObject = inputString
			
	return outputObject

def DictAppend(address, dictionary): 
	if (dictionary == {}):
		return

	if (not DictFileExists(address)):
		DictSave(address, dictionary)

	else:
		address += ".txt"
		file = open(address, "a")
		for key, value in dictionary.items():
			file.write(str(key)+":"+serializer(value)+"\n")
		file.close()

	return
def DictSave(address, dictionary):
	address += ".txt"
	file = open(address, "w")
	for key, value in dictionary.items():
		serializerValue = serializer(value)
		file.write(str(key)+":"+serializerValue+"\n")
	file.close()
	return
def DictLoad(address, loadingBarOn=False):
	dictionary = {}
	address += ".txt"

	loadingBar = LoadingBar.LoadingBar(loadingBarOn)
	loadingBar.Update(0, "Loading Dict")

	file = open(address, "r")
	lines = file.readlines()
	file.close()
	
	numberOfLines = len(lines)
	loadingBar.Update(0, "Loading dict", 0, numberOfLines)

	for loop in range(numberOfLines):
		line = lines[loop][:-1].split(":")
		key = line[0]
		dictionary[key] = deserializer(line[1])

		loadingBar.Update(loop/numberOfLines, "Loading dict", loop, numberOfLines)

	loadingBar.Update(loop/numberOfLines, "Loading dict", numberOfLines, numberOfLines)

	return dictionary
def DictFileExists(address):
	return os.path.exists(address+".txt")

def ComplexSave(address, objectInfo):
	pickle.dump(objectInfo, open(address+".p", "wb"))
	return
def ComplexLoad(address):
	file = open(address+".p", "rb")
	objectInfo = pickle.load(file)
	file.close()
	return objectInfo
def ComplexFileExists(address):
	method = 0
	value = False
	value = os.path.exists(address+".p")
	return value

class DataSetTable:
	Content = {}
	IsLoaded = False

	def __init__(self, address, isLoaded):
		self.FileAddress = address
		self.IsLoaded = isLoaded
		self.Content = {}
		return

	def Load(self):
		self.Content = ComplexLoad(self.FileAddress)
		self.IsLoaded = True
		return
	def Save(self):
		ComplexSave(self.FileAddress, self.Content)
		return
	def Unload(self):
		self.Content ={}
		self.IsLoaded = False
		return