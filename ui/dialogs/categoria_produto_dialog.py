from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QTextEdit, QCheckBox, QDialogButtonBox, QMessageBox, QLabel)
from models.categoria_produto import CrudCategoriaProduto

class CategoriaProdutoDialog(QDialog):
    def __init__(self, parent=None, categoria_id=None):
        super().__init__(parent)
        self.categoria_id = categoria_id
        self.setWindowTitle("Nova Categoria" if categoria_id is None else "Editar Categoria")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        self.nome_edit.setPlaceholderText("Ex: Bebidas, Petiscos, Instrumentos...")
        form_layout.addRow(QLabel("Nome da Categoria:*"), self.nome_edit)
        
        self.descricao_edit = QTextEdit()
        self.descricao_edit.setMaximumHeight(100)
        self.descricao_edit.setPlaceholderText("Descrição opcional da categoria")
        form_layout.addRow(QLabel("Descrição:"), self.descricao_edit)
        
        self.ativo_check = QCheckBox("Categoria ativa")
        self.ativo_check.setChecked(True)
        form_layout.addRow(QLabel(""), self.ativo_check)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if categoria_id:
            self.carregar_dados()
    
    def carregar_dados(self):
        dados = CrudCategoriaProduto.buscar_por_id(self.categoria_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
            self.descricao_edit.setText(dados["descricao"] or "")
            self.ativo_check.setChecked(dados["ativo"] == 1)
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome da categoria não pode estar vazio.")
            return
        
        descricao = self.descricao_edit.toPlainText().strip()
        ativo = self.ativo_check.isChecked()
        
        if self.categoria_id is None:
            sucesso, msg = CrudCategoriaProduto.criar(nome, descricao)
            if sucesso:
                if not ativo:
                    categorias = CrudCategoriaProduto.listar_todos(apenas_ativos=False)
                    for cat in categorias:
                        if cat["nome"] == nome:
                            CrudCategoriaProduto.atualizar(cat["id"], nome, descricao, ativo)
                            break
        else:
            sucesso, msg = CrudCategoriaProduto.atualizar(self.categoria_id, nome, descricao, ativo)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)