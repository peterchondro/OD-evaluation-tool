import sys
import os
import re
import cv2
import time
import math
import linecache
import numpy as np
from PyQt5.QtCore import *
import PyQt5.QtWidgets as qws
from PyQt5.QtGui import *
import xlrd
import xlwt
from xlutils.copy import copy as cp
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random

np.seterr(divide='ignore',invalid='ignore')

class PlotCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		plt.style.use('seaborn-whitegrid') #https://tonysyu.github.io/raw_content/matplotlib-style-gallery/gallery.html
		
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
 
		FigureCanvas.setSizePolicy(self,
				qws.QSizePolicy.Expanding,
				qws.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		#self.bar()

	def plot(self, title = None, data = None):
		self.clear()
		data = [random.random()*100 for i in range(25)]
		#ax = self.figure.add_subplot(111)
		self.axes.plot(data, 'r-')
		self.axes.set_title(title)
		self.draw()

	def bar(self, title = None, x_data = None, y_data=None):
		self.clear()
		if(x_data == None):
			x_data = [i for i in range(10)]
		if (y_data == None):
			y_data = [int(random.random()*100) for i in range(len(x_data))]
		y_data = np.array(y_data)
		y_data[y_data == -1] = 0
		y_data = y_data.tolist()
		
		#ax = self.figure.add_subplot(111)
		self.axes.bar(x_data, y_data, width=0.2)
		for tick in self.axes.get_xticklabels():
			tick.set_rotation(15)

		self.axes.set_yticks(y_data)
		self.axes.set_title(title)
		self.draw()
		
	def clear(self):
		self.axes.clear()
		self.draw()

class AnalysisThread_2D(QThread):
	update = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	end = pyqtSignal()
	def __init__(self, GT_path, Result_path, header_class, weighted_parameters):
		QThread.__init__(self)

		self.GT_path = GT_path
		self.Result_path = Result_path
		self.header_class = header_class
		self.class_num = len(header_class)
		self.ERHist = [0 for x in range(self.class_num)]
		self.lACC = [0 for x in range(self.class_num)]
		self.lFPR = [0 for x in range(self.class_num)]
		self.lFNR = [0 for x in range(self.class_num)]
		self.weighted_parameters =  weighted_parameters
		self.gACC = 0.0
		self.gFPR = 0.0
		self.gFNR = 0.0
		self.gSum = 0.0
		self.img_width = 416
		self.img_height = 256

	def __del__(self):
		self.wait()

	def Calculate_Acc(self):
		pass

	def run(self):
		gtDet, n_gtDet = self.readDet_2DGT()
		rsDet, n_rsDet = self.readDet_2DRS()
		GT, TP, FP, FN, ER = self.BB2DEvaluation(gtDet, n_gtDet, rsDet, n_rsDet)
		max_error = 0
		best_error = 0
		for k in range(self.class_num):
			if(self.weighted_parameters[k] == 0):
				continue
			if(GT[k] == 0):
				self.lACC[k] = -1
				self.lFPR[k] = -1
				self.lFNR[k] = -1
			else:
				self.lACC[k] = TP[k] / GT[k];
				self.lFPR[k] = FP[k] / GT[k];
				self.lFNR[k] = FN[k] / GT[k];
				# if(k!=4 and k!=8):#4Person_sitting8DontCare
				self.gFPR += self.lFPR[k]
				self.gFNR += self.lFNR[k]
				self.gACC += self.lACC[k]
				self.gSum+=1
			for l in range(self.class_num):
				if(k != l):
					if(ER[k][l] > max_error):
						max_error = ER[k][l]
						best_error = l
			if(max_error == 0):
				if(GT[k] == 0):
					self.ERHist[k] = -1
				else:
					self.ERHist[k] = k
			else:
				self.ERHist[k] = best_error
		if(FP[self.class_num] != 0):
			self.gFPR /= (self.gSum + 1)
		else:
			self.gFPR /= self.gSum
		self.gACC /= self.gSum
		self.gFNR /= self.gSum
		Accuracy_Text = "Accuracy = {0}\n".format(self.gACC)
		self.update.emit(GT, TP, FP, FN, self.lACC, self.lFPR, self.lFNR, self.gACC, 0, self.gFPR, self.gFNR, self.ERHist)
		self.end.emit()

	def readDet_2DGT(self):
		file=open(self.GT_path)
		lines=file.readlines() 
		det_num=len(lines)
		det_dtl = np.zeros((det_num, 6), dtype=np.int64)
		i = -1
		for line in lines:
			if (len(line) > 3):
				a = line.split()
				i+=1
				for j in range(4):
					det_dtl[i][j] = a[j + 1]
				var_x = det_dtl[i][0]
				var_y = det_dtl[i][1]
				class_index = int(a[0])
				if(var_x < 0):
					det_dtl[i][0] = 0
				elif(var_x > self.img_width):
					det_dtl[i][0] = self.img_width
				if(var_y < 0):
					det_dtl[i][1] = 0
				elif(var_y > self.img_height):
					det_dtl[i][1] = self.img_height
				if(class_index < self.class_num):
					det_dtl[i][4] = class_index
					det_dtl[i][5] = 1
				else:
					det_dtl[i][4] = -1
					det_dtl[i][5] = 0
		det_num = i + 1
		return det_dtl, det_num

	def readDet_2DRS(self):
		file=open(self.Result_path)
		lines=file.readlines() 
		det_num=len(lines)
		det_dtl = np.zeros((det_num, 6), dtype=np.int64)
		i = -1
		for line in lines:
			if (len(line) > 3):
				a = line.split()
				i+=1
				for j in range(4):
					det_dtl[i][j] = a[j + 1]
				var_x = det_dtl[i][0]
				var_y = det_dtl[i][1]
				class_index = int(a[0])
				if(var_x < 0):
					det_dtl[i][0] = 0
				elif(var_x > self.img_width):
					det_dtl[i][0] = self.img_width
				if(var_y < 0):
					det_dtl[i][1] = 0
				elif(var_y > self.img_height):
					det_dtl[i][1] = self.img_height
				if(class_index < self.class_num):
					det_dtl[i][4] = class_index
					det_dtl[i][5] = 1
				else:
					det_dtl[i][4] = -1
					det_dtl[i][5] = 0
		det_num = i + 1
		return det_dtl, det_num

	def BB2DEvaluation(self, gtBB, n_gtBB, rsBB, n_rsBB):
		pairStatusRS = np.zeros(n_rsBB, dtype=bool)
		nGT = np.zeros(self.class_num , dtype=np.int64)
		nTP = np.zeros(self.class_num , dtype=np.int64)
		nFP = np.zeros((self.class_num + 1) , dtype=np.int64)
		nFN = np.zeros(self.class_num , dtype=np.int64)
		hER = np.zeros((self.class_num , self.class_num ), dtype=np.int64)
		x_res = 0.01
		y_res = 0.01
		IOU_th = 0.15
		for n in range(n_gtBB):
			loneCounter = 0
			IOU_score = -1
			x_startGT = gtBB[n][0]
			x_stopGT = gtBB[n][2]
			y_startGT = gtBB[n][1]
			y_stopGT = gtBB[n][3]
			x_cntGT = (x_stopGT + x_startGT) / 2
			y_cntGT = (y_stopGT + y_startGT) / 2
			classGT = gtBB[n][4]
			nGT[classGT]+=1
			gtWidth = gtBB[n][2] - gtBB[n][0]
			gtHeight = gtBB[n][3] - gtBB[n][1]
			if(gtWidth > gtHeight):
				th_dt = gtWidth
			else:
				th_dt = gtHeight
			for r in range(n_rsBB):
				x_startRS = rsBB[r][0]
				x_stopRS = rsBB[r][2]
				y_startRS = rsBB[r][1]
				y_stopRS = rsBB[r][3]
				x_cntRS = (x_stopRS + x_startRS) / 2
				y_cntRS = (y_stopRS + y_startRS) / 2
				classRS = rsBB[r][4]
				x_aux = x_cntGT - x_cntRS
				y_aux = y_cntGT - y_cntRS
				xy_dt = math.sqrt((x_aux * x_aux) + (y_aux * y_aux))
				if(xy_dt < th_dt):
					intersection = 0
					for y in np.arange(y_startGT, y_stopGT):
						for x in np.arange(x_startGT, x_stopGT):
							if(x > x_startRS and x < x_stopRS):
								if(y > y_startRS and y < y_stopRS):
									intersection+=1
					inArea = intersection
					gtArea = (gtBB[n][2] - gtBB[n][0]) * (gtBB[n][3] - gtBB[n][1])
					rsArea = (rsBB[r][2] - rsBB[r][0]) * (rsBB[r][3] - rsBB[r][1])
					if(inArea > gtArea or inArea > rsArea):
						if(gtArea > rsArea):
							inArea = rsArea
						else:
							inArea = gtArea
					unArea = gtArea + rsArea - inArea
					score = inArea / unArea
					if(IOU_score < score):
						IOU_score = score
						pairOptimum = r
				else:
					loneCounter+=1
			if(loneCounter == n_rsBB):
				nFN[classGT]+=1
			else:
				if(IOU_score > IOU_th):
					classRS = rsBB[pairOptimum][4]
					pairStatusRS[pairOptimum]=True
					if(classRS == -1):
						nFN[classGT]+=1
					else:
						if(classGT == classRS):
							nTP[classGT]+=1
						else:
							nFN[classGT]+=1
							hER[classGT][classRS]+=1
				else:
					nFN[classGT]+=1
		for r in range(n_rsBB):
			if(pairStatusRS[r] == False):
				classRS = int(rsBB[r][4])
				if(classRS == -1):
					nFP[self.class_num]+=1
				else:
					nFP[classRS]+=1
		return nGT, nTP, nFP, nFN, hER

class AnalysisDataSetThread_2D(QThread):
	update = pyqtSignal(object, object, object, object, object, object, object, object, object, object, object, object)
	progress = pyqtSignal(int)
	setmaxprogress = pyqtSignal(int)
	end = pyqtSignal(bool)
	test = pyqtSignal(list)
	def __init__(self, GT_path, Result_path, header_class, weighted_parameters):
		QThread.__init__(self)
		self.img_width = 416
		self.img_height = 256
		self.GT_path = GT_path
		self.Result_path = Result_path
		self.header_class = header_class
		self.class_num = len(header_class)
		self.GT = np.zeros(self.class_num, dtype=np.int64)
		self.TP = np.zeros(self.class_num, dtype=np.int64)
		self.FP = np.zeros((self.class_num + 1), dtype=np.int64)
		self.FN = np.zeros(self.class_num, dtype=np.int64)
		self.weighted_parameters =  weighted_parameters
		self.lACC = [0 for x in range(self.class_num)]
		self.lFPR = [0 for x in range(self.class_num)]
		self.lFNR = [0 for x in range(self.class_num)]
		self.ER = np.zeros((self.class_num, self.class_num), dtype=np.int64)
		self.ERHist = [0 for x in range(self.class_num)]
		self.gACC = 0.0
		self.wgACC = 0.0
		self.gFPR = 0.0
		self.gFNR = 0.0
		self.gSum = 0.0
		self.Accuracy_Text = ""

	def __del__(self):
		self.wait()
	
	def _checkisfolder(self, path):
		if(os.path.isdir(path) is not True):
			return os.path.dirname(path)
		return path
	
	def _pairgtandresult(self, gt, result):
		pair_gt = []
		pair_result = []
		for gt_file in gt:
			for result_file in result:
				if (os.path.splitext(gt_file)[0] == os.path.splitext(result_file)[0]):
					pair_gt.append(gt_file)
					pair_result.append(result_file)
					break
		self.test.emit([len(pair_result)])
		return pair_gt, pair_result
	
	def _analysis(self, gt, result, nameref):
		self.file_gt = gt
		self.file_result = result
		gtDet, n_gtDet = self.readDet_2DGT()
		rsDet, n_rsDet = self.readDet_2DRS()
		self.BB2DEvaluation(gtDet, n_gtDet, rsDet, n_rsDet, nameref)

	def readDet_2DGT(self):
		file=open(self.file_gt)
		lines=file.readlines() 
		det_num=len(lines)
		det_dtl = np.zeros((det_num, 6), dtype=np.int64)
		i = -1
		for line in lines:
			if (len(line) > 3):
				a = line.split()
				i+=1
				for j in range(4):
					det_dtl[i][j] = a[j + 1]
				var_x = det_dtl[i][0]
				var_y = det_dtl[i][1]
				class_index = int(a[0])
				if(var_x < 0):
					det_dtl[i][0] = 0
				elif(var_x > self.img_width):
					det_dtl[i][0] = self.img_width
				if(var_y < 0):
					det_dtl[i][1] = 0
				elif(var_y > self.img_height):
					det_dtl[i][1] = self.img_height
				if(class_index < self.class_num):
					det_dtl[i][4] = class_index
					det_dtl[i][5] = 1
				else:
					det_dtl[i][4] = -1
					det_dtl[i][5] = 0
		det_num = i + 1
		return det_dtl, det_num

	def readDet_2DRS(self):
		file=open(self.file_result)
		lines=file.readlines() 
		det_num=len(lines)
		det_dtl = np.zeros((det_num, 6), dtype=np.int64)
		i = -1
		for line in lines:
			if (len(line) > 3):
				a = line.split()
				i+=1
				for j in range(4):
					det_dtl[i][j] = a[j + 1]
				var_x = det_dtl[i][0]
				var_y = det_dtl[i][1]
				class_index = int(a[0])
				if(var_x < 0):
					det_dtl[i][0] = 0
				elif(var_x > self.img_width):
					det_dtl[i][0] = self.img_width
				if(var_y < 0):
					det_dtl[i][1] = 0
				elif(var_y > self.img_height):
					det_dtl[i][1] = self.img_height
				if(class_index < self.class_num):
					det_dtl[i][4] = class_index
					det_dtl[i][5] = 1
				else:
					det_dtl[i][4] = -1
					det_dtl[i][5] = 0
		det_num = i + 1
		return det_dtl, det_num

	def BB2DEvaluation(self, gtBB, n_gtBB, rsBB, n_rsBB, nameref):
		pairStatusRS = np.zeros(n_rsBB, dtype=bool)
		nGT = np.zeros(self.class_num , dtype=np.int64)
		nTP = np.zeros(self.class_num , dtype=np.int64)
		nFP = np.zeros((self.class_num + 1) , dtype=np.int64)
		nFN = np.zeros(self.class_num , dtype=np.int64)
		hER = np.zeros((self.class_num , self.class_num ), dtype=np.int64)
		x_res = 0.01
		y_res = 0.01
		IOU_th = 0.005
		for n in range(n_gtBB):
			loneCounter = 0
			IOU_score = -1
			x_startGT = gtBB[n][0]
			x_stopGT = gtBB[n][2]
			y_startGT = gtBB[n][1]
			y_stopGT = gtBB[n][3]
			x_cntGT = (x_stopGT + x_startGT) / 2
			y_cntGT = (y_stopGT + y_startGT) / 2
			classGT = gtBB[n][4]
			self.GT[classGT]+=1
			gtWidth = gtBB[n][2] - gtBB[n][0]
			gtHeight = gtBB[n][3] - gtBB[n][1]
			if(gtWidth > gtHeight):
				th_dt = gtWidth
			else:
				th_dt = gtHeight
			for r in range(n_rsBB):
				x_startRS = rsBB[r][0]
				x_stopRS = rsBB[r][2]
				y_startRS = rsBB[r][1]
				y_stopRS = rsBB[r][3]
				x_cntRS = (x_stopRS + x_startRS) / 2
				y_cntRS = (y_stopRS + y_startRS) / 2
				classRS = rsBB[r][4]
				x_aux = x_cntGT - x_cntRS
				y_aux = y_cntGT - y_cntRS
				xy_dt = math.sqrt((x_aux * x_aux) + (y_aux * y_aux))
				if(xy_dt < th_dt):
					intersection = 0
					for y in np.arange(y_startGT, y_stopGT):
						for x in np.arange(x_startGT, x_stopGT):
							if(x > x_startRS and x < x_stopRS):
								if(y > y_startRS and y < y_stopRS):
									intersection+=1
					inArea = intersection
					gtArea = (gtBB[n][2] - gtBB[n][0]) * (gtBB[n][3] - gtBB[n][1])
					rsArea = (rsBB[r][2] - rsBB[r][0]) * (rsBB[r][3] - rsBB[r][1])
					if(inArea > gtArea or inArea > rsArea):
						if(gtArea > rsArea):
							inArea = rsArea
						else:
							inArea = gtArea
					unArea = gtArea + rsArea - inArea
					score = inArea / unArea
					if(IOU_score < score):
						IOU_score = score
						pairOptimum = r
				else:
					loneCounter+=1
			if(loneCounter == n_rsBB):
				self.FN[classGT]+=1
				nFN[classGT]+=1
			else:
				if(IOU_score > IOU_th):
					classRS = rsBB[pairOptimum][4]
					pairStatusRS[pairOptimum]=True
					if(classRS == -1):
						self.FN[classGT]+=1
						nFN[classGT]+=1
					else:
						if(classGT == classRS):
							self.TP[classGT]+=1
							nTP[classGT]+=1
						else:
							self.FN[classGT]+=1
							nFN[classGT]+=1
							self.ER[classGT][classRS]+=1
				else:
					self.FN[classGT]+=1
					nFN[classGT]+=1
		for r in range(n_rsBB):
			if(pairStatusRS[r] == False):
				classRS = int(rsBB[r][4])
				if(classRS == -1):
					self.FP[self.class_num]+=1
					nFP[self.class_num]+=1
				else:
					self.FP[classRS]+=1
					nFP[classRS]+=1
		#nTPR = (nTP[0]+nTP[1]+nTP[2]+nTP[3])/(nTP[0]+nTP[1]+nTP[2]+nTP[3]+nFN[0]+nFN[1]+nFN[2]+nFN[3])
		#nFPR = (nFP[0]+nFP[1]+nFP[2]+nFP[3])/(nTP[0]+nTP[1]+nTP[2]+nTP[3]+nFP[0]+nFP[1]+nFP[2]+nFP[3])
		#if ((nTPR > 0.75) and (nTPR <= 0.85)):
			#print(nameref)

	def _setresulttext(self):
		max_error = 0
		best_error = 0
		for k in range(self.class_num):
			if(self.weighted_parameters[k] == 0):
				continue
			if(self.GT[k] == 0):
				self.lACC[k] = -1
				self.lFPR[k] = -1
				self.lFNR[k] = -1
			else:
				self.lACC[k] = self.TP[k] / self.GT[k];
				self.lFPR[k] = self.FP[k] / self.GT[k];
				self.lFNR[k] = self.FN[k] / self.GT[k];
				# if(k!=4 and k!=8):#4Person_sitting8DontCare
				self.gFPR += self.lFPR[k]
				self.gFNR += self.lFNR[k]
				self.gACC += self.lACC[k]
				self.gSum+=1
			for l in range(self.class_num):
				if(k != l):
					if(self.ER[k][l] > max_error):
						max_error = self.ER[k][l]
						best_error = l
			if(max_error == 0):
				if(self.GT[k] == 0):
					self.ERHist[k] = -1
				else:
					self.ERHist[k] = k
			else:
				self.ERHist[k] = best_error
		self.wgACC = sum(self.weighted_parameters*self.lACC)
		if(self.FP[self.class_num] != 0):
			self.gFPR /= (self.gSum + 1)
		else:
			self.gFPR /= self.gSum
		constant = sum(self.weighted_parameters)
		self.wgACC /= constant
		self.gACC /= self.gSum
		self.gFNR /= self.gSum
		print("lACC",self.lACC)
		print ("gACC",self.gACC,"wgACC",self.wgACC)
		self.Accuracy_Text = "Accuracy = {0}\n".format(self.gACC)

	def run(self):
		self.GT_path = self._checkisfolder(self.GT_path)
		self.Result_path = self._checkisfolder(self.Result_path)
		gt_filenames = os.listdir(self.GT_path)
		result_filenames = os.listdir(self.Result_path)
		gt_filenames, result_filenames = self._pairgtandresult(gt_filenames, result_filenames)
		self.setmaxprogress.emit(len(gt_filenames) - 1)
		for idx, filenames in enumerate(zip(gt_filenames, result_filenames)):
			#print(filenames[0])
			self.progress.emit(idx)
			self._analysis(os.path.join(self.GT_path, filenames[0]), os.path.join(self.Result_path, filenames[1]), filenames[0])
		self._setresulttext()
		self.update.emit(self.GT, self.TP, self.FP, self.FN, self.lACC, self.lFPR, self.lFNR, self.gACC,self.wgACC, self.gFPR, self.gFNR, self.ERHist)
		self.end.emit(True)

class ToolUI(qws.QWidget):
	def __init__(self, parent=None):
		#Set Main Window
		self.RawInput_path = ""
		self.Class_path = ""
		self.Weights_path = ""
		self.GT_path = ""
		self.Result_path = ""
		self.__LUT_path = "./LUT/cityscapes19_v4.png"
		self.__LUT = self.SetLUT()
		qws.QWidget.__init__(self)
		self.setMouseTracking(True)
		self.setGeometry(0, 0, 1920, 1080) #(start location x, start location y, size width, size height)
		self.setWindowTitle('Test')
		self.allclass = 0
		self.class_num = 0
		self._progress = 0
		self.maxprogress = 100
		self.timer = QTimer(self)
		self.timer.timeout.connect(self._SetProgress)

		#Set Table
		self.header_class = []
		self.short_header_class = []
		self.iERR_Tabel = self.SetTable([460, 970], self.class_num, 2,size=[1390, 75], name="iERR_tabel")
		self.iERR_Tabel.setVerticalHeaderLabels(["ERROR","weight"])
		self.Fig = PlotCanvas(self, width=14, height=5)
		self.Fig.move(460, 320)#chat position
		#self.Fig.bar(title = "Random Initial")
		#self.Fig.clear()

		# Set Label
		q = 50
		w = 330
		e = 610
		self.mouselocationlabel = self.SetLabel([10, 1030], "mouselocationlabel", name="mouselocationlabel", size=[250, 20])
		self.iERR_Label = self.SetLabel([1000, 930], "Error Summary", name="iERR_Label", size=[200, 30])
		self.iERR_Label.setFont(QFont("Roman times",15,QFont.Bold))
		#self.predicition = self.SetLabel([930, 730], "Predicition", name="predicition", size=[50, 20])
		self.Input = self.SetLabel([10, q], "Input Image: ", name="Input", size=[190, 20])
		self.Input_Label = self.SetLabel([10, q + 20], " ", name="Input_Label", size=[185, 20])
		self.Class = self.SetLabel([195, q], "Class Path: ", name="Class", size=[190, 20])
		self.Class_Label = self.SetLabel([195, q + 20], "", name="Class_Label", size=[185, 20])
		self.Weights = self.SetLabel([380, q], "Weights Path: ", name="Weights", size=[190, 20])
		self.Weights_Label = self.SetLabel([380, q + 20], "", name="Weights_Label", size=[185, 20])
		self.GT = self.SetLabel([10, w], "GT Path: ", name="GT", size=[220, 20])
		self.GT_Label = self.SetLabel([10, w + 20], "", name="GT_Label", size=[400, 20])
		self.Result = self.SetLabel([10, e], "Result Path: ", name="Result", size=[220, 20])
		self.Result_Label = self.SetLabel([10, e + 20], "", name="Result_Label", size=[400, 20])

		self.Analysis_Label = self.SetLabel([460, 820], "Analysis Label: ", name="Analysis_Label", size=[1395, 100], alignment=Qt.AlignLeft, frameshape=qws.QFrame.Box, frameshadow=qws.QFrame.Raised)
		self.Analysis_Label.setTextFormat(Qt.AutoText)

		self.Input_Image = self.SetLabel([800, 10], "Image", name="Input_Image", size=[512, 256], alignment=Qt.AlignCenter, frameshape=qws.QFrame.Box, frameshadow=qws.QFrame.Plain)
		# Set Button
		self.Input_Button = self.SetButton([10, q + 40], "Select RGB Images", "Input_Button", size=[190, 25])
		self.Input_Button.clicked.connect(self.showDialog)

		self.Class_Button = self.SetButton([195, q + 40], "Select Class List", "Class_Button", size=[190, 25])
		self.Class_Button.clicked.connect(self.showDialog)

		self.Weights_Button = self.SetButton([380, q + 40], "Select Weights List", "Weights_Button", size=[190, 25])
		self.Weights_Button.clicked.connect(self.showDialog)

		self.GT_Button = self.SetButton([10, w + 40], "Select GT Images", "GT_Button", size=[220, 25])
		self.GT_Button.clicked.connect(self.showDialog)

		self.Result_Button = self.SetButton([10, e + 40], "Select PD Images", "Result_Button", size=[200, 25])
		self.Result_Button.clicked.connect(self.showDialog)
		self.Analysis_Button_2D = self.SetButton([10, 920], "Analyze One", "Analysis_Button_2D", size=[200, 25])
		self.Analysis_Button_2D.clicked.connect(self.AnalysisStart_2D)
		
		self.AnalysisDataSet_Button_2D = self.SetButton([210, 920], "Analyze All", "AnalysisDataSet_Button_2D", size=[200, 25])
		self.AnalysisDataSet_Button_2D.clicked.connect(self.AnalysisDataSetStart_2D)

		self.Clear_Button = self.SetButton([10, 1000], "Clear Data", "Clear_Button", size=[200, 30])
		self.Clear_Button.clicked.connect(self.Clear_Measure)
		
		self.Export_Button = self.SetButton([210, 1000], "Export Data", "Export_Button", size=[200, 30])
		self.Export_Button.clicked.connect(self.Export)
		
		a = 800
		s = 100
		
		self.Acc_Button = self.SetButton([a + (1 * ( s + 10)), 280], "Acc", "Acc_Button", size=[s, 30])
		self.Acc_Button.clicked.connect(self.draw)
		
		self.FPR_Button = self.SetButton([a + (2 * ( s + 10)), 280], "FPR", "FPR_Button", size=[s, 30])
		self.FPR_Button.clicked.connect(self.draw)
		
		self.FNR_Button = self.SetButton([a + (3 * ( s + 10)), 280], "FNR", "FNR_Button", size=[s, 30])
		self.FNR_Button.clicked.connect(self.draw)
		
		# Set ListWidget uo show data
		self.Input_Files = self.SetListWidget([10, q + 65], "Input_Files", 190 ,200)
		self.Input_Files.currentItemChanged.connect(self.Change_File)

		self.Class_Files = self.SetListWidget([195, q + 65], "Class_Files", 190 ,200)
		self.Class_Files.currentItemChanged.connect(self.Change_File)

		self.Weights_Files = self.SetListWidget([380, q + 65], "Weights_Files", 190 ,200)
		self.Weights_Files.currentItemChanged.connect(self.Change_File)

		self.GT_Files = self.SetListWidget([10, w + 65], "GT_Files", 360 ,200)
		self.GT_Files.currentItemChanged.connect(self.Change_File)

		self.Result_Files = self.SetListWidget([10, e + 65], "Result_Files", 360, 200)
		self.Result_Files.currentItemChanged.connect(self.Change_File)

		self.ProgressBar = self.SetProgressBar([0, 1050], name="ProgressBar", size=[1920, 20])

	def mouseMoveEvent(self, event):
		self.pos = event.pos()
		self.mouselocationlabel.setText(str(event.pos().x()) + "," + str(event.pos().y()))
		self.update()

	def SetTable(self, location, col, row, name = "", size=[100, 30]):
		table = qws.QTableWidget(self)
		table.setObjectName(name)
		table.setGeometry(location[0], location[1], size[0], size[1])
		table.setColumnCount(col)
		table.setRowCount(row)
		table.setMouseTracking(True)
		return table

	def SetLabel(self, location, text, name = "", size=[100, 30], alignment = None, scaled = True, frameshape = None, frameshadow = None):
		Label = qws.QLabel(self)
		Label.setGeometry(location[0], location[1], size[0], size[1])
		Label.setText(text)
		Label.setObjectName(name)
		Label.setMouseTracking(True)
		if(alignment != None):
			Label.setAlignment(alignment)
		Label.setScaledContents(scaled)
		if(frameshape is not None):
			Label.setFrameShape(frameshape)
		if (frameshadow is not None):
			Label.setFrameShadow(frameshadow)
		return Label

	def SetButton(self, location, text, name = "", size=[100, 30]):
		button = qws.QPushButton(self)
		button.setGeometry(location[0], location[1], size[0], size[1])
		#button.move(location[0], location[1])
		button.setText(text)
		button.setObjectName(name)
		button.setMouseTracking(True)
		return button

	def SetListWidget(self, location, name = "", width = 0, height = 0):
		ListWidget = qws.QListWidget(self)
		ListWidget.move(location[0], location[1])
		ListWidget.resize(width, height)
		ListWidget.setObjectName(name)
		ListWidget.setMouseTracking(True)
		return ListWidget
		
	def SetProgressBar(self, location, name = "", size=[100, 30], min= 0, max= 100):
		PB = qws.QProgressBar(self)
		PB.setGeometry(location[0], location[1], size[0], size[1])
		PB.setMouseTracking(True)
		PB.setMinimum(min)
		PB.setMaximum(max)
		return PB
	
	def SetLUT(self):
		label_colours = cv2.imread(self.__LUT_path, 1).astype(np.uint8)
		#label_colours_bgr = label_colours[..., ::-1]
		return label_colours
	
	'''def ConvertGray2RGB(self, input_path):
		input_image = cv2.imread(input_path)
		label_rgb = np.zeros(input_image.shape, dtype=np.uint8)
		cv2.LUT(input_image, self.__LUT, label_rgb)
		#cv2.imshow("y", label_rgb)
		height, width, channel = label_rgb.shape
		bytesPerLine = 3 * width
		qImg = QImage(label_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
		pix = QPixmap(qImg)
		return pix'''
		
	def showDialog(self):
		s = self.sender()
		directory = qws.QFileDialog.getExistingDirectory(self, "Select " + s.objectName().split("_")[0] + " folder", "./")
		'''if (directory != ""):
			datas = os.listdir(directory)
			datas.sort(key=len)'''
		if(directory == ""):
			print("empty")
		elif(s.objectName() == "Input_Button"):
			datas = os.listdir(directory)
			datas.sort()
			self.Input_path = directory
			self.Input_Label.setText(self.Input_path)
			self.Input_Files.clear()
			self.Input_Files.addItems(datas)
		elif (s.objectName() == "Class_Button"):
			datas = os.listdir(directory)
			datas.sort()
			self.Class_path = directory
			self.Class_Label.setText(self.Class_path)
			self.Class_Files.clear()
			self.Class_Files.addItems(datas)
		elif (s.objectName() == "Weights_Button"):
			datas = os.listdir(directory)
			datas.sort()
			self.Weights_path = directory
			self.Weights_Label.setText(self.Weights_path)
			self.Weights_Files.clear()
			self.Weights_Files.addItems(datas)
		elif(s.objectName() == "GT_Button"):
			datas = os.listdir(directory)
			datas.sort()
			self.GT_path = directory
			self.GT_Label.setText(self.GT_path)
			self.GT_Files.clear()
			self.GT_Files.addItems(datas)
		elif (s.objectName() == "Result_Button"):
			datas = os.listdir(directory)
			datas.sort()
			self.Result_path = directory
			self.Result_Label.setText(self.Result_path)
			self.Result_Files.clear()
			self.Result_Files.addItems(datas)

	def Change_File(self):
		s = self.sender()
		if(s.currentItem() == None):
			pass
		elif (s.objectName() == "Input_Files"):#self.Input_path[(self.Input_path.rfind('/')):]
			self.Input_Label.setText(self.Input_path+ "/" + s.currentItem().text())
			if (os.path.splitext(self.Input_Label.text())[1] == ".jpg" or os.path.splitext(self.Input_Label.text())[1] == ".png"):
				self.Input_Image.setPixmap(QPixmap(self.Input_Label.text()).scaled(self.Input_Image.width(), self.Input_Image.height()))
				print(self.Input_Label.text())#self.Class_path[(self.Class_path.rfind('/')):]
		elif(s.objectName() == "Class_Files"):#self.Class_path
			self.Class_Label.setText(self.Class_path+ "/" + s.currentItem().text())
			if(os.path.splitext(self.Class_Label.text())[1] == ".txt"):
				lines = open(self.Class_Label.text()).readlines()
				self.header_class = [line.replace("\n","") for line in lines]
				self.short_header_class = self.header_class
				self.class_num = len(self.header_class)
				self.weighted_parameters = np.ones(self.class_num)
				self.iERR_Tabel.setColumnCount(self.class_num)
				self.iERR_Tabel.setHorizontalHeaderLabels(self.header_class)
				self.Fig.bar(title = "Random Initial",x_data = self.header_class)
				print(self.Class_Label.text())
				for i in range(self.class_num):
					self.iERR_Tabel.setItem(1,i,qws.QTableWidgetItem(str(self.weighted_parameters[i])))
		elif(s.objectName() == "Weights_Files"):
			self.Weights_Label.setText(self.Weights_path+ "/" + s.currentItem().text())
			print(os.path.splitext(self.Weights_Label.text())[1])
			print(os.path.splitext(self.Weights_Label.text()))
			if(os.path.splitext(self.Weights_Label.text())[1] == ".txt"):
				lines = open(self.Weights_Label.text()).readlines()
				self.weighted_parameters = [float(line.replace("\n","")) for line in lines]
				self.weighted_parameters = np.array(self.weighted_parameters)
				for i in range(self.class_num):
					self.iERR_Tabel.setItem(1,i,qws.QTableWidgetItem(str(self.weighted_parameters[i])))
		elif(s.objectName() == "GT_Files"):
			self.GT_Label.setText(self.GT_path+ "/" + s.currentItem().text())
			print(self.GT_Label.text())
		elif (s.objectName() == "Result_Files"):
			self.Result_Label.setText(self.Result_path + "/" + s.currentItem().text())
			print(self.Result_Label.text())

	def AnalysisStart_2D(self):
		self.AnalysisThread = AnalysisThread_2D(self.GT_Label.text(), self.Result_Label.text(), self.header_class, self.weighted_parameters)
		self.AnalysisThread.update.connect(self._AnalysisThreadUpdate)
		self.AnalysisThread.end.connect(self._ProgressEnd)
		self.AnalysisThread.run()

	def Show(self, T):
		print(T)

	def _AnalysisThreadUpdate(self, GT, TP, FP, FN, lACC, lFPR, lFNR, gACC, wgACC, gFPR, gFNR, ERHist):
		self.GT = GT
		self.TP = TP
		self.FP = FP
		self.FN = FN
		self.lACC = lACC
		self.lFPR = lFPR
		self.lFNR = lFNR
		self.gACC = gACC
		self.wgACC = wgACC
		self.gFPR = gFPR
		self.gFNR = gFNR
		self.ERHist = ERHist
		print("_AnalysisThreadUpdate_ER",self.ERHist)
		print("FP of CLASS_OTHERS", FP[self.class_num])
		print("GT  -  TP  - FP  -  FN")
		for k in range(self.class_num):
			print(self.GT[k], '   ', self.TP[k], '   ', self.FP[k], '   ', self.FN[k])
			print("\n")
		print("PER CLASS EVALUATION METRICS")
		print("ACC  -  FPR  -  FNR")
		for k in range(self.class_num):
			print(self.lACC[k], '    ', self.lFPR[k], '    ', self.lFNR[k])
		print("\n")

	def AnalysisDataSetStart_2D(self):
		self.AnalysisDataSet_Button_2D.setEnabled(False)
		self.AnalysisDataSetThread = AnalysisDataSetThread_2D(self.GT_Label.text(), self.Result_Label.text(), self.header_class, self.weighted_parameters)
		self.AnalysisDataSetThread.update.connect(self._AnalysisThreadUpdate)
		self.AnalysisDataSetThread.progress.connect(self._SetDataSetThreadProgress)
		self.AnalysisDataSetThread.setmaxprogress.connect(self._SetMaxProgress)
		self.AnalysisDataSetThread.test.connect(self.test)
		self.AnalysisDataSetThread.end.connect(self._ProgressEnd)
		self.AnalysisDataSetThread.start()

	def _SetMaxProgress(self, max):
		self.maxprogress = max

	def _SetDataSetThreadProgress(self, progress):
		self._progress = progress
		#self.ProgressBar.setValue((progress / self.maxprogress) * 100)
		##print((progress / self.maxprogress) * 100)
		#self.ProgressBar.setValue(progress)

	def test(self, filelist):
		for neme in filelist:
			print('no. of pair GT_RESULT:', neme)

	def _ProgressEnd(self, En = False):
		print("ERROR HISTOGRAM")
		print(self.ERHist)
		print("\n")
		for i in range(self.class_num):
			if (self.ERHist[i] == -1):
				self.iERR_Tabel.setItem(0, i, qws.QTableWidgetItem("Didn't appear"))
			else:
				self.iERR_Tabel.setItem(0, i, qws.QTableWidgetItem(self.short_header_class[self.ERHist[i]]))
		self._SetResultText()
		self.ProgressBar.reset()
		if(En):
			self.AnalysisDataSet_Button_2D.setEnabled(True)

	def _SetResultText(self):
		print("ALL CLASSES EVALUATION METRICS")
		print("ACC  -  wACC  -  FPR  -  FNR")
		print(self.gACC, '   ', self.wgACC, '   ', self.gFPR, '   ', self.gFNR)
		print("\n")
		data_need_to_show = "{0:^20} = {1:2.4f}\n".format("Accuracy", self.gACC)
		data_need_to_show += "{0:^20} = {1:2.4f}\n".format("Weighted Accuracy", self.wgACC)
		data_need_to_show += "{0:^20} = {1:2.4f}\n".format("False Positive Rate", self.gFPR)
		data_need_to_show += "{0:^20} = {1:2.4f}\n".format("False Negative Rate", self.gFNR)
		self.Analysis_Label.setText(data_need_to_show)
		
	def _SetProgress(self):
		self.ProgressBar.setValue(self._progress)
	
	def draw(self):
		s = self.sender()
		if(s.objectName() == "Acc_Button"):
			self.Fig.bar(title = "Accuracy", x_data = self.short_header_class, y_data = self.lACC)
		elif(s.objectName() == "FPR_Button"):
			self.Fig.bar(title = "False Positive Rate", x_data = self.short_header_class, y_data = self.lFPR)
		elif(s.objectName() == "FNR_Button"):
			self.Fig.bar(title = "False Negative Rate", x_data = self.short_header_class, y_data = self.lFNR)

	def Export(self):
		#Just saves the numbers of accuracy,fpr, fnr, err etc in the excel
		options = qws.QFileDialog.Options()
		options |= qws.QFileDialog.DontUseNativeDialog
		fileName, _ = qws.QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","temp.xls","All Files (*);;Text Files (*.txt)", options=options)
		if fileName:
			print(fileName)
			file = xlwt.Workbook()
			table = self._write(file, 'Class Accuracy', self.lACC)
			table.write(2, 0, "ALL CLASSES Accuracy")
			table.write(2, 1, self.gACC)
			table = self._write(file, 'False Positive Rate', self.lFPR)
			table.write(2, 0, "ALL CLASSES FPR")
			table.write(2, 1, self.gFPR)
			table = self._write(file, 'False Negative Rate', self.lFNR)
			table.write(2, 0, "ALL CLASSES FNR")
			table.write(2, 1, self.gFNR)
			table = self._write(file, 'ERHist', self.ERHist)
			file.save(fileName)
			
	def _write(self, file, sheet_name, data, cell_overwrite_ok = True):
		table = file.add_sheet(sheet_name, cell_overwrite_ok=cell_overwrite_ok)
		for col in range(len(data)):
			table.write(0, col, self.header_class[col])
		for col in range(len(data)):
			table.write(1, col, str(data[col]))
		return table
	
	def Clear_Measure(self):
		self.Input_Image.setText("Image")
		self.Analysis_Label.setText("Analysis Label: ")
		self.iERR_Tabel.clearContents()
		for i in range(self.class_num):
			self.iERR_Tabel.setItem(1,i,qws.QTableWidgetItem(str(self.weighted_parameters[i])))

		self.Fig.clear()
		
if __name__ == "__main__":
	app = qws.QApplication(sys.argv)
	UI = ToolUI()
	UI.show()
	sys.exit(app.exec_())