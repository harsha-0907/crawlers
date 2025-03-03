# A visual rerpresentation of the webpages using Networkx

import networkx as nx
import os
import json
from model import Url
import matplotlib.pyplot as plt

class Graph():
    def __init__(self, relativeGraphPath="results/web-graph.json", relativeUrlsPath="results/web-urls.json"):
        self.graph = nx.DiGraph()
        filePath = os.path.abspath(__file__)
        filePath = filePath[:filePath.rfind('/')]
        graphFilePath = os.path.join(filePath, relativeGraphPath)
        urlsFilePath = os.path.join(filePath,relativeUrlsPath)
        if not os.path.exists(graphFilePath) or not os.path.exists(urlsFilePath):
            print("Graph Not Found")
            exit()
        self.graphFilePath = graphFilePath
        self.urlsFilePath = urlsFilePath
        self.graph = nx.DiGraph()
    
    def intializeNodes(self):
        try:
            with open(self.graphFilePath, 'r', encoding="utf-8") as file:
                self.graphData = json.load(file)
            with open(self.urlsFilePath, 'r', encoding="utf-8") as file:
                self.reverseUrlsData = json.load(file)
        
        except Exception as _e:
            print(f"Error occured while loading json: {_e}")
    
    def addNodes(self):
        for node in self.reverseUrlsData:
            url = self.reverseUrlsData[node]
            self.graph.add_nodes_from([(node, {"Url": self.reverseUrlsData[node]})])
    
    def addEdges(self):
        for node, url in self.reverseUrlsData.items():
            if node not in self.graphData:
                toNodes = []
            else:
                toNodes = self.graphData[node]
            for toNode in toNodes:
                self.graph.add_edge(node, toNode)
    
    def plotGraph(self):
        self.intializeNodes()
        self.addNodes()
        self.addEdges()
        nx.draw(self.graph)
        plt.show()

g = Graph()
g.plotGraph()