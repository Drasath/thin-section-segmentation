from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
import numpy as np
from skimage import measure
from skimage import io
from skimage import color
from skimage import segmentation
import matplotlib.pyplot as plt


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
        self.show_borders = False
        
        self.setupUI()

    # TODO - Refactor this mess. LH
    def setupUI(self) -> None:
        # Menubar
        menubarItems = [["Open File", self.open_file],
                        ["Save File", self.save_file],
                        ["Global segment", self.segment],
                        ["Apply modifier", self.apply_modifier],
                        ["Toggle Borders", self.toggleBorders],
                        ["Print AMG", self.printAMG]]
       
        for item in menubarItems:
            self.menuBar().addAction(item[0], item[1])

        # Main Layout
        mainLayout = QHBoxLayout()

        self.mainview = QWidget()
        self.viewbox = Canvas(self, self.mainview)

        inspector = QVBoxLayout()
        tabs = QTabWidget()

        self.outliner = QListWidget()
        self.outliner.itemClicked.connect(self.selectRegion)    # TODO - Make this work when you select using the keyboard. LH

        self.zoomview = QLabel("Zoom View")

        self.parameters = ParameterTab(self, modifiers[0])

        combobox = QComboBox()

        for modifier in modifiers:
            combobox.addItem(modifier.name)

        combobox.currentIndexChanged.connect(lambda: self.parameters.setModifier(modifiers[combobox.currentIndex()]))
        self.segmentation_method_tab = QWidget()
        self.segmentation_method_tab.setLayout(QVBoxLayout())
        self.segmentation_method_tab.layout().setAlignment(Qt.AlignTop)
        self.segmentation_method_tab.layout().addWidget(combobox)
        self.segmentation_method_tab.layout().addWidget(self.parameters)
        
        tabs.addTab(self.segmentation_method_tab, "Properties")
        tabs.addTab(self.outliner, "Inspector")


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
        # TODO - Implement undo function. LH
        pass

    def reset(self) -> None:
        # TODO - Implement reset function. LH
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

    def apply_modifier(self) -> None:
        self.amg.addNode(AMG.Node("Apply Modifier: " + self.parameters.modifier.name))
        modifiers[0].apply(segments = self.segments)

    # TODO - Move this to the canvas class. LH
    def toggleBorders(self) -> None:
        image = io.imread(self.filename, plugin='pil')

        image = color.gray2rgb(image)

        if self.show_borders:
            self.show_borders = False
        else:
            self.show_borders = True
            image = segmentation.mark_boundaries(image, self.segments, color=(0, 1, 0))
            image = (image * 255).astype(np.uint8) # REVIEW - Is there a better way to do this? LH

        q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.viewbox.setImage(q_image)

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

        image = io.imread(self.filename, plugin='pil')
        image = color.gray2rgb(image)

        mask = self.segments == selectedIndex + 1 # FIXME - This + 1 is a botch. LH
        image[mask] = (255, 0, 0)

        q_image = QImage(image.tobytes(), image.shape[1], image.shape[0], QImage.Format_RGB888)

        self.viewbox.setImage(q_image)

        # TODO - Implement zoom view. LH

    def printAMG(self) -> None:
        print(self.amg)
