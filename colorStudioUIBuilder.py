# -*- coding: utf-8 -*-
"""
Color Studio - 2019
----------------------------------
new version of
Color Studio
"""
# ----------------------------------------------------------------------------------
# main changes
# ----------------------------------------------------------------------------------
# GUI lib: pygame to pyqt5 -> pyqt6 (June 2024 migration to Python 3.12)
# include 3d color point cloud (modernGL) 
# ----------------------------------------------------------------------------------
# version0.0
# -----------------------------------------------------------------------------------
# Qt window

# import(s)
# ----------------------------------------------------------------------------------

import sys
import imageio
import moderngl

import numpy as np
import skimage

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QMainWindow, QScrollArea, QGroupBox
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6 import QtCore, QtOpenGL 

import colorStudioModel
import colorStudioWidget
import colorStudioController
import colorStudioUtils

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
class CSUIBuilder:
    # class attributes
    uiLoadIMG  	= None
    uiSaveIMG  	= None
    uiAEonIMG  	= None
    uiAEoffIMG 	= None
    uiDEIMG 	= None
    uiIEIMG 	= None
    uiCCIMG 	= None

    template1920x1080 = { 
        'scale': 0.5 ,                     \
        'uiRenderWidget_pos' : (480,30),                    \
        'uiRenderWidget_size' : (int(1920/2),int(1080/2)),  \
        # color3D widget
        'uiColor3DWidget_pos' : (1440,30),                  \
        'uiColor3DWidget_size' : (480,480),                 \
        # color wheel widget
        'uiColorWheelWidget_pos' : (1440,540),              \
        'uiColorWheelWidget_size' : (480,480),              \
        # menu/control widget
        'uiControlWidget_pos' : (0,30),                     \
        'uiControlWidget_size' : (480,0)
    }

    template3000x200 = { 
        'scale': 1,                        \
        'uiRenderWidget_pos' : (int(480*1.25),60),          \
        'uiRenderWidget_size' : (int(1920),int(1080)),      \
        # color3D widget
        'uiColor3DWidget_pos' : (3000-480,60),              \
        'uiColor3DWidget_size' : (480,480),                 \
        # color wheel widget
        'uiColorWheelWidget_pos' : (3000-480,540+60),       \
        'uiColorWheelWidget_size' : (480,480),              \
        # menu/control widget
        'uiControlWidget_pos' : (0,60),                     \
        'uiControlWidget_size' : (480,0)
    }

    template = template1920x1080

    # class method
    @staticmethod
    def setTemplate(widthSceen, heightScreen):
        if widthSceen == 3000 : 
            CSUIBuilder.template = CSUIBuilder.template3000x200

    # constructor
    def __init__(self):
        pass

    # class method
    @staticmethod
    def uiLoadIcon(pathUIimg=None):
        if pathUIimg == None: 
            pathUIimg = './images/others/'
        # window with buttons
        CSUIBuilder.uiLoadIMG  	= QIcon(pathUIimg+'uiLoad.png')
        CSUIBuilder.uiSaveIMG  	= QIcon(pathUIimg+'uiSave.png')
        CSUIBuilder.uiAEonIMG  	= QIcon(pathUIimg+'uiAEon.png')
        CSUIBuilder.uiAEoffIMG 	= QIcon(pathUIimg+'uiAEoff.png')
        CSUIBuilder.uiDEIMG 	= QIcon(pathUIimg+'uiLight_F_DE.png')
        CSUIBuilder.uiIEIMG 	= QIcon(pathUIimg+'uiLight_F_IE.png')
        CSUIBuilder.uiCCIMG 	= QIcon(pathUIimg+'uiLight_F_CC.png')
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
class CSUIAllBuilder(CSUIBuilder):
    def __init__(self, lightsScene):
        # (0) load qIcon images and get screen resolution
        CSUIBuilder.uiLoadIcon()

        # --- CRÉATION DE LA FENÊTRE PRINCIPALE UNIQUE ---
        self.mainWindow = QMainWindow()
        self.mainWindow.setWindowTitle("Color Studio")
        
        # Le widget central requis par QMainWindow pour accueillir le layout global
        centralWidget = QWidget()
        self.mainWindow.setCentralWidget(centralWidget)
        
        # Disposition horizontale globale : [ Contrôles ] [ Vue Rendu ] [ Couleurs (3D + Roue) ]
        mainLayout = QHBoxLayout(centralWidget)
        mainLayout.setSpacing(12)
        mainLayout.setContentsMargins(8, 8, 8, 8)

        # (1) render Widget
        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Render View")

        # (2) color3D widget
        self._color3DWidget = colorStudioWidget.MyWidgetGL(skimage.transform.rescale(lightsScene.render(), 0.1, anti_aliasing=True, channel_axis=2), True)

        # (3) colorWheel Widget
        w, h = CSUIBuilder.template['uiColorWheelWidget_size']
        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None, w)
        colorWheelController = colorStudioController.CSColorWheelController(lightsScene, None, [self._renderWidget, self._color3DWidget], self._colorWheelWidget)
        self._colorWheelWidget._controller = colorWheelController

        # (4) control Widget (scrollable)
        self._controlWidget = colorStudioWidget.CSDisplayControls()
        self._controlWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        controlScroll = QScrollArea()
        controlScroll.setWidgetResizable(True)
        controlScroll.setWidget(self._controlWidget)
        controlScroll.setFixedWidth(360)

        # (5) load/save layout to control widget (grouped)
        loadSaveLayout = colorStudioWidget.CSQLoadSaveLayout(CSUIBuilder.uiLoadIMG, CSUIBuilder.uiSaveIMG)
        box_load = QGroupBox("Load / Save")
        box_load.setLayout(QVBoxLayout())
        box_load.layout().addLayout(loadSaveLayout)
        self._controlWidget._layout.addWidget(box_load)

        # (6) light Control Layout per light
        for light in lightsScene._lights:
            # set value according to light
            lightControl_layout = colorStudioWidget.CSQLightControlLayout(None, lightPosIdx=light._imageIdx)
            expoString = "{:+.2f}".format(light._exposure)
            lightControl_layout._exposureValueLabel.setText(expoString)
            self._controlWidget._layout.addLayout(lightControl_layout)
            # lightController
            lightController = colorStudioController.CSLightController(lightsScene, light, [self._renderWidget, self._color3DWidget])
            lightController._colorWheelController = colorWheelController
            lightControl_layout._controller = lightController

        # (7) post processing
        # hacking waiting to Post process in XML
        ae = colorStudioModel.AE_Ymean(Ytarget=0.5, exposure=0.0)
        lightsScene.addPostProcess(ae)
        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        box_ae = QGroupBox("Automatic Exposure")
        box_ae.setLayout(QVBoxLayout())
        box_ae.layout().addLayout(AE_layout)
        self._controlWidget._layout.addWidget(box_ae)
        ae_controller = colorStudioController.CSAEController(lightsScene, ae, [self._renderWidget, self._color3DWidget])
        AE_layout._controller = ae_controller

        sat = colorStudioModel.Saturation()
        lightsScene.addPostProcess(sat)
        sat_layout = colorStudioWidget.CSQSaturationLayout(None)
        box_sat = QGroupBox("Saturation")
        box_sat.setLayout(QVBoxLayout())
        box_sat.layout().addLayout(sat_layout)
        self._controlWidget._layout.addWidget(box_sat)
        sat_controller = colorStudioController.CSSaturationController(lightsScene, sat, [self._renderWidget, self._color3DWidget])
        sat_layout._controller = sat_controller
        # end of hack

        # --- ASSEMBLAGE ET INTEGRATION DES BLOCS DANS LA FENÊTRE UNIQUE ---
        
        # Colonne de droite verticale pour empiler le rendu 3D et la Roue Chromatique
        rightColumnLayout = QVBoxLayout()
        rightColumnLayout.setSpacing(8)
        rightColumnLayout.addWidget(self._color3DWidget)
        rightColumnLayout.addWidget(self._colorWheelWidget)
        
        # Ajout séquentiel des panneaux de gauche à droite avec des facteurs de proportion (stretch)
        mainLayout.addWidget(controlScroll, stretch=1)    # Panneau de commandes (scrollable)
        mainLayout.addWidget(self._renderWidget, stretch=3)     # Rendu principal (prend plus de place)
        mainLayout.addLayout(rightColumnLayout, stretch=1)      # Outils d'analyse de couleur

        # Affichage de l'interface globale
        self.mainWindow.showMaximized()

        # (end) init render
        self._renderWidget._update(lightsScene.render())

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------