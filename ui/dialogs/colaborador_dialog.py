from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QCheckBox, QTextEdit, QDialogButtonBox, 
                               QMessageBox, QListWidget, QListWidgetItem, QPushButton,
                               QHBoxLayout, QGroupBox)
from models.colaborador import CrudColaborador
from models.funcao import CrudFuncao

class ColaboradorDialog(QDialog):
    def __init__(self, parent=None, colaborador_id=None):
        super().__init__(parent)
        self.colaborador_id = colaborador_id
        self.setWindowTitle("Novo Colaborador" if colaborador_id is None else "Editar Colaborador")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Dados principais
        main_group = QGroupBox("Dados Principais")
        form_layout = QFormLayout(main_group)
        
        self.nome_edit = QLineEdit()
        form_layout.addRow("Nome:*", self.nome_edit)
        
        self.socio_check = QCheckBox("É sócio do negócio")
        form_layout.addRow("", self.socio_check)
        
        self.funcao_combo = QComboBox()
        self.carregar_funcoes()
        form_layout.addRow("Função Principal:", self.funcao_combo)
        
        self.observacao_edit = QTextEdit()
        self.observacao_edit.setMaximumHeight(60)
        form_layout.addRow("Observação:", self.observacao_edit)
        
        layout.addWidget(main_group)
        
        # Funções adicionais
        funcoes_group = QGroupBox("Funções Adicionais (o colaborador pode exercer)")
        funcoes_layout = QVBoxLayout(funcoes_group)
        
        self.funcoes_list = QListWidget()
        self.funcoes_list.setMaximumHeight(100)
        funcoes_layout.addWidget(self.funcoes_list)
        
        btn_layout = QHBoxLayout()
        self.btn_adicionar_funcao = QPushButton("+ Adicionar Função")
        self.btn_adicionar_funcao.clicked.connect(self.adicionar_funcao)
        self.btn_remover_funcao = QPushButton("- Remover Selecionada")
        self.btn_remover_funcao.clicked.connect(self.remover_funcao)
        btn_layout.addWidget(self.btn_adicionar_funcao)
        btn_layout.addWidget(self.btn_remover_funcao)
        funcoes_layout.addLayout(btn_layout)
        
        layout.addWidget(funcoes_group)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if colaborador_id:
            self.carregar_dados()
    
    def carregar_funcoes(self):
        self.funcao_combo.clear()
        self.funcao_combo.addItem("(Nenhuma)", None)
        for func in CrudFuncao.listar_todos():
            self.funcao_combo.addItem(func["nome"], func["id"])
    
    def carregar_funcoes_adicionais(self, colaborador_id):
        self.funcoes_list.clear()
        for func in CrudColaborador.listar_funcoes_do_colaborador(colaborador_id):
            item = QListWidgetItem(func["nome"])
            item.setData(1, func["id"])
            self.funcoes_list.addItem(item)
    
    def carregar_dados(self):
        dados = CrudColaborador.buscar_por_id(self.colaborador_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
            self.socio_check.setChecked(dados["eh_socio"] == 1)
            self.observacao_edit.setText(dados["observacao"] or "")
            
            if dados["funcao_principal_id"]:
                idx = self.funcao_combo.findData(dados["funcao_principal_id"])
                if idx >= 0:
                    self.funcao_combo.setCurrentIndex(idx)
            
            self.carregar_funcoes_adicionais(self.colaborador_id)
    
    def adicionar_funcao(self):
        from PySide6.QtWidgets import QInputDialog
        funcoes = CrudFuncao.listar_todos()
        funcoes_dict = {f["nome"]: f["id"] for f in funcoes}
        nomes = list(funcoes_dict.keys())
        
        nome, ok = QInputDialog.getItem(self, "Adicionar Função", "Selecione a função:", nomes, 0, False)
        if ok and nome:
            funcao_id = funcoes_dict[nome]
            # Verifica se já não tem
            for i in range(self.funcoes_list.count()):
                if self.funcoes_list.item(i).data(1) == funcao_id:
                    QMessageBox.warning(self, "Aviso", "Colaborador já possui esta função.")
                    return
            
            if self.colaborador_id:
                sucesso, msg = CrudColaborador.adicionar_funcao(self.colaborador_id, funcao_id)
                if sucesso:
                    item = QListWidgetItem(nome)
                    item.setData(1, funcao_id)
                    self.funcoes_list.addItem(item)
                else:
                    QMessageBox.warning(self, "Erro", msg)
            else:
                # Ainda não foi salvo, só adiciona visualmente (será salvo depois)
                item = QListWidgetItem(nome)
                item.setData(1, funcao_id)
                self.funcoes_list.addItem(item)
    
    def remover_funcao(self):
        item = self.funcoes_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecione uma função para remover.")
            return
        
        funcao_id = item.data(1)
        
        if self.colaborador_id:
            sucesso, msg = CrudColaborador.remover_funcao(self.colaborador_id, funcao_id)
            if sucesso:
                self.funcoes_list.takeItem(self.funcoes_list.row(item))
            else:
                QMessageBox.warning(self, "Erro", msg)
        else:
            self.funcoes_list.takeItem(self.funcoes_list.row(item))
    
    def salvar_funcoes_adicionais(self, colaborador_id):
        """Salva as funções adicionais para um novo colaborador"""
        for i in range(self.funcoes_list.count()):
            funcao_id = self.funcoes_list.item(i).data(1)
            if funcao_id:
                CrudColaborador.adicionar_funcao(colaborador_id, funcao_id)
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do colaborador é obrigatório.")
            return
        
        funcao_principal_id = self.funcao_combo.currentData()
        eh_socio = self.socio_check.isChecked()
        observacao = self.observacao_edit.toPlainText().strip()
        
        if self.colaborador_id is None:
            sucesso, novo_id, msg = CrudColaborador.criar(nome, eh_socio, funcao_principal_id, observacao)
            if sucesso:
                self.salvar_funcoes_adicionais(novo_id)
                QMessageBox.information(self, "Sucesso", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", msg)
        else:
            sucesso, msg = CrudColaborador.atualizar(self.colaborador_id, nome, eh_socio, funcao_principal_id, observacao)
            if sucesso:
                QMessageBox.information(self, "Sucesso", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", msg)