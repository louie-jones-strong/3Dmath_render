import DataManger.BoardInfo as BoardInfo
import DataManger.MoveInfo as MoveInfo
from DataManger.Serializer import BoardToKey
from Shared import OutputFormating as Format

class AgentBase:
	AgentType = "Base"
	NumInvailds = 0
	NumMoves = 0
	NumGames = 1
	AgentNumber = 0

	def __init__(self, dataSetManager, loadData, winningModeON=False):
		self.DataSetManager = dataSetManager
		self.WinningModeON = winningModeON
		self.TempDataSet = {}
		self.MoveNumber = 0
		self.RecordMoves = True
		self.TotalFittness = 0
		
		self.AllMovesPlayedValue = (2**self.DataSetManager.MaxMoveIDs)-1

		if loadData:
			self.DataSetManager.LoadTableInfo()
		return
	
	def MoveCal(self, board):

		return

	def MoveListCal(self, board):
		
		return [self.MoveCal(board)]

	def RecordMove(self, board, move):
		if not self.RecordMoves:
			return

		self.DataSetManager.MetaDataAdd("TriedMovesPlayed", 1)

		key = BoardToKey(board)
		moveID = self.DataSetManager.MoveIDLookUp.index(move)
		found, boardInfo = self.DataSetManager.GetBoardInfo(key)

		if not found:  # never played board before
			self.DataSetManager.AddNewBoard(key, board)
			found, boardInfo = self.DataSetManager.GetBoardInfo(key)
		
		with boardInfo.Lock:
			boardInfo.BeingUsed = True
			# never played this move before
			if moveID not in boardInfo.Moves:
				boardInfo.Moves[moveID] = MoveInfo.MoveInfo()

			# mark move as played if never played before
			if boardInfo.PlayedMovesLookUpArray < self.AllMovesPlayedValue:

				if not (2**moveID & boardInfo.PlayedMovesLookUpArray):
					boardInfo.PlayedMovesLookUpArray += 2**moveID

				if boardInfo.PlayedMovesLookUpArray >= self.AllMovesPlayedValue:
					self.DataSetManager.MetaDataAdd("NumberOfCompleteBoards", 1)
				

		if self.RecordMoves:
			self.TempDataSet[str(key)+str(moveID)] = {"BoardKey": key, "MoveID": moveID, "MoveNumber":self.MoveNumber}
			self.MoveNumber += 1

		return

	def UpdateInvalidMove(self, board, move):
		if not self.RecordMoves:
			return

		key = BoardToKey(board)
		moveID = self.DataSetManager.MoveIDLookUp.index(move)

		found, boardInfo = self.DataSetManager.GetBoardInfo(key)
		if found:
			with boardInfo.Lock:
				if moveID in boardInfo.Moves:
					del boardInfo.Moves[moveID]

		if str(key)+str(moveID) in self.TempDataSet:
			del self.TempDataSet[str(key)+str(moveID)]

		self.MoveNumber -= 1

		self.NumInvailds += 1
		return

	def UpdateMoveOutCome(self, boardKey, move, outComeBoard, gameFinished=False):
		if not self.RecordMoves:
			return
		
		self.DataSetManager.MetaDataAdd("VaildMovesPlayed", 1)
		moveID = self.DataSetManager.MoveIDLookUp.index(move)
		found, boardInfo = self.DataSetManager.GetBoardInfo(boardKey)
		
		with boardInfo.Lock:
			if found and moveID in boardInfo.Moves:
				if gameFinished:
					outComeKey = "GameFinished"
				else:
					outComeKey = BoardToKey(outComeBoard)
	
				move = boardInfo.Moves[moveID]
				boardInfo.BeingUsed = False
				if outComeKey in move.MoveOutComes:
					move.MoveOutComes[outComeKey] += 1
				else:
					move.MoveOutComes[outComeKey] = 1
		
		self.NumMoves += 1
		return

	def GameFinished(self, fitness):
		self.TotalFittness += fitness
		
		if not self.RecordMoves:
			return
		
		TempDataSetList = []

		for tempValue in self.TempDataSet.values():
			TempDataSetList += [tempValue]

		TempDataSetList.sort(key=GetSortKey, reverse=True)

		for tempValue in TempDataSetList:
			key = tempValue["BoardKey"]
			moveID = tempValue["MoveID"]

			found, boardInfo = self.DataSetManager.GetBoardInfo(key)
			if found:
				with boardInfo.Lock:

					# add fittness to total move fittness
					if moveID in boardInfo.Moves:
						newFitness = boardInfo.Moves[moveID].AvgFitness*boardInfo.Moves[moveID].TimesPlayed
						newFitness += fitness
						boardInfo.Moves[moveID].TimesPlayed += 1
						newFitness /= boardInfo.Moves[moveID].TimesPlayed
						boardInfo.Moves[moveID].AvgFitness = newFitness

						if newFitness > boardInfo.BestAvgFitness:
							boardInfo.MoveIDOfBestAvgFitness = moveID
							boardInfo.BestAvgFitness = newFitness

						if not boardInfo.Finished:
							boardInfo.Finished = self.IsBoardFinished(boardInfo)
							if boardInfo.Finished:
								self.DataSetManager.MetaDataAdd("NumberOfFinishedBoards", 1)

					
					# add fittness to total board fittness
					newFitness = boardInfo.TotalAvgFitness*boardInfo.TotalTimesPlayed
					newFitness += fitness
					boardInfo.TotalTimesPlayed += 1
					newFitness /= boardInfo.TotalTimesPlayed
					boardInfo.TotalAvgFitness = newFitness


		self.TempDataSet = {}
		self.MoveNumber = 0
		self.NumGames += 1
		return

	def TournamentFinished(self):
		
		return

	def IsBoardFinished(self, boardInfo):
		if boardInfo.Finished:
			return True

		if boardInfo.PlayedMovesLookUpArray < self.AllMovesPlayedValue:
			return False
		
		for moveId in range(self.DataSetManager.MaxMoveIDs):
			if moveId in boardInfo.Moves:
				if not self.IsMoveFinished(boardInfo, moveId):
					return False
						
		
		return True

	def IsMoveFinished(self, boardInfo, moveId):
		if boardInfo.Finished:
			return True

		if not (2**moveId & boardInfo.PlayedMovesLookUpArray):
			return False

		if moveId in boardInfo.Moves:

			for outComeKey in boardInfo.Moves[moveId].MoveOutComes:

				if outComeKey != "GameFinished":
					found, outComeBoardInfo = self.DataSetManager.GetBoardInfo(outComeKey)
					if not found:
						return False
					
					if not outComeBoardInfo.Finished:
						return False
			
		return True		

	def IsMoveLocked(self, boardInfo, moveId):
		if not (2**moveId & boardInfo.PlayedMovesLookUpArray):
			return False

		if moveId in boardInfo.Moves:

			for outComeKey in boardInfo.Moves[moveId].MoveOutComes:

				if outComeKey != "GameFinished":
					found, outComeBoardInfo = self.DataSetManager.GetBoardInfo(outComeKey)
					if not found:
						return False
					
					if outComeBoardInfo.BeingUsed or outComeBoardInfo.Lock.locked():
						return True
			
		return False		

	def AgentInfoOutput(self):
		info = ""
		
		fitPerGame = self.TotalFittness
		perGame = self.NumInvailds
		if self.NumGames > 0:
			perGame = self.NumInvailds/self.NumGames
			fitPerGame = self.TotalFittness/self.NumGames

		perMove = self.NumInvailds
		if self.NumMoves > 0:
			perMove = self.NumInvailds/self.NumMoves

		info += "Avg Fittness per Game: "+str(round(fitPerGame))
		info += "\n"
		info += "Avg Invalids per Game: "+str(round(perGame))
		info += "\n"
		info += "Avg Invalids Per move: "+str(round(perMove))
		info += "\n"
		info += "moves played: "+Format.SplitNumber(self.NumMoves)

		return info

def GetSortKey(val):
	return val["MoveNumber"]
