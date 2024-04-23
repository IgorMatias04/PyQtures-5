import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.modified_image = None
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1200, 600)  # Aumentando o tamanho da janela
        self.setWindowTitle('Manipulador de Imagens Avançado com PyQt5')

        self.setStyleSheet("""
            background-color: #f7f5f5;
            QPushButton {
                background-color: #000000;
                border: 2px solid #000000;
                border-radius: 10px;
                color: white;
                padding: 8px 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #8B0000;
                border-color: #8B0000;
            }
        """)

        main_layout = QVBoxLayout()  # Layout principal

        # Layout para as imagens
        images_layout = QHBoxLayout()
        self.originalImageLabel = QLabel('Aqui será exibida sua imagem original')
        self.originalImageLabel.setAlignment(Qt.AlignCenter)
        images_layout.addWidget(self.originalImageLabel)

        self.modifiedImageLabel = QLabel('Aqui será exibida sua imagem editada')
        self.modifiedImageLabel.setAlignment(Qt.AlignCenter)
        images_layout.addWidget(self.modifiedImageLabel)
        main_layout.addLayout(images_layout)

        # Layout para os botões
        btns_layout = QHBoxLayout()
        btns_layout.setAlignment(Qt.AlignCenter)

        self.createButtons(btns_layout)  # Adiciona os botões ao layout
        main_layout.addLayout(btns_layout)

        self.setLayout(main_layout)

    def createButtons(self, layout):
        layout.setSpacing(20)

        self.btnLoad = QPushButton('Carregar Imagem')
        self.btnLoad.clicked.connect(self.loadImage)
        layout.addWidget(self.btnLoad)

        self.btnBlackWhite = QPushButton('Preto e Branco')
        self.btnBlackWhite.clicked.connect(self.convertToBlackWhite)
        layout.addWidget(self.btnBlackWhite)

        self.btnRotate = QPushButton('Rotacionar')
        self.btnRotate.clicked.connect(self.rotateImage)
        layout.addWidget(self.btnRotate)

        self.btnScale = QPushButton('Escalar')
        self.btnScale.clicked.connect(self.scaleImage)
        layout.addWidget(self.btnScale)

        self.btnTranslate = QPushButton('Transladar')
        self.btnTranslate.clicked.connect(self.translateImage)
        layout.addWidget(self.btnTranslate)

        self.btnFlip = QPushButton('Espelhar Original')
        self.btnFlip.clicked.connect(self.flipOriginalImage)
        layout.addWidget(self.btnFlip)

        self.btnFlipModified = QPushButton('Espelhar Editada')
        self.btnFlipModified.clicked.connect(self.flipModifiedImage)
        layout.addWidget(self.btnFlipModified)

        self.btnResetModified = QPushButton('Resetar Editada')
        self.btnResetModified.clicked.connect(self.resetModifiedImage)
        layout.addWidget(self.btnResetModified)

        self.btnSave = QPushButton('Salvar Imagem')
        self.btnSave.clicked.connect(self.saveImage)
        layout.addWidget(self.btnSave)

    def displayOriginalImage(self, img):
        """Atualiza o QLabel com uma nova imagem original."""
        qformat = QImage.Format_Indexed8 if len(
            img.shape) == 2 else QImage.Format_RGB888
        outImage = QImage(img, img.shape[1],
                          img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        self.originalImageLabel.setPixmap(QPixmap.fromImage(outImage).scaled(
            self.originalImageLabel.size(), Qt.KeepAspectRatio))  # type: ignore

    def displayModifiedImage(self, img):
        """Atualiza o QLabel com uma nova imagem editada."""
        qformat = QImage.Format_Indexed8 if len(
            img.shape) == 2 else QImage.Format_RGB888
        outImage = QImage(img, img.shape[1],
                          img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        self.modifiedImageLabel.setPixmap(QPixmap.fromImage(outImage).scaled(
            self.modifiedImageLabel.size(), Qt.KeepAspectRatio))  # type: ignore

    def loadImage(self):
        imagePath, _ = QFileDialog.getOpenFileName()
        if imagePath:
            self.image = cv2.imread(imagePath)
            self.modified_image = self.image.copy()
            self.displayOriginalImage(self.image)
            self.displayModifiedImage(self.modified_image)

    def convertToBlackWhite(self):
        if self.image is not None:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            (thresh, blackWhite) = cv2.threshold(
                gray, 127, 255, cv2.THRESH_BINARY)
            self.modified_image = blackWhite
            self.displayModifiedImage(self.modified_image)

    def rotateImage(self):
        if self.image is not None:
            height, width = self.image.shape[:2]
            center = (width // 2, height // 2)
            rotate_matrix = cv2.getRotationMatrix2D(
                center=center, angle=90, scale=1)
            rotated_image = cv2.warpAffine(
                src=self.image, M=rotate_matrix, dsize=(width, height))
            self.modified_image = rotated_image
            self.displayModifiedImage(self.modified_image)

    def scaleImage(self):
        if self.image is not None:
            scaled_image = cv2.resize(
                self.image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
            self.modified_image = scaled_image
            self.displayModifiedImage(self.modified_image)

    def translateImage(self):
        if self.image is not None:
            translation_matrix = np.float32([[1, 0, 100], [0, 1, 50]])  # type: ignore
            translated_image = cv2.warpAffine(
                self.image, translation_matrix, (self.image.shape[1], self.image.shape[0]))  # type: ignore
            self.modified_image = translated_image
            self.displayModifiedImage(self.modified_image)

    def flipOriginalImage(self):
        if self.image is not None:
            flipped_image = cv2.flip(self.image, 1)  # Horizontal flip
            self.image = flipped_image
            self.displayOriginalImage(self.image)

    def flipModifiedImage(self):
        if self.modified_image is not None:
            flipped_image = cv2.flip(self.modified_image, 1)  # Horizontal flip
            self.modified_image = flipped_image
            self.displayModifiedImage(self.modified_image)

    def resetModifiedImage(self):
        if self.image is not None:
            self.modified_image = self.image.copy()
            self.displayModifiedImage(self.modified_image)

    def saveImage(self):
        if self.modified_image is not None:
            imagePath, _ = QFileDialog.getSaveFileName()
            if imagePath:
                cv2.imwrite(imagePath, self.modified_image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageApp()
    ex.show()
    sys.exit(app.exec_())
