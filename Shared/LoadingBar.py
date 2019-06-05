import time
import os
import Shared.OutputFormating as Formating

class LoadingBar():

	def __init__(self, allowUpdate=True):
		self.CurrentProgress = 0
		self.CurrentText = ""
		self.Resolution = 100
		self.LastUpdateTime = 0
		self.AllowUpdate = allowUpdate
		return

	def Update(self, progress, numDone=None, totalNum=None, text=""):
		progress = max(progress, 0)
		progress = min(progress, 1)

		progress = int(progress*self.Resolution)

		if time.time()-self.LastUpdateTime >= 0.15 or progress == self.Resolution:
			if progress != self.CurrentProgress or text != self.CurrentText:
				os.system("cls")
				bar = "#"*progress
				fill = " "*(self.Resolution-progress)
				print("|"+bar+fill+"|")
				print(text)
				
				if numDone != None and totalNum != None:
					output = Formating.SplitNumber(numDone)
					output += "/"
					output += Formating.SplitNumber(totalNum)
					output += " "+round(progress, 2)+"%"

					print(output)

				self.CurrentProgress = progress
				self.CurrentText = text
				self.LastUpdateTime = time.time()
		return
