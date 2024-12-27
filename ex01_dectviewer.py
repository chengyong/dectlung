# -*- coding: utf-8 -*-

#
# Project: 双能CT可视化显示系统
# Author: Cheng Y.(orangeinfo@163.com)
# Description:
# Refer:
# Date: 2024-05-07
# History:
# 1. 实现阅读DECT PBV数据
#


import os
import sys
import pydicom
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QScrollArea, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

class DicomViewer(QMainWindow):
    def __init__(self, dicom_images):
        super().__init__()
        self.dicom_images = dicom_images  # List of DICOM image data
        self.current_image_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DECT Image Browser")
        self.setGeometry(100, 100, 512, 512)
        # Create a label to display DICOM images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)

        self.load_image(self.current_image_index)

        # Enable mouse wheel event
        self.image_label.wheelEvent = self.scroll_images

    def load_image(self, index):
        # Convert DICOM image data to QImage
        image_data = self.dicom_images[index].pixel_array
        height, width, channel = image_data.shape
        bytes_per_line = 3 * width
        q_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_RGB888)
        # Convert QImage to QPixmap and display it on the label
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def scroll_images(self, event):
        # Change the image index based on the mouse wheel movement
        delta = event.angleDelta().y()
        if delta > 0 and self.current_image_index > 0:
            self.current_image_index -= 1
        elif delta < 0 and self.current_image_index < len(self.dicom_images) - 1:
            self.current_image_index += 1
        self.load_image(self.current_image_index)

def load_dicom_images(directory):
    # Load DICOM images from a directory and return a list of DICOM image data
    # This is just a placeholder function. You need to implement the DICOM loading logic here.
    dicom_images = []
    for entry in os.listdir(directory):
        # Replace with actual DICOM file loading
        dicom_images.append(pydicom.dcmread(os.path.join(directory, entry)))
    return dicom_images

def show_pbv_images(pbv_dirpath):
    app = QApplication(sys.argv)
    # Load DICOM images (replace 'your_dicom_directory' with the actual directory path)
    dir_path = os.path.join(pbv_dirpath)
    dicom_images = load_dicom_images(dir_path)
    # Create and show the DICOM browser
    browser = DicomViewer(dicom_images)
    browser.show()
    sys.exit(app.exec())


def run_show_pbv_images():
    pbv_dirpath = r"E:\cjfh\dectpe\raw\untypical\case3\PBV-color"
    show_pbv_images(pbv_dirpath)


run_show_pbv_images()