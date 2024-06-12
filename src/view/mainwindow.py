from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
import numpy as np
from skimage import measure, io
import zipfile
import os

from constants import *
from model import AMG
from model.segmentation import segment
from view.canvas import Canvas
from view.parameter_tab import ParameterTab
from modifiers import modifiers

# TODO - Refactor this mess. LH
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Set window properties
        images_directory = Path(PROJECT_DIRECTORY / "resources" / "images")
        self.setWindowIcon(QIcon(str(images_directory / "icon.png")))
        self.setWindowTitle("Thinsight")
        self.setStatusBar(QStatusBar())
        self.setMouseTracking(True)

        # Shortcuts
        QShortcut(QKeySequence('Ctrl+Z'), self, self.undo)
        QShortcut(QKeySequence('Ctrl+R'), self, self.reset)
        QShortcut(QKeySequence('Ctrl+Q'), self, self.segment)

        self.initialize_variables()
        
        self.setupUI()

    def initialize_variables(self) -> None:
        self.amg = AMG.AMG()
        self.filename = None
        self.segments = None
        self.regionprops = None
        self.regionprops_text = None
        self.lc = None

    def setupUI(self) -> None:

        # Main Layout
        mainLayout = QHBoxLayout()

        self.mainview = QWidget()
        self.mainview.setLayout(QVBoxLayout())

        self.viewbox = Canvas(self)
        self.mainview.layout().addWidget(self.viewbox)

        self.init_menubar()

        inspector = QVBoxLayout()
        tabs = QTabWidget()

        self.outliner = QListWidget()
        self.outliner.itemClicked.connect(self.selectRegion)    # TODO - Make this work when you select using the keyboard. LH

        self.parameters = ParameterTab(self, modifiers[0])

        self.combobox = QComboBox()

        # Load modifiers
        for modifier in modifiers:
            self.combobox.addItem(modifier.name)

        self.combobox.currentIndexChanged.connect(lambda: self.parameters.setModifier(modifiers[self.combobox.currentIndex()]))
        self.segmentation_method_tab = QWidget()
        self.segmentation_method_tab.setLayout(QVBoxLayout())
        self.segmentation_method_tab.layout().setAlignment(Qt.AlignTop)
        self.segmentation_method_tab.layout().addWidget(self.combobox)
        self.segmentation_method_tab.layout().addWidget(self.parameters)
        
        self.properties_tab = QWidget()
        self.properties_tab.setLayout(QVBoxLayout())
        self.selected_region_properties = QLabel("Properties")
        self.properties_tab.layout().addWidget(self.selected_region_properties)
        zoom_button = QPushButton("Zoom")
        zoom_button.clicked.connect(self.viewbox.zoomIn)
        self.properties_tab.layout().addWidget(zoom_button)

        tabs.addTab(self.outliner, "Inspector")
        tabs.addTab(self.properties_tab, "Properties")
        tabs.addTab(self.segmentation_method_tab, "Refinement")

        # inspector.addWidget(self.zoomview)
        inspector.addWidget(tabs)
        
        mainLayout.addWidget(self.mainview, stretch=3)
        mainLayout.addLayout(inspector, stretch=1)

        self.timeline = QLabel("Timeline")
        
        layout = QVBoxLayout()
        layout.addLayout(mainLayout)
        layout.addWidget(self.timeline)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def init_menubar(self) -> None:
        menubarItems = [["Open File", self.open_file],
                        ["Save File", self.save_file],
                        ["Global segment", self.segment],
                        ["Apply modifier", self.apply_modifier],
                        ["Toggle Borders", self.viewbox.toggleBorders],
                        ["Toggle RAG", self.viewbox.toggleRAG]]
                        
       
        for item in menubarItems:
            self.menuBar().addAction(item[0], item[1])

    def load_modifiers(self) -> None:
        # TODO - Implement loading of modifiers. LH
        pass

    def apply_modifier(self) -> None:
        self.amg.addNode(AMG.Node("Apply Modifier: " + self.parameters.modifier.name))
        res = modifiers[self.combobox.currentIndex()].apply(image=self.viewbox.image, segments=self.segments, parameters=self.parameters.getParameters())
        self.viewbox.setImage(res)

    def undo(self) -> None:
        # TODO - Implement undo function. LH
        pass

    def reset(self) -> None:
        # TODO - Implement reset function. LH
        pass

    def segment(self) -> None:
        logging.info("Segmenting image...")
        self.amg.addNode(AMG.Node("Segment"))
        self.segments, self.lc = segment(self.filename, n_segments=1000)
        self.regionprops = measure.regionprops(self.segments)

        self.outliner.clear()
        for region in range(len(self.regionprops)):
            self.outliner.addItem("Region " + str(region) + ": " + str(self.regionprops[region].area) + " pixels")

        self.regionprops_text = self.regionprops

    def open_file(self) -> None:
        (self.filename, _) = QFileDialog.getOpenFileName(filter="Images (*.tif *.tiff)", directory=str(PROJECT_DIRECTORY / "datasets"))
        if not self.filename:
            logging.warning("No file selected")
            return
        
        logging.info("Open file: " + self.filename)
        self.amg.addNode(AMG.Node("Open File: " + self.filename))
        self.viewbox.openFile(self.filename)
        self.lastCursorPosition = self.viewbox.pos()

    def save_file(self) -> None:
        #TODO - Create save file pipeline
        # np.save("segments.npy", self.segments)
        # Store AMG
        with open("amg.json", "w") as f:
            f.write(self.amg.toJSON())
        
        file_path = Path(f"test{'.save'}")

        if file_path.exists():
            os.remove(file_path)
        with zipfile.ZipFile(file_path, 'w') as savefile:
            savefile.write(str(PROJECT_DIRECTORY / "logs" / "log.log"), "log.log")
            savefile.write('amg.json')
            for image in range(len(self.viewbox.revisions)):
                logging.info(f"Saving image")
                io.imsave(f'{image}.tif', self.viewbox.revisions[image])
                savefile.write(f'{image}.tif', f'cache/{image}.tif')

        logging.info("Saved file")

    def selectRegion(self) -> None:
        selectedIndex = self.outliner.selectedIndexes()[0].row()
        self.viewbox.selectSegment(selectedIndex + 1)

        # TODO - Implement zoom view. LH
        # bbox = self.regionprops[selectedIndex].bbox

    def printAMG(self) -> None:
        print(self.amg)
