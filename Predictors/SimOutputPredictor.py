#import Agents.NeuralNetwork as NeuralNetwork
from DataManger.Serializer import BoardToKey
import time
from Shared import OutputFormating as Format
import Predictors.PredictorBase as PredictorBase


class SimOutputPredictor(PredictorBase.PredictorBase):
	TrainedEpochs = 0
	NumWrongPredictions = 0

	def __init__(self, dataSetManager, loadData, trainingMode=False):
		super().__init__(dataSetManager, loadData)

		self.Predictions = {}

		#todo
		# networkModel, runId, numberOfLayers = NeuralNetwork.MakeModel(self.DataSetManager)
		# self.AnnModel = NeuralNetwork.NeuralNetwork(networkModel, numberOfLayers, 5000, runId)

		# if loadData:
		# 	found, weights = self.DataSetManager.LoadNetworkWeights()
		# 	if found:
		# 		self.AnnModel.SetWeights(weights)

		# if trainingMode:
		# 	self.Train()
		return

	def PredictOutput(self, board, move):
		newBoard = []

		key = BoardToKey(board)
		found, boardInfo = self.DataSetManager.GetBoardInfo(key)

		if found:
			moveID = self.DataSetManager.MoveIDLookUp.index(move)
			if moveID in boardInfo.Moves:
				with boardInfo.Lock:
					moveOutComes = boardInfo.Moves[moveID].MoveOutComes

					highestTimes = 0
					for outCome, times in moveOutComes.items():

						if highestTimes < times:
							newBoard = outCome
							highestTimes = times
		
		self.Predictions[str(key)+str(move)] = {"BoardKey": key, "Move": move, "Prediction": newBoard}
		self.NumPredictions += 1
		return newBoard

	def UpdateInvalidMove(self, boardKey, move):

		return

	def UpdateMoveOutCome(self, boardKey, move, outComeBoard, finished):

		if str(boardKey)+str(move) in self.Predictions:
			prediction = self.Predictions[str(boardKey)+str(move)]["Prediction"]

			outComeBoardKey = BoardToKey(outComeBoard)
			if finished:
				outComeBoardKey = "GameFinished"

			if prediction != outComeBoardKey:
				self.NumWrongPredictions += 1
		return

	def Train(self):
		dataSetX = []
		dataSetY = []

		while len(dataSetY) == 0:
			time.sleep(10)
			dataSetX, dataSetY = self.DataSetManager.GetSimPredictionDataSet()

		while True:
			self.TrainedEpochs += self.AnnModel.Train(dataSetX, dataSetY, trainingTime=60)
			
			weights = self.AnnModel.GetWeights()
			self.DataSetManager.SaveNetworkWeights("Sim", weights)
			dataSetX, dataSetY = self.DataSetManager.GetSimPredictionDataSet()

		return

	def PredictorInfoOutput(self):
		info = super().PredictorInfoOutput()
		info = ""
		info += "Number of Wrong predictions: "+Format.SplitNumber(self.NumWrongPredictions)
		if self.NumPredictions != 0:
			info += "\n"
			ratio = (1-(self.NumWrongPredictions/self.NumPredictions))*100
			info += "predictions ratio: "+str(round(ratio,ndigits=2))+"%"

		return info
