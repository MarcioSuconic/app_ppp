from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QDialogButtonBox, QMessageBox, QLabel)
from models.tipo_ferramenta import CrudTipoFerramenta

class TipoFerramentaDialog(QDialog):
    def __init__(self, parent=None, tipo_id=None):
        super().__init__(parent)
        self.tipo_id = tipo_id
        self.setWindowTitle("Novo Tipo" if tipo_id is None else "Editar Tipo")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow(QLabel("Nome do Tipo:*"), self.nome_edit)
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if tipo_id:
            self.carregar_dados()
    
    def carregar_dados(self):
        dados = CrudTipoFerramenta.buscar_por_id(self.tipo_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do tipo é obrigatório.")
            return
        if self.tipo_id is None:
            sucesso, msg = CrudTipoFerramenta.criar(nome)
        else:
            sucesso, msg = CrudTipoFerramenta.atualizar(self.tipo_id, nome)
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)