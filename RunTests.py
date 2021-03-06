from Shared import Logger
import time
import RunController.eRenderType as eRenderType
import RunController.eLoadType as eLoadType
import RunController.RunController as runner
from Shared.OutputFormating import SplitTime, TimeToDateTime
from DataManger import BasicLoadAndSave
from Shared import BaseMetricsLogger
import RunController.AgentSetupData as AgentData
import RunController.eAgentType as eAgentType

class Tests:
	def __init__(self):
		self.MetaDataAddress = "Logs//TestOutputs_"
		self.MetaDataAddress += TimeToDateTime(time.time(), dateOn=True, 
				dateSplitter="_", dateTimeSplitter="_", timeSplitter="_")

		self.MetaDataAddress += "//"


		self.Logger = Logger.Logger()
		self.Logger.ClearAllowed = False
		self.Logger.SetTitleAllowed = False
		self.Logger.LoadingBarAllowed = False
		self.Logger.InputAllowed = False

		Sims = [1, 3, 4, 6]
		Agents = [AgentData.AgentSetupData(eAgentType.eAgentType.BruteForce, playingMode=False)]

		hadError = False
		timeMark = time.time()
		for simNum in Sims:
			for agent in Agents:
				if self.RunTest(simNum, agent):
					hadError = True

		print("Full Test Took: "+SplitTime(time.time()-timeMark))

		print("tests Finished")

		if hadError:
			exit(code=1)
		return


	def RunTest(self, simNum, agentData):
		agentType = agentData.GetType().name

		hadError = False
		print("")
		print("Setup Sim: "+str(simNum)+" With Agent: "+str(agentType))

		agentSetupData = []
		agentSetupData += [agentData]
		agentSetupData += [AgentData.AgentSetupData(eAgentType.eAgentType.BruteForce, playingMode=False)]

		try:
			timeMarkSetup = time.time()
			metricsLogger = BaseMetricsLogger.MetricsLogger("combined-ai-v3", False)

			controller = runner.RunController(self.Logger, metricsLogger, agentSetupData, simNumber=simNum, loadType=eLoadType.eLoadType.NotLoad,
			                                  renderQuality=eRenderType.eRenderType.Muted, stopTime=60)

			print("Setup Done Took: "+SplitTime(time.time()-timeMarkSetup))
			print("Sim = "+controller.SimInfo["SimName"])
			print("Starting Run...")
			timeMarkRun = time.time()

			controller.RunTraning()
			metaData1 = controller.DataManager.MetaData.Content

			address = self.MetaDataAddress+"MetaData_" +controller.SimInfo["SimName"]+"_"+agentType+"_1"
			BasicLoadAndSave.DictSave(address, metaData1)

			print("Run+Save Took: "+SplitTime(time.time()-timeMarkRun))
			print("Games Played: " + str(metaData1["NumberOfGames"]))
			print("Tried Moves Played: " + str(metaData1["TriedMovesPlayed"]))
			print("Vaild Moves Played: " + str(metaData1["VaildMovesPlayed"]))
			print("dataset size: " + str(metaData1["SizeOfDataSet"]))
			print("number complete boards: " + str(metaData1["NumberOfCompleteBoards"]))
			print("number finished boards: " + str(metaData1["NumberOfFinishedBoards"]))

			controller = runner.RunController(self.Logger, metricsLogger, agentSetupData, simNumber=simNum, loadType=eLoadType.eLoadType.Load,
			                                  renderQuality=eRenderType.eRenderType.Muted, stopTime=10)

			metaData2 = controller.DataManager.MetaData.Content
			address = self.MetaDataAddress+"MetaData_" + controller.SimInfo["SimName"]+"_"+agentType+"_2"
			BasicLoadAndSave.DictSave(address, metaData2)

			metaDataSame = True
			for key in metaData1.keys():
				if key not in metaData2 or metaData1[key] != metaData2[key]:
					metaDataSame = False
					break

			if not metaDataSame:
				self.Logger.LogWarning("sim: "+controller.SimInfo["SimName"]+" AI: " +agentType+" metaData1 != metaData2: save error?")
				hadError = True
			else:
				controller.RunTraning()

		except Exception as error:
			hadError = True
			self.Logger.LogError(error)

		return hadError


if __name__ == "__main__":
	Tests()
