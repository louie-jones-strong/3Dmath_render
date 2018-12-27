import BruteForce as AI
import importlib
import time
import os
import sys

from threading import Thread

def MakeAIMove(turn, board, AIs, game):
	AI = AIs[turn-1]
	valid = False
	if turn == 1:
		while not valid:
			move = AI.MoveCal(game.FlipBoard())
			flipedMove = game.FlipInput(move)
			valid, board = game.MakeSelection(flipedMove[0], flipedMove[1])
			if not valid:
				AI.UpdateInvalidMove(game.FlipBoard(), move)
			else:
				valid, board, turn = game.MakeMove(flipedMove[2], flipedMove[3])
				if not valid:
					AI.UpdateInvalidMove(game.FlipBoard(), move)
		
	else:
		while not valid:
			move = AI.MoveCal(board)
			valid, board = game.MakeSelection(move[0], move[1])
			if not valid:
				AI.UpdateInvalidMove(board, move)
			else:
				valid, board, turn = game.MakeMove(move[2], move[3])
				if not valid:
					AI.UpdateInvalidMove(board, move)
	return board, turn

class RunController(object):
	def __init__(self):
		files = os.listdir("Simulations")
		if "__pycache__" in files:
			files.remove("__pycache__")

		if "SimulationInterface.py" in files:
			files.remove("SimulationInterface.py")

		for loop in range(len(files)):
			files[loop] = files[loop][:-3]
			if len(files) > 1:
				print(str(loop+1)+") "+ files[loop])

		userInput = 1
		if len(files) > 1:
			userInput = int(input("pick Simulation: "))

		if userInput > len(files):
			userInput = len(files)

		if userInput < 1:
			userInput = 1

		simName = files[userInput-1]
		self.Sim = importlib.import_module("Simulations." + simName)
		datasetAddress = "DataSets//"+simName+"Dataset"

		userInput = input("load Dataset[Y/N]:")
		if userInput == "n" or userInput == "N":
			self.AiDataManager = AI.DataSetManager(4, 8, 1, datasetAddress, loadData=False)

		else:
			self.AiDataManager = AI.DataSetManager(4, 8, 1, datasetAddress, loadData=True)

		#setting 
		self.RenderQuality = 2
		self.NumberOfBots = 2

		self.WinningMode = False
		if self.NumberOfBots == 1:
			self.WinningMode = True


		if self.RenderQuality == 2:
			import RenderEngine
			self.RenderEngine = RenderEngine.RenderEngine()

		self.RunGame()
		return

	def Render(self, board=None, turn=None):
		if self.RenderQuality == 2:
			if board !=None and turn != None:
				self.RenderEngine.UpdateBoard(board, turn)
			#self.RenderEngine.UpdateFrame()
			Thread(target=self.RenderEngine.UpdateFrame()).start()
		return
	
	def MakeHumanMove(self, game):
		if self.RenderQuality == 2:
			board, turn = self.RenderEngine.MakeHumanMove(game)
		return board, turn

	def RunGame(self):
		game = self.Sim.Simulation()
		AIs = []
		AIs += [AI.BruteForce(self.AiDataManager, winningModeON=self.WinningMode)]
		AIs += [AI.BruteForce(self.AiDataManager, winningModeON=self.WinningMode)]
		board, turn = game.Start()

		self.Render(board=board, turn=turn)

		
		numGames = 0
		numMoves = 0

		timeSampleSize = 50
		moveTook = 0

		time_taken = time.time()
		MoveTime = time.time()
		while True:
			if self.NumberOfBots >= turn:
				board, turn = MakeAIMove(turn, board, AIs, game)
			else:
				board, turn = self.MakeHumanMove(game)

			self.Render(board=board, turn=turn)

			if self.RenderQuality == 2:
				self.RenderEngine.UpdateConsoleText("Dataset Size: "+str(len(self.AiDataManager.DataSet))+"\n Game: "+str(numGames)+"\n Move: "+str(numMoves)+"\n AVG time: "+str(moveTook))

			numMoves += 1
			if numMoves % timeSampleSize == 0 or self.RenderQuality == 1:
				moveTook = (time.time() - MoveTime)/timeSampleSize

				if self.RenderQuality == 1:
					print("done " + str(numMoves) + " moves, last took: " + str(time.time() - MoveTime) + " seconds")
				else: 
					print("done " + str(numMoves) + " moves took on AVG: " + str(moveTook) + " seconds")

				MoveTime = time.time()

			finished, fit = game.CheckFinished()
			if finished == False and numMoves >= 1000:
				finished = True
				fit = [3,3]

			if finished:

				print("")
				for loop in range(len(AIs)):
					AIs[loop].UpdateData(fit[loop])

				print("Dataset size: " + str(len(self.AiDataManager.DataSet)))
				print("finished game: " + str(numGames+1) + " with " + str(numMoves) + " moves made")
				print("each move took on AVG: " + str((time.time() - time_taken)/numMoves) + " seconds")
				print("game in total took: " + str(time.time() - time_taken) + " seconds")

				board, turn = game.Start()
				numGames += 1
				numMoves = 0

				print("")
				print("")
				time_taken = time.time()
				MoveTime = time.time()
		return

if __name__ == "__main__":
	RunController()