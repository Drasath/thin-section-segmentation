from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
import numpy as np
from skimage import measure

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

        self.amg = AMG.AMG()
        
        self.setupUI()

    def setupUI(self) -> None:
        # Menubar
        menubarItems = [["Open File", self.open_file],
                        ["Save File", self.save_file],
                        ["Segment",   self.segment],
                        ["Print AMG", self.printAMG]]
       
        for item in menubarItems:
            self.menuBar().addAction(item[0], item[1])

        # Main Layout
        mainLayout = QHBoxLayout()

        self.mainview = QWidget()
        self.viewbox = Canvas(self, self.mainview)

        self.tmp = Canvas(self, self.mainview)
        self.tmp.image.fill(QColor(0, 0, 0, 0))

        inspector = QVBoxLayout()
        tabs = QTabWidget()

        self.outliner = QListWidget()
        self.outliner.itemClicked.connect(self.selectRegion)

        self.zoomview = QLabel("Zoom View")

        self.segmentation_method = QWidget()
        self.segmentation_method.setLayout(QVBoxLayout())
        self.parameters = ParameterTab(self, modifiers[0])

        combobox = QComboBox()

        for modifier in modifiers:
            combobox.addItem(modifier.name)

        self.segmentation_method.layout().addWidget(combobox)
        self.segmentation_method.layout().setAlignment(Qt.AlignTop)
        combobox.currentIndexChanged.connect(lambda: self.parameters.setModifier(modifiers[combobox.currentIndex()]))
        

        tabs.addTab(self.parameters, "Properties")
        tabs.addTab(self.outliner, "Inspector")
        tabs.addTab(self.segmentation_method, "Segmentation Method")


        inspector.addWidget(self.zoomview)
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

    def undo(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def segment(self) -> None:
        logging.info("Segmenting image...")
        self.amg.addNode(AMG.Node("Segment"))
        self.segments = segment(self.filename)
        regionprops = measure.regionprops(self.segments)

        self.outliner.clear()
        for region in range(len(regionprops)):
            self.outliner.addItem("Region " + str(region) + ": " + str(regionprops[region].area) + " pixels")

        self.regionprops = regionprops

    def open_file(self) -> None:
        (self.filename, _) = QFileDialog.getOpenFileName(filter="Images (*.tif *.tiff)", directory="./datasets")
        if not self.filename:
            logging.warning("No file selected")
            return
        
        logging.info("Open file: " + self.filename)
        self.amg.addNode(AMG.Node("Open File: " + self.filename))
        self.viewbox.openFile(self.filename)
        self.lastCursorPosition = self.viewbox.pos()

    def save_file(self) -> None:
        #TODO - Create save file pipeline
        np.save("segments.npy", self.segments)
        # Store AMG
        with open("amg.json", "w") as f:
            f.write(self.amg.toJSON())
        
        logging.info("Saved file")

    def selectRegion(self) -> None:
        selectedIndex = self.outliner.selectedIndexes()[0].row()
        
        bbox = self.regionprops[selectedIndex].bbox
        self.zoomview.setPixmap(QPixmap.fromImage(self.viewbox.image.copy(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])))

    def printAMG(self) -> None:
        pass
