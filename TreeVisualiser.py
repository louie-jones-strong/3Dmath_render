import matplotlib.pyplot as plt
import networkx as nx
import time

class TreeVisualiser:

	def __init__(self, dataSetManager):
		self.DataSetManager = dataSetManager
		self.DataSetManager.LoadTableInfo()
		startBoard = "[0, 0, 0, 0, 0, 0, 0, 0, 0]"
		self.Tree = nx.Graph()
		self.Tree.add_node(startBoard)
		self.Pos = {}
		self.DepthNumNodes = {}
		self.Labels = {}
		self.FinishedNodes = []
		self.NonFinishedNodes = []
		self.MaxDepth = 12
		self.EdgeCapPerNode = 3

		self.LastOutput = time.time()
		self.BuildTree(startBoard)
		self.DataSetManager.Clear()
		self.ShowTree()
		return
	
	def BuildTree(self, key, depth=0):
		if key in self.Labels:
			return

		if depth not in self.DepthNumNodes:
			self.DepthNumNodes[depth] = 0

		x = self.DepthNumNodes[depth]
		if x % 2 == 0:
			x *= -1
		x /= 2
		y = -depth*100

		self.Pos[key] = [x,y]
		self.DepthNumNodes[depth] += 1
		self.Labels[key] = key

		found, boardInfo = self.DataSetManager.GetBoardInfo(key)
		if found:
			if boardInfo.Finished:
				self.FinishedNodes += [key]
			else:
				self.NonFinishedNodes += [key]

			if time.time() - self.LastOutput >= 1:
				self.ShowTree()
				self.LastOutput = time.time()

			if depth <= self.MaxDepth:
				edges = 0
				for movekey, moveValue in boardInfo.Moves.items():
					for outComesKey, outComesValue in moveValue.MoveOutComes.items():
						if edges < self.EdgeCapPerNode:
							self.Tree.add_edge(key, outComesKey)
							edges += 1
						self.BuildTree(outComesKey, depth+1)
		else:
			self.FinishedNodes += [key]
		return

	def ShowTree(self):

		#plt.subplot()
		plt.plot()

		nx.draw_networkx_nodes(self.Tree, self.Pos, nodelist=self.NonFinishedNodes, node_color='r', node_size=100)
		nx.draw_networkx_nodes(self.Tree, self.Pos, nodelist=self.FinishedNodes, node_color='g', node_size=100)
		# edges
		nx.draw_networkx_edges(self.Tree, self.Pos, alpha=0.5)

		#nx.draw_networkx_labels(self.Tree, self.Pos, self.Labels)

		print("Nodes: "+str(self.Tree.number_of_nodes()))
		print("edges: "+str(self.Tree.number_of_edges()))
		plt.axis('off')
		#plt.savefig("tree.svg", transparent=False)
		plt.show()
		return