from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QTextEdit, QDialogButtonBox, QMessageBox)
from models.operacao import CrudOperacao

class OperacaoDialog(QDialog):
    def __init__(self, parent=None, operacao_id=None):
        super().__init__(parent)
        self.operacao_id = operacao_id
        self.setWindowTitle("Nova Operação" if operacao_id is None else "Editar Operação")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow("Nome da Operação:", self.nome_edit)
        
        self.descricao_edit = QTextEdit()
        self.descricao_edit.setMaximumHeight(100)
        form_layout.addRow("Descrição:", self.descricao_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if operacao_id:
            self.carregar_dados()
    
    def carregar_dados(self):
        dados = CrudOperacao.buscar_por_id(self.operacao_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
            self.descricao_edit.setText(dados["descricao"] or "")
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        descricao = self.descricao_edit.toPlainText().strip()
        
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome da operação não pode estar vazio.")
            return
        
        if self.operacao_id is None:
            sucesso, msg = CrudOperacao.criar(nome, descricao)
        else:
            sucesso, msg = CrudOperacao.atualizar(self.operacao_id, nome, descricao)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)