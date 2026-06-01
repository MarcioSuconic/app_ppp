from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QDialogButtonBox, QMessageBox)
from models.funcao import CrudFuncao

class FuncaoDialog(QDialog):
    def __init__(self, parent=None, funcao_id=None):
        super().__init__(parent)
        self.funcao_id = funcao_id
        self.setWindowTitle("Nova Função" if funcao_id is None else "Editar Função")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow("Nome da Função:", self.nome_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if funcao_id:
            self.carregar_dados()
    
    def carregar_dados(self):
        dados = CrudFuncao.buscar_por_id(self.funcao_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome da função não pode estar vazio.")
            return
        
        if self.funcao_id is None:
            sucesso, msg = CrudFuncao.criar(nome)
        else:
            sucesso, msg = CrudFuncao.atualizar(self.funcao_id, nome)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)