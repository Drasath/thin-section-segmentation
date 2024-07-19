from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
from skimage.measure import regionprops
import numpy as np
import matplotlib.pyplot as plt

from constants import *
from modifiers import modifiers, rag_modifier

from .viewport import Viewport
from .parameter_tab import ParameterTab
from model.segmentation import segment
from .tutorial import Tutorial
from model.AMG import AMG, Node as AMGNode

class MainWindow(QMainWindow):
    """
    Main window of the program
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        # Disabled keyboard shortcuts
        # QShortcut(QKeySequence('Ctrl+Z'), self, self.undo)
        # QShortcut(QKeySequence('Ctrl+Y'), self, self.redo)
        
        self._setup_ui()
        QShortcut(QKeySequence("Ctrl+M"), self, self.merge_regions)
        QShortcut(QKeySequence("Ctrl+I"), self, self.viewport.invert_selection)

        self.setWindowTitle("ThinSight")
        self.setWindowIcon(QIcon(str(PROJECT_DIRECTORY / "resources" / "images" / "icon.png")))

        self.save_path = None
        self.amg = AMG(self)
        
        self.save_path = Path(PROJECT_DIRECTORY / "saves" / f"subject{SUBJECT_NR}.save")
        self.viewport.load_image(str(PROJECT_DIRECTORY / "datasets" / "example_medium_quality.tif"))
        

    def _setup_ui(self):

        # SECTION - Menu Bar
        menu_items = {
            "File": [
                {"Open": self.open_file},
                {"Save": self.save_file},
                {"Save As": self.save_as_file},
                # {"Preferences": lambda: None},
                # {"Recent Files": lambda: None},
                # {"Recent Projects": lambda: None},
                # {"Export": lambda: None},
                {"Exit": self.close}
            ],
            "Edit": [
                # {"Undo": self.undo},
                # {"Redo": self.redo},
                {"Merge Regions": self.merge_regions}
            ],
            "View": [
                {"Show Borders": self.toggle_borders},
                # {"Show Colors": self.toggle_colors},
                # {"Show Goal": self.toggle_overlay},
                # {"Show RAG": self.toggle_rag},
                {"Reset View": self.reset_view}
            ],
            "Analysis": [
                # {"Show Clustering": self.show_clustering},
                {"Show Histogram": lambda: self.show_histogram()},
                # {"Jaccard Distance": self.jaccard_distance},
                # {"Print AMG": lambda: print(self.amg)}
            ],
            "Segmentation": [
                # {"Refine": },
                {"Segment": self.global_segmentation}
            ],
            # "Help": [
            #     {"About": self.about}
            # ]
        }

        menu_bar = self.menuBar()
        for menu_name, menu_actions in menu_items.items():
            menu = menu_bar.addMenu(menu_name)
            for action in menu_actions:
                (action_name, action_function), = action.items()
                menu.addAction(action_name, action_function)

        #!SECTION

        # SECTION - Central Widget
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        viewport_wrapper = QWidget()
        viewport_wrapper_layout = QVBoxLayout()
        viewport_wrapper.setLayout(viewport_wrapper_layout)
        main_layout.addWidget(viewport_wrapper)
        
        # SECTION - Viewport
        self.viewport = Viewport()
        viewport_wrapper_layout.addWidget(self.viewport)
        #!SECTION

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)

        self.outliner_wrapper = QTabWidget()
        self.outliner = QListWidget()
        self.outliner.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.outliner.itemClicked.connect(self.select_region)
        self.outliner_wrapper.addTab(self.outliner, "Outliner")

        sidebar_layout.addWidget(Tutorial(self.save_as_file))
        sidebar_layout.addWidget(self.outliner_wrapper)

        self.inspector = QTabWidget()
        sidebar_layout.addWidget(self.inspector)

        # SECTION - Global parameters
        # TODO - Put in separate class/function
        self.global_parameters = QWidget()
        global_parameters_layout = QVBoxLayout()
        global_parameters_layout.setAlignment(Qt.AlignTop)
        self.global_parameters.setLayout(global_parameters_layout)
        
        self.global_parameters.n_segments = QLineEdit()
        self.global_parameters.compactness = QLineEdit()
        self.global_parameters.min_lum = QLineEdit()
        self.global_parameters.min_size = QLineEdit()
        self.global_parameters.quality = QLineEdit()

        self.global_parameters.n_segments.setValidator(QIntValidator(1, 2000))
        self.global_parameters.n_segments.setText("800")
        self.global_parameters.compactness.setValidator(QDoubleValidator(0, 1, 5))
        self.global_parameters.compactness.setText("0.1")
        self.global_parameters.min_lum.setValidator(QDoubleValidator(0, 1, 5))
        self.global_parameters.min_lum.setText("0.2")
        self.global_parameters.min_size.setValidator(QIntValidator(1, 10000))
        self.global_parameters.min_size.setText("500")
        self.global_parameters.quality.setValidator(QDoubleValidator(0, 1, 5))
        self.global_parameters.quality.setText("0.1")
        
        global_parameters_layout.addWidget(QLabel("Number of Segments (0-2000)"))
        global_parameters_layout.addWidget(self.global_parameters.n_segments)
        global_parameters_layout.addWidget(QLabel("Compactness (0.00-1.00)"))
        global_parameters_layout.addWidget(self.global_parameters.compactness)
        global_parameters_layout.addWidget(QLabel("Minimum Luminance (0.00-1.00)"))
        global_parameters_layout.addWidget(self.global_parameters.min_lum)
        global_parameters_layout.addWidget(QLabel("Minimum Grain Size (0-10000)"))
        global_parameters_layout.addWidget(self.global_parameters.min_size)
        global_parameters_layout.addWidget(QLabel("Quality (0.00-1.00)"))
        global_parameters_layout.addWidget(self.global_parameters.quality)
        
        global_parameters_layout.addWidget(QPushButton("Segment", clicked=self.global_segmentation))
        self.inspector.addTab(self.global_parameters, "Global Parameters")

        #!SECTION - Global parameters

        self.rag_parameters = QWidget()
        rag_parameters_layout = QVBoxLayout()
        rag_parameters_layout.setAlignment(Qt.AlignTop)
        self.rag_parameters.setLayout(rag_parameters_layout)
        self.rag_parameters.threshold = QLineEdit()
        self.rag_parameters.threshold.setValidator(QDoubleValidator(0, 1, 2))
        rag_parameters_layout.addWidget(QLabel("Threshold (0.00-1.00)"))
        rag_parameters_layout.addWidget(self.rag_parameters.threshold)
        self.rag_parameters.layout().addWidget(QPushButton("Apply RAG", clicked=self.apply_rag))
        self.inspector.addTab(self.rag_parameters, "RAG Parameters")

        self.refinement = QWidget()
        refinement_layout = QVBoxLayout()
        self.refinement.setLayout(refinement_layout)        
        self.refinement.segmentation_method = QComboBox()

        for modifier in modifiers:
            self.refinement.segmentation_method.addItem(modifier.name)

        self.refinement.parameters = ParameterTab(self, modifiers[0])
        self.refinement.segmentation_method.currentIndexChanged.connect(lambda: self.refinement.parameters.set_modifier(modifiers[self.refinement.segmentation_method.currentIndex()]))
        refinement_layout.addWidget(self.refinement.segmentation_method)
        refinement_layout.addWidget(self.refinement.parameters)
        refinement_layout.addWidget(QPushButton("Apply", clicked=self.apply_modifier))

        self.inspector.addTab(self.refinement, "Refinement")

        #!SECTION

        main_layout.setStretch(0, 3)
        main_layout.setStretch(1, 1)
        self.setCentralWidget(central_widget)
    
    def open_file(self):
        (file_path, _) = QFileDialog.getOpenFileName(filter="Images (*.tif *.tiff *.save)", directory=str(PROJECT_DIRECTORY / "datasets"))

        if file_path:
            if file_path.endswith(".tif") or file_path.endswith(".tiff"):
                logging.info(f"File opened: {file_path}")
                self.viewport.load_image(file_path)
            elif file_path.endswith(SAVE_FILE_EXTENTION): # TODO: Make save files open all stored data (image, segmentation, AMG)
                logging.info(f"Segments opened: {file_path}")
                segments = np.load(file_path)
                self.viewport.set_segments(segments)
        else:
            logging.info("No file selected.")

    def store_file(self, cache=None):
        path = self.save_path
        if cache is not None:
            path = Path(path)
            path = Path(path.parent / (str(cache) + "_" + path.name))
            
        with open(str(path), 'wb') as file:
            np.save(file, self.viewport.segments)

        with open(str(Path(path).parent / f"{str(cache)}_AMG.json"), 'w') as file:
            file.write(self.amg.to_JSON())

    def save_file(self):
        """
        Saves the current progress, prompts the user if there is no previous save file.
        """
        if self.save_path:
            logging.info("Saving file...")
            self.store_file()
        else:
            self.save_as_file()

    def save_as_file(self):
        (file_path, _) = QFileDialog.getSaveFileName(filter="Save Files (*.save)", directory=str(PROJECT_DIRECTORY / "saves"))

        if file_path:
            logging.info(f"File saved as: {file_path}")
            if file_path.endswith(SAVE_FILE_EXTENTION):
                self.save_path = Path(file_path)
                self.save_file()
        else:
            logging.info("No file location selected.")

    def undo(self):
        """
        
        """
        self.amg.undo()
        # self.load_file(self.amg.activeNode.index)

    def redo(self):
        """
        """
        self.amg.redo()
        # self.load_file(self.amg.activeNode.index)

    def global_segmentation(self):
        parameters = {
            "n_segments": int(self.global_parameters.n_segments.text() or 800),
            "compactness": float(self.global_parameters.compactness.text() or 0.1),
            "min_size": int(self.global_parameters.min_size.text() or 500),
            "min_lum": float(self.global_parameters.min_lum.text() or 0.2),
            "quality": float(self.global_parameters.quality.text() or 0.1)
        }
        self.amg.addNode(AMGNode({"modifier": "Global segmentation", "parameters": {**parameters}}))

        segments, lc = segment(self.viewport.image, **parameters)
        segments += 1
        self.viewport.set_segments(segments)
        self.prev_segments = self.viewport.segments.copy()
        props = regionprops(segments)
        biggest = max(props, key=lambda x: x.area)
        self.outliner.clear()
        for prop in props:
            if prop == biggest:
                self.outliner.addItem(f"Background {prop.label}")
            else:
                self.outliner.addItem(f"Region {prop.label}")

        np.save("segments.npy", segments)

    def select_region(self, item):
        self.viewport.selected_segments = []
        for item in self.outliner.selectedIndexes():
            self.viewport.selected_segments.append(item.row() + 1)
        self.viewport.update()

    def apply_modifier(self):
        modifier = modifiers[self.refinement.segmentation_method.currentIndex()]
        parameters = self.refinement.parameters.get_parameters()
        
        self.amg.addNode(AMGNode({"modifier": modifier.name, "parameters": parameters}))

        qApp.changeOverrideCursor(Qt.BusyCursor)
        if modifier.type == "image":
            result = modifier.apply(self.viewport.image, self.viewport.segments, parameters)
            self.viewport.set_image(result)
            self.viewport._resize_image()
        elif modifier.type == "segments":
            for segment in self.viewport.selected_segments:
                mask = self.viewport.segments == segment
                segments = self.viewport.segments.copy()
                segments[mask] = 0 # TODO - Merge with close regions. LH
                parameters["start_label"] = self.viewport.segments.max() + 1
                logging.info(f"{mask}")
                result = modifier.apply(self.viewport.image, mask, parameters)
                segments[result] = segment
                self.viewport.set_segments(segments)
        qApp.restoreOverrideCursor()

    def merge_regions(self):
        self.amg.addNode(AMGNode({"modifier": "Merge regions", "parameters": self.viewport.selected_segments}))
        segments = self.viewport.segments.copy()
        for segment in self.viewport.selected_segments:
            segments[segments == segment] = self.viewport.selected_segments[0]
            # self.outliner.takeItem(self.outliner.row(self.outliner.selectedItems()[0]))

        self.viewport.set_segments(segments)
        self.viewport.selected_segments = [self.viewport.selected_segments[0]]

    def reset_view(self):
        self.viewport.reset_transform()

    def show_histogram(self):
        # FIXME - Does not display the histogram correctly the first time you call it after the segmentation. LH
        image = self.viewport.image.flatten()
        plt.hist(image, bins=256, range=(0, 256), density=True)
        plt.show()

    def apply_rag(self):
        parameters = {
            "Threshold": float(self.rag_parameters.threshold.text() or 0.00)/100
        }
        
        self.viewport.segments = self.prev_segments.copy()

        self.amg.addNode(AMGNode({"modifier": rag_modifier.name, "parameters": parameters}))
        logging.info(f"{self.viewport.segments}")
        result = rag_modifier.apply(self.viewport.image, self.viewport.segments, parameters)
        
        self.viewport.set_segments(result)

    def toggle_borders(self):
        self.viewport.toggle_borders()

    def toggle_rag(self):
        self.viewport.toggle_rag()

    def toggle_colors(self):
        self.viewport.toggle_colors()

    def toggle_overlay(self):
        self.viewport.toggle_overlay()