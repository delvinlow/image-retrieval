import sys
import os
import cv2
from colorhist.colordescriptor import ColorDescriptor
from colorhist.searcher import Searcher
from textsearch.index_text import build_normal_index
from textsearch.index_text import index_tags_normal
from textsearch.search_text import search_text_index

from SIFT.search_sift import SIFTandBOW

from fuse_scores import fuse_scores

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
import design
import glob

from deeplearning.classify_image import run_inference_on_image

class Window(QtGui.QMainWindow, design.Ui_MainWindow):
	def __init__(self):
		super(Window, self).__init__()
		self.setupUi(self)
		self.build_index()
		self.home()
		self.statesConfiguration = {"colorHist": True, "visualConcept": True, "visualKeyword": True, "deepLearning": True}

		self.sab = SIFTandBOW()

	def home(self):
		"""Specific to page. Connect the buttons to functions"""
		self.btn_picker.clicked.connect(self.choose_image)
		self.btn_search.clicked.connect(self.search_image)
		self.btn_quit.clicked.connect(self.close_application)
		self.btn_reset.clicked.connect(self.clear_results)

		self.checkBoxColorHist.stateChanged.connect(self.state_changed)
		self.checkBoxVisualConcept.stateChanged.connect(self.state_changed)
		self.checkBoxVisualKeyword.stateChanged.connect(self.state_changed)
		self.checkBoxDeepLearning.stateChanged.connect(self.state_changed)

		self.show()


	def state_changed(self):
		if self.checkBoxColorHist.isChecked():
			self.statesConfiguration["colorHist"] = True
		else:
			self.statesConfiguration["colorHist"] = False

		if self.checkBoxVisualConcept.isChecked():
			self.statesConfiguration["visualConcept"] = True
		else:
			self.statesConfiguration["visualConcept"] = False

		if self.checkBoxVisualKeyword.isChecked():
			self.statesConfiguration["visualKeyword"] = True
		else:
			self.statesConfiguration["visualKeyword"] = False

		if self.checkBoxDeepLearning.isChecked():
			self.statesConfiguration["deepLearning"] = True
		else:
			self.statesConfiguration["deepLearning"] = False

		print self.statesConfiguration


	def closeEvent(self, event):
		event.ignore()
		self.close_application()

	def close_application(self):
		choice = QtGui.QMessageBox.question(self, "Quit?", 
			"Are you sure to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

		if choice == QtGui.QMessageBox.Yes:
			sys.exit()
		else:
			pass

	def choose_image(self):
		self.tags_search.setText("")
		self.filename = QtGui.QFileDialog.getOpenFileName(self, "Open Image", os.path.dirname(__file__),"Images (*.jpg *.gif *.png)")
		base_img_id = os.path.splitext(os.path.basename(str(self.filename)))
		base_img_id = "".join(base_img_id)

		self.label_query_img.setPixmap(QPixmap(self.filename).scaledToWidth(100) )

		# COLOR HISTOGRAM -process query image to feature vector
		# initialize the image descriptor
		cd = ColorDescriptor((8, 12, 3))
		self.filename = str(self.filename)
		query = cv2.imread(self.filename)
		# load the query image and describe it
		self.queryfeatures = cd.describe(query)


		self.hist_sift_query = self.sab.histogramBow(query)


		# If tags exist, load them into the searchbar
		if base_img_id in self.tags_index:
			tags = " ".join(self.tags_index[base_img_id])
			self.tags_search.setText(tags)



	def search_image(self):
		final_results = []

		# Perform the search on Color Histogram
		searcher = Searcher("colorhist/index_color_hist.csv")
		results_color_hist = searcher.search(self.queryfeatures, limit=160)

		# Perform Text Search
		queryTags = str(self.tags_search.text())
		results_text = []
		if len(queryTags) > 0:
			results_text = search_text_index(queryTags, limit=160) # Will return a min heap (smaller is better)

		# Perform search on SIFT
		results_sift = self.sab.search(self.hist_sift_query, limit=160)

		final_results = fuse_scores(self.statesConfiguration, results_color_hist, results_sift, results_text, [(1, "0321_2347368812.jpg")], [(1, "0350_350973894.jpg")])
		print final_results


		for (score, img_id) in final_results:
			fullpath = glob.glob(os.path.join(os.path.curdir, "ImageData", "train", "data", "*", img_id) )[0]
			img_widget_icon = QListWidgetItem(QIcon(fullpath), img_id)
			self.listWidgetResults.addItem(img_widget_icon)



	def clear_results(self):
		self.listWidgetResults.clear()

	def build_index(self):
		# Read in query tags
		test_tags = os.path.join(os.path.dirname(__file__), "ImageData", "test", "test_text_tags.txt")
		try:
		 	file_train_tags = open(test_tags, "r")
	 	except IOError:
	 		print "Cannot open test_text_tags.txt"
	 	else:
	 		self.tags_index = index_tags_normal(file_train_tags)
	 		file_train_tags.close()
	 		# print self.tags_index


def main():
	app = QtGui.QApplication(sys.argv)
	GUI = Window()
	sys.exit(app.exec_())

main()