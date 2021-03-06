import Simulations.SimulationBase as SimBase


class Simulation(SimBase.SimBase):
	Info = {"MinPlayers":2,"MaxPlayers":2,
	        "SimName":"ConnectFour","NumInputs":1,
			"MinInputSize":0,"MaxInputSize":6,
			"Resolution":1,"RenderSetup":True}

	def __init__(self, index=None):
		self.Index = 0

		gridSizeList = [(7,6), (4,4)]
		if index == None:
			for loop in range(len(gridSizeList)):
				print(str(loop)+") X="+str(gridSizeList[loop][0])+" Y="+str(gridSizeList[loop][1]))

			index = int(input("pick grid shape: "))

		self.Index = index
		self.Grid = gridSizeList[index]
		self.Info["MaxInputSize"] = self.Grid[0]-1
		self.Info["SimName"] = "ConnectFour"+str(self.Grid)
		return

	def CreateNew(self):
		sim = Simulation(self.Index)
		return sim

	def Start(self):
		self.Board = []
		for loop in range(self.Grid[0]):
			temp = []
			for loop2 in range(self.Grid[1]):
				temp += [0]

			self.Board += [temp]

		self.Turn = 1
		self.MoveNum = 0
		return self.Board, self.Turn

	def MakeMove(self,inputs):
		valid = False

		column = inputs[0]

		if self.Board[column][0] == 0:
			temp = 0
			valid = True
			for loop in range(1,len(self.Board[column])):

				if (self.Board[column][loop] == 0):
					temp = loop
				else:
					break
			
			self.Board[column][temp] = self.Turn
				
		
		if valid:
			if self.Turn == 1:
				self.Turn = 2
			else:
				self.Turn = 1

			self.MoveNum += 1
		return valid, self.Board, self.Turn

	def CheckFinished(self):
		player1Fitness, player2Fitness = 0,0
		finished = False

		if self.MoveNum >= 7:
			won, side = WinCheck(self.Board)
			if won:
				if (side == 1):#win
					finished = True
					player1Fitness = 5
					player2Fitness = -5

				elif (side == 2):#loss
					finished = True
					player1Fitness = -5
					player2Fitness = 5

				elif side == 0:#draw
					finished = True
					player1Fitness = 3
					player2Fitness = 3
			
		return finished, [player1Fitness, player2Fitness]

	def FlipBoard(self, board):
		output = []
		for X in range(len(board)):
			temp = []
			for Y in range(len(board[X])):
				if board[X][Y] == 1:
					temp += [2]
				elif board[X][Y] == 2:
					temp += [1]
				else:
					temp += [0]

			output += [temp]

		return output

	def FlipInput(self, move):
		return move

	def SimpleBoardOutput(self, board):
		for Y in range(len(board[0])):
			temp = "|"
			for X in range(len(board)):
				if board[X][Y] == 1:
					temp += "O"
				elif board[X][Y] == 2:
					temp += "X"
				else:
					temp += " "
				temp += "|"

			print(temp)
		print("|0|1|2|3|4|5|6|")
		return

	def ComplexOutputSetup(self):
		import RenderEngine.Shape as Shape
		import RenderEngine.Piece.PolygonPiece as Piece
		super().ComplexOutputSetup()
		gridSize = 40
		self.BackGroundpieceList += [Piece.PolygonPiece([350, 350], [self.Grid[0]*gridSize, self.Grid[1]*gridSize], Shape.Square(), [0, 0, 255])]
		return

	def ComplexBoardOutput(self, board):
		import RenderEngine.Shape as Shape
		import RenderEngine.Piece.PolygonPiece as Piece

		super().ComplexBoardOutput(board)
		pieceSize = 30
		gridSize = 40

		pieceList = []
		pieceList += self.BackGroundpieceList
		for x in range(self.Grid[0]):
			for y in range(self.Grid[1]):
				if board[x][y] == 0:
					pieceList += [Piece.PolygonPiece([((x+0.5)-self.Grid[0]/2)*gridSize*2+350, ((y+0.5)-self.Grid[1]/2)
                                               * gridSize*2+350], [35, 35], Shape.Circle(), [0, 0, 0])]
				elif board[x][y] == 1:
					pieceList += [Piece.PolygonPiece([((x+0.5)-self.Grid[0]/2)*gridSize*2+350, ((y+0.5)-self.Grid[1]/2)
                                                * gridSize*2+350], [pieceSize, pieceSize], Shape.Circle(), [255, 0, 0])]
				else:
					pieceList += [Piece.PolygonPiece([((x+0.5)-self.Grid[0]/2)*gridSize*2+350, ((y+0.5)-self.Grid[1]/2)
                                               * gridSize*2+350], [pieceSize, pieceSize], Shape.Circle(), [0, 255, 0])]
		return pieceList

def WinCheck(board):
	won = False
	side = 0
	foundZero = False
	for X in range(len(board)):
		for Y in range(len(board[X])):

			if board[X][Y] != 0:
				for turn in [1,2]:
					if X < len(board)-3:
						if board[X][Y] == turn and board[X+1][Y] == turn \
						and board[X+2][Y] == turn and board[X+3][Y] == turn:
							won = True
							side = turn
							return won, side

						if Y < len(board[X])-3:
							if board[X][Y] == turn and board[X+1][Y+1] == turn \
							and board[X+2][Y+2] == turn and board[X+3][Y+3] == turn:
								won = True
								side = turn
								return won, side

					if Y < len(board[X])-3:
						if board[X][Y] == turn and board[X][Y+1] == turn \
						and board[X][Y+2] == turn and board[X][Y+3] == turn:
							won = True
							side = turn
							return won, side

					if X > 2:
						if Y > 2:
							if board[X][Y] == turn and board[X-1][Y-1] == turn \
							and board[X-2][Y-2] == turn and board[X-3][Y-3] == turn:
								won = True
								side = turn
								return won, side
			
			else:
				foundZero = True

				
	if not won and not foundZero:
		won = True
		side = 0

	return won, side
