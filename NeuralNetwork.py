print("Importing Tflearn...")
import tflearn

class NeuralNetwork(object):

	def __init__(self, dataSetManager, winningModeON=False):
		self.DataSetManager = dataSetManager

		self.DataSetX = []
		self.DataSetY = []

		while len(self.DataSetY) == 0:
			self.DataSetX, self.DataSetY = self.DataSetManager.GetDataSet()

		inputShape, structreArray = self.PredictNetworkStructre()
		self.RunId = "test"
		self.NetworkModel = ModelMaker(inputShape, structreArray, batchSize=1000, lr=0.001)#, optimizer="sgd")
		return
	def PredictNetworkStructre(self):
		inputShape = [len(self.DataSetX[0])]
		if hasattr(self.DataSetX[0][0], "__len__"):
			inputShape += [len(self.DataSetX[0][0])]

			if hasattr(self.DataSetX[0][0][0], "__len__"):
				inputShape += [len(self.DataSetX[0][0][0])]

				if hasattr(self.DataSetX[0][0][0][0], "__len__"):
					inputShape += [len(self.DataSetX[0][0][0][0])]

		structreArray = []
		structreArray += [["ann", 1000, "Tanh"]]
		structreArray += [["ann", 1000, "Tanh"]]
		structreArray += [["ann", 1000, "Tanh"]]
		structreArray += [["ann", 1000, "Tanh"]]
		structreArray += [["ann", 1000, "Tanh"]]
		structreArray += [["ann", 1000, "Tanh"]]
		structreArray += [["ann", 9, "Tanh"]]

		if self.DataSetManager.MinOutputSize < -1 or self.DataSetManager.MinOutputSize > 1:
			structreArray += [["ann", len(self.DataSetY[0]), "Linear"]]
		elif self.DataSetManager.MinOutputSize < 0:
			structreArray += [["ann", len(self.DataSetY[0]), "Tanh"]]
		else:
			structreArray += [["ann", len(self.DataSetY[0]), "Sigmoid"]]

		self.NumberOfLayers = len(structreArray)
		return inputShape, structreArray

	def MoveCal(self, inputs):
		outputs = self.NetworkModel.predict([inputs])[0]
		

		temp =""
		for loop in range(len(outputs)):
			temp += str(loop)+": "+str(round(outputs[loop],2))+" "
		print(temp)

		largest = 0
		moveId = 0
		for loop in range(len(outputs)):
			if outputs[loop] > largest:
				moveId = loop
				largest = outputs[loop]
		
		outputMove = self.DataSetManager.MoveIDLookUp[moveId]
		return outputMove

	def UpdateInvalidMove(self, board, move):
		self.NetworkModel.fit(self.DataSetX, self.DataSetY, n_epoch=10, run_id=self.RunId)
		return

	def UpdateMoveOutCome(self, board, move, outComeBoard, gameFinished=False):				
		return

	def SaveData(self, fitness):
		weights = GetWeights(self.NetworkModel, self.NumberOfLayers)
		return

def ModelMaker(inputShape, structreArray, batchSize=20, lr=0.01, optimizer="adam"):
	tflearn.config.init_graph(gpu_memory_fraction=0.95, soft_placement=True)

	if len(inputShape) == 1:
		network = tflearn.input_data(shape=[None, inputShape[0] ], name='input')
	elif len(inputShape) == 2:
		network = tflearn.input_data(shape=[None, inputShape[0] , inputShape[1] ], name='input')
	elif len(inputShape) == 3:
		network = tflearn.input_data(shape=[None, inputShape[0] , inputShape[1] , inputShape[2] ], name='input')
	else:
		network = tflearn.input_data(shape=[None, inputShape[0] , inputShape[1] , inputShape[2] , inputShape[3] ], name='input')

	network = LayerMaker(network, structreArray)
	
	loss = loss='mean_square'
	#loss = "categorical_crossentropy"
	if optimizer == "adam":
		network = tflearn.regression(network, optimizer="adam", learning_rate=lr, batch_size=batchSize, loss=loss, name='target')
	else:
		sgd = tflearn.SGD(learning_rate = lr)
		network = tflearn.regression(network, optimizer=sgd, learning_rate=lr, batch_size=batchSize, loss=loss, name="target")
	
	model = tflearn.DNN(network, tensorboard_dir="log")
	return model
def LayerMaker(network, structreArray, layerNumber=0):
	layerName = "layer" + str(layerNumber)

	layerInfo = structreArray[layerNumber]

	if layerInfo[0] == "conv":
		network = tflearn.conv_2d(network, layerInfo[1], 3, activation=layerInfo[2], regularizer="L2", name=layerName)

	elif layerInfo[0] == "ann":
		network = tflearn.fully_connected(network, layerInfo[1], activation=layerInfo[2], bias=True, name=layerName)
		#network = tflearn.dropout(network, 0.8)

	elif layerInfo[0] == "maxpool":
		network = tflearn.max_pool_2d(network, layerInfo[1], name=layerName)

	elif layerInfo[0] == "rnn":
		network = tflearn.simple_rnn(network, layerInfo[1], activation=layerInfo[2], bias=True, name=layerName)

	elif  layerInfo[0] == "lstm":
		if len(layerInfo) > 2 and layerInfo[3] == "True":
			network = tflearn.lstm(network, layerInfo[1], activation=layerInfo[2], dropout=0.8, return_seq=True, name=layerName)
		else:
			network = tflearn.lstm(network, layerInfo[1], activation=layerInfo[2], return_seq=False, name=layerName)



	if len(structreArray) > layerNumber+1:
		network = LayerMaker(network, structreArray, layerNumber=layerNumber+1)

	return network

def GetWeights(model, numberOfLayers):
	weightsValue = []

	for loop in range(numberOfLayers):
		temp = tflearn.variables.get_layer_variables_by_name("layer"+str(loop))
		with model.session.as_default():
			temp[0] = tflearn.variables.get_value(temp[0])
			temp[1] = tflearn.variables.get_value(temp[1])
			weightsValue += [temp]
	return weightsValue
def SetWeights(model, numberOfLayers, newWeights):

	for loop in range(numberOfLayers):
		temp = tflearn.variables.get_layer_variables_by_name("layer"+str(loop))
		with model.session.as_default():
			tflearn.variables.set_value(temp[0],newWeights[loop][0])
			tflearn.variables.set_value(temp[1],newWeights[loop][1])
	return model
