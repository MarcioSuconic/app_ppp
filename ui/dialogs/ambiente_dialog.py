from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QTextEdit, QComboBox, QDialogButtonBox, QMessageBox)
from models.ambiente import CrudAmbiente
from models.operacao import CrudOperacao

class AmbienteDialog(QDialog):
    def __init__(self, parent=None, ambiente_id=None):
        super().__init__(parent)
        self.ambiente_id = ambiente_id
        self.setWindowTitle("Novo Ambiente" if ambiente_id is None else "Editar Ambiente")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow("Nome do Ambiente:", self.nome_edit)
        
        self.operacao_combo = QComboBox()
        self.carregar_operacoes()
        form_layout.addRow("Operação:", self.operacao_combo)
        
        self.descricao_edit = QTextEdit()
        self.descricao_edit.setMaximumHeight(100)
        form_layout.addRow("Descrição:", self.descricao_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if ambiente_id:
            self.carregar_dados()
    
    def carregar_operacoes(self):
        self.operacao_combo.clear()
        for op in CrudOperacao.listar_todos():
            self.operacao_combo.addItem(op["nome"], op["id"])
    
    def carregar_dados(self):
        dados = CrudAmbiente.buscar_por_id(self.ambiente_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
            self.descricao_edit.setText(dados["descricao"] or "")
            idx = self.operacao_combo.findData(dados["operacao_id"])
            if idx >= 0:
                self.operacao_combo.setCurrentIndex(idx)
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        operacao_id = self.operacao_combo.currentData()
        descricao = self.descricao_edit.toPlainText().strip()
        
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do ambiente não pode estar vazio.")
            return
        if operacao_id is None:
            QMessageBox.warning(self, "Aviso", "Selecione uma operação.")
            return
        
        if self.ambiente_id is None:
            sucesso, msg = CrudAmbiente.criar(nome, operacao_id, descricao)
        else:
            sucesso, msg = CrudAmbiente.atualizar(self.ambiente_id, nome, operacao_id, descricao)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)