from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QDialogButtonBox, QMessageBox, QLabel)
from models.marca import CrudMarca

class MarcaDialog(QDialog):
    def __init__(self, parent=None, marca_id=None):
        super().__init__(parent)
        self.marca_id = marca_id
        self.setWindowTitle("Nova Marca" if marca_id is None else "Editar Marca")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow(QLabel("Nome da Marca:*"), self.nome_edit)
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if marca_id:
            self.carregar_dados()
    
    def carregar_dados(self):
        dados = CrudMarca.buscar_por_id(self.marca_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome da marca é obrigatório.")
            return
        if self.marca_id is None:
            sucesso, msg = CrudMarca.criar(nome)
        else:
            sucesso, msg = CrudMarca.atualizar(self.marca_id, nome)
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)