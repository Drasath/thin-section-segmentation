from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
from skimage.measure import regionprops
import numpy as np

from constants import *
from modifiers import modifiers

from .viewport import Viewport
from .parameter_tab import ParameterTab
from model.segmentation import segment
from .timeline import Timeline

class MainWindow(QMainWindow):
    """
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        QShortcut(QKeySequence('Ctrl+Z'), self, self.undo)
        QShortcut(QKeySequence('Ctrl+Y'), self, self.redo)
        QShortcut(QKeySequence("Ctrl+M"), self, self.merge_regions)

        self.setWindowTitle("ThinSight")
        self.setWindowIcon(QIcon(str(PROJECT_DIRECTORY / "resources" / "images" / "icon.png")))
        self._setup_ui()
        self.viewport.load_image("C:/Users/Drasath/Desktop/Belangrijke Bestanden/Uni/Bachelor/Year 3/Bachelor Project/thin-section-segmentation/datasets/test.tif")

    def _setup_ui(self):

        # SECTION - Menu Bar
        menu_items = {
            "File": [
                {"Open": self.open_file},
                {"Save": self.save_file},
                {"Preferences": lambda: None},
                {"Recent Files": lambda: None},
                {"Recent Projects": lambda: None},
                {"Export": lambda: None},
                {"Exit": self.close}
            ],
            "Edit": [
                {"Undo": self.undo},
                {"Redo": self.redo},
                {"Merge Regions": self.merge_regions}
            ],
            "View": [
                {"Show Borders": self.toggle_borders},
                {"Show RAG": self.toggle_rag},
                {"Reset View": self.reset_view}
            ],
            "Analysis": [
                {"Show Clustering": self.show_clustering},
                {"Jaccard Distance": self.jaccard_distance}
            ],
            "Segmentation": [
                # {"Refine": },
                {"Segment": self.global_segmentation}
            ],
            "Help": [
                {"About": self.about}
            ]
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

            # SECTION - Timeline
        self.timeline = Timeline()
        viewport_wrapper_layout.addWidget(self.timeline)
            #!SECTION

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)

        self.outliner = QListWidget()
        self.outliner.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.outliner.itemClicked.connect(self.select_region)
        # sidebar_layout.addWidget(self.outliner)

        sidebar_layout.addWidget(QLabel("Tutorial"))

        self.inspector = QTabWidget()
        sidebar_layout.addWidget(self.inspector)

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

        self.global_parameters = QWidget()
        global_parameters_layout = QVBoxLayout()
        self.global_parameters.setLayout(global_parameters_layout)
        global_parameters_layout.addWidget(QLabel("Global Parameters"))
        global_parameters_layout.addWidget(QPushButton("Segment", clicked=self.global_segmentation))
        self.inspector.addTab(self.global_parameters, "Global Parameters")

        self.properties = QWidget()
        properties_layout = QVBoxLayout()
        self.properties.setLayout(properties_layout)
        properties_layout.addWidget(QLabel("Properties"))

        self.inspector.addTab(self.properties, "Properties")

        # for modifier in modifiers:
        #     self.inspector.addTab(ParameterTab(self, modifier), modifier.name)

        #!SECTION

        main_layout.setStretch(0, 3)
        main_layout.setStretch(1, 1)
        self.setCentralWidget(central_widget)
    
    def open_file(self):
        (file_path, _) = QFileDialog.getOpenFileName(filter="Images (*.tif *.tiff)", directory=str(PROJECT_DIRECTORY / "datasets")) # TODO - Allow opening of save files. LH 
        if file_path:
            logging.info(f"File opened: {file_path}")
            self.viewport.load_image(file_path)
        else:
            logging.info("No file selected.")

    def save_file(self):
        logging.info("Saving file...")

    def undo(self):
        pass

    def redo(self):
        pass

    def toggle_borders(self):
        self.viewport.toggle_borders()

    def toggle_rag(self):
        self.viewport.toggle_rag()

    def about(self):
        pass

    def global_segmentation(self):
        # open segments cache to avoid recomputing
        # cache = np.load("segments.npy")
        # if cache is not None:
        #     self.viewport.set_segments(cache)
        #     props = regionprops(cache)
        #     self.outliner.clear()
        #     for prop in props:
        #         self.outliner.addItem(f"Region {prop.label}")
        #     return

        segments, lc = segment(self.viewport.image)
        segments += 1
        self.viewport.set_segments(segments)
        props = regionprops(segments)
        self.outliner.clear()
        for prop in props:
            self.outliner.addItem(f"Region {prop.label}")

        np.save("segments.npy", segments)

    def select_region(self, item):
        self.viewport.selected_segments = [(self.outliner.selectedIndexes()[0].row() + 1)]
        self.viewport.update()

    def apply_modifier(self):
        modifier = modifiers[self.refinement.segmentation_method.currentIndex()]
        parameters = self.refinement.parameters.get_parameters()
        
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
            
                result = modifier.apply(self.viewport.image, mask, parameters)
                segments[result] = segment
                self.viewport.set_segments(segments)

    def merge_regions(self):
        segments = self.viewport.segments.copy()
        for segment in self.viewport.selected_segments:
            segments[segments == segment] = self.viewport.selected_segments[0]

        self.viewport.set_segments(segments)
        self.viewport.selected_segments = [self.viewport.selected_segments[0]]

    def show_clustering(self):
        
        data = []
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(data)

        weights = {'feature1': 1.0, 'feature2': 0.5, 'feature3': 2.0}  # Adjust these as needed

        # Apply weights to normalized data
        weighted_data = normalized_data.copy()
        for feature, weight in weights.items():
            weighted_data[:, data.columns.get_loc(feature)] *= weight

        kmeans = KMeans(n_clusters=3)
        kmeans.fit(weighted_data)
        data['Cluster'] = kmeans.labels_

        plt.scatter(weighted_data[:, 0], weighted_data[:, 1], c=data['Cluster'])
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.title('K-means Clustering with Weighted Features')
        plt.show()

    def jaccard_distance(self, a, b):
        # Load ground truth image
        # For each region in the ground truth image, calculate the Jaccard distance between the ground truth region and all segmented regions, record the minimum Jaccard distance
        # Calculate the average Jaccard distance over all regions
        # Show heatmap of Jaccard distances, where regions with a low accuracy are colored red and regions with a high accuracy are colored green

        pass

    def reset_view(self):
        self.viewport.reset_transform()