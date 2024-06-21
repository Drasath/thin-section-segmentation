from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from constants import *

class Tutorial(QFrame):
    """
    """
    
    def __init__(self, finish, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.finish = finish
        # set background color to white
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.maximumWidth = 400

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.image = QLabel()
        self.layout().addWidget(self.image)
        pixmap = QPixmap(str(PROJECT_DIRECTORY / "resources" / "images" / "goal.tif"))
        # pixmap = QPixmap(str(PROJECT_DIRECTORY / "datasets" / "example_medium_quality.tif"))
        pixmap = pixmap.scaledToWidth(400)
        self.image.setPixmap(pixmap)
        
        self.image.setAlignment(Qt.AlignCenter)


        self.title = QLabel()
        self.title.setFont(QFont("Arial", 20, QFont.Bold))
        self.layout().addWidget(self.title)

        self.text = QLabel()
        self.layout().addWidget(self.text)

        button_layout = QHBoxLayout()
        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.previous_page)
        button_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        button_layout.addWidget(self.next_button)

        self.layout().addLayout(button_layout)

        self.pages = [
            {
                "title": "Global segmentation",
                "text": "To start, we will segment the image using a global method.\n\n1. Click on the 'Global Parameters' tab.\n2. Set the parameters, and segment the image.\n3. In the menu click on view -> show borders.\n4. Play around with the parameters until you get a reasonably good segmentation.\n5. Move on to the next page."
            }, {
                "title": "Region Adjacency Graph",
                "text": "The next step is to combine some of the sections we've obtained. We do this using a region adjacency graph.\n\n1. Click on the 'RAG Parameters' tab.\n2. Set the threshold, and apply the RAG.\n4. Play around with the parameters a bit.\n Select segments by clicking, select multiple with ctrl-clicking\n5. Manually merge segments by using ctrl+M\n6. Move on to the next page."
            }, {
                "title": "Refinement",
                "text": "To refine our segmentation, we will apply some modifiers.\n\n1. Select a segment by clicking on it.\n2. Click on the 'Refinement' tab.\n3. Select a modifier from the list. (explained in the next page)\n4. Set the parameters and apply the modifier.\n5. Repeat steps 3 and 4 until you are satisfied with the segmentation."
            }, {
                "title": "Modifiers",
                "text": "You can select multiple segments by holding ctrl and left clicking.\nMerge segments by using the edit menu or pressing ctrl+M\nErosion: makes the segments smaller.\nDilation: makes the segments larger.\nOpening: erosion followed by dilation.\nClosing: dilation followed by erosion.\nHistogram Equalization: enhances the contrast of the image.\n(This is more of a preprocessing step to get a better global segmentation)"
            }
        ]
        self.index = -1
        self.next_page()
        self.previous_button.setEnabled(False)
        
    def next_page(self):
        if self.index < len(self.pages):
            self.index += 1
        self.title.setText(self.pages[self.index]["title"])
        self.text.setText(self.pages[self.index]["text"])
        self.previous_button.setEnabled(True)
        if self.index == len(self.pages) - 1:
            self.next_button.setText("Finish")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self.finish)

    def previous_page(self):
        if self.index > 0:
            self.index -= 1
        if self.index == 0:
            self.previous_button.setEnabled(False)
        if self.index != len(self.pages) - 1:
            self.next_button.setText("Next")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(self.next_page)
        self.title.setText(self.pages[self.index]["title"])
        self.text.setText(self.pages[self.index]["text"])
        self.next_button.show()
        