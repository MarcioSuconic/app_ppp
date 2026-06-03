from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QTextEdit, QComboBox, QDoubleSpinBox, QCheckBox,
                               QDialogButtonBox, QMessageBox, QTabWidget, QWidget,
                               QListWidget, QPushButton, QHBoxLayout, QSpinBox, QLabel, QListWidgetItem)
from PySide6.QtCore import Qt
from models.produto import CrudProduto
from models.categoria_produto import CrudCategoriaProduto
from models.unidade import CrudUnidade
from models.operacao import CrudOperacao
from models.equipamento import CrudEquipamento

class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto_id=None):
        super().__init__(parent)
        self.produto_id = produto_id
        self.setWindowTitle("Novo Produto" if produto_id is None else "Editar Produto")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # Abas
        self.tab_widget = QTabWidget()
        
        # Aba Dados Principais
        self.tab_principal = QWidget()
        self.setup_principal_tab()
        self.tab_widget.addTab(self.tab_principal, "📝 Dados Principais")
        
        # Aba Operações
        self.tab_operacoes = QWidget()
        self.setup_operacoes_tab()
        self.tab_widget.addTab(self.tab_operacoes, "🏭 Operações")
        
        # Aba Equipamentos
        self.tab_equipamentos = QWidget()
        self.setup_equipamentos_tab()
        self.tab_widget.addTab(self.tab_equipamentos, "🔧 Equipamentos")
        
        layout.addWidget(self.tab_widget)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if produto_id:
            self.carregar_dados()
    
    def setup_principal_tab(self):
        layout = QFormLayout(self.tab_principal)
        
        self.nome_edit = QLineEdit()
        layout.addRow(QLabel("Nome do Produto:*"), self.nome_edit)
        
        self.descricao_edit = QTextEdit()
        self.descricao_edit.setMaximumHeight(80)
        layout.addRow(QLabel("Descrição:"), self.descricao_edit)
        
        self.categoria_combo = QComboBox()
        self.carregar_categorias()
        layout.addRow(QLabel("Categoria:"), self.categoria_combo)
        
        self.unidade_combo = QComboBox()
        self.carregar_unidades()
        layout.addRow(QLabel("Unidade:"), self.unidade_combo)
        
        self.quantidade_spin = QDoubleSpinBox()
        self.quantidade_spin.setRange(0.01, 999999)
        self.quantidade_spin.setValue(1.0)
        self.quantidade_spin.setSuffix(" unidade(s)")
        layout.addRow(QLabel("Quantidade por unidade:"), self.quantidade_spin)
        
        self.preco_spin = QDoubleSpinBox()
        self.preco_spin.setRange(0, 999999)
        self.preco_spin.setPrefix("R$ ")
        layout.addRow(QLabel("Preço Sugerido:"), self.preco_spin)
        
        self.custo_spin = QDoubleSpinBox()
        self.custo_spin.setRange(0, 999999)
        self.custo_spin.setPrefix("R$ ")
        layout.addRow(QLabel("Custo de Produção:"), self.custo_spin)
        
        self.ativo_check = QCheckBox("Produto ativo")
        self.ativo_check.setChecked(True)
        layout.addRow(QLabel(""), self.ativo_check)
    
    def setup_operacoes_tab(self):
        layout = QVBoxLayout(self.tab_operacoes)
        
        layout.addWidget(QLabel("Operações onde este produto é vendido:"))
        
        self.operacoes_list = QListWidget()
        self.operacoes_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.carregar_operacoes()
        layout.addWidget(self.operacoes_list)
    
    def setup_equipamentos_tab(self):
        layout = QVBoxLayout(self.tab_equipamentos)
        
        layout.addWidget(QLabel("Equipamentos usados para produzir este produto:"))
        
        self.equipamentos_list = QListWidget()
        self.equipamentos_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.equipamentos_list)
        
        btn_layout = QHBoxLayout()
        self.btn_adicionar_eq = QPushButton("➕ Adicionar Equipamento")
        self.btn_adicionar_eq.clicked.connect(self.adicionar_equipamento)
        self.btn_remover_eq = QPushButton("➖ Remover Selecionado")
        self.btn_remover_eq.clicked.connect(self.remover_equipamento)
        btn_layout.addWidget(self.btn_adicionar_eq)
        btn_layout.addWidget(self.btn_remover_eq)
        layout.addLayout(btn_layout)
    
    def carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("(Nenhuma)", None)
        for cat in CrudCategoriaProduto.listar_todos(apenas_ativos=True):
            self.categoria_combo.addItem(cat["nome"], cat["id"])
    
    def carregar_unidades(self):
        self.unidade_combo.clear()
        self.unidade_combo.addItem("(Nenhuma)", None)
        for unid in CrudUnidade.listar_todos():
            self.unidade_combo.addItem(f"{unid['nome']} ({unid['sigla']})", unid["id"])
    
    def carregar_operacoes(self):
        self.operacoes_list.clear()
        for op in CrudOperacao.listar_todos(apenas_ativos=True):
            item = QListWidgetItem(op["nome"])
            item.setData(Qt.ItemDataRole.UserRole, op["id"])
            self.operacoes_list.addItem(item)
    
    def carregar_equipamentos_vinculados(self):
        self.equipamentos_list.clear()
        if self.produto_id:
            for eq in CrudProduto.listar_equipamentos_vinculados(self.produto_id):
                texto = f"{eq['nome']} - {eq['tempo_minutos']} min"
                item = QListWidgetItem(texto)
                item.setData(Qt.ItemDataRole.UserRole, eq["id"])
                item.setData(Qt.ItemDataRole.UserRole + 1, eq["tempo_minutos"])
                self.equipamentos_list.addItem(item)
    
    def adicionar_equipamento(self):
        from PySide6.QtWidgets import QInputDialog
        equipamentos = CrudEquipamento.listar_todos()
        if not equipamentos:
            QMessageBox.warning(self, "Aviso", "Nenhum equipamento cadastrado.")
            return
        
        nomes = [f"{e['nome']}" for e in equipamentos]
        nome, ok = QInputDialog.getItem(self, "Adicionar Equipamento", "Selecione o equipamento:", nomes, 0, False)
        if ok and nome:
            equipamento = next(e for e in equipamentos if e["nome"] == nome)
            tempo, ok = QInputDialog.getInt(self, "Tempo de Produção", "Tempo em minutos:", 1, 1, 1440)
            if ok:
                if self.produto_id:
                    sucesso, msg = CrudProduto.vincular_equipamento(self.produto_id, equipamento["id"], tempo)
                    if sucesso:
                        self.carregar_equipamentos_vinculados()
                    else:
                        QMessageBox.warning(self, "Erro", msg)
                else:
                    texto = f"{equipamento['nome']} - {tempo} min"
                    item = QListWidgetItem(texto)
                    item.setData(Qt.ItemDataRole.UserRole, equipamento["id"])
                    item.setData(Qt.ItemDataRole.UserRole + 1, tempo)
                    self.equipamentos_list.addItem(item)
    
    def remover_equipamento(self):
        item = self.equipamentos_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecione um equipamento para remover.")
            return
        
        equipamento_id = item.data(Qt.ItemDataRole.UserRole)
        if self.produto_id:
            sucesso, msg = CrudProduto.desvincular_equipamento(self.produto_id, equipamento_id)
            if sucesso:
                self.equipamentos_list.takeItem(self.equipamentos_list.row(item))
            else:
                QMessageBox.warning(self, "Erro", msg)
        else:
            self.equipamentos_list.takeItem(self.equipamentos_list.row(item))
    
    def carregar_dados(self):
        dados = CrudProduto.buscar_por_id(self.produto_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
            self.descricao_edit.setText(dados["descricao"] or "")
            self.preco_spin.setValue(dados["preco_sugerido"] or 0)
            self.custo_spin.setValue(dados["custo_producao"] or 0)
            self.quantidade_spin.setValue(dados["quantidade_por_unidade"] or 1)
            self.ativo_check.setChecked(dados["ativo"] == 1)
            
            if dados["categoria_id"]:
                idx = self.categoria_combo.findData(dados["categoria_id"])
                if idx >= 0:
                    self.categoria_combo.setCurrentIndex(idx)
            
            if dados["unidade_id"]:
                idx = self.unidade_combo.findData(dados["unidade_id"])
                if idx >= 0:
                    self.unidade_combo.setCurrentIndex(idx)
            
            # Carregar operações vinculadas
            operacoes_vinculadas = CrudProduto.listar_operacoes_vinculadas(self.produto_id)
            for i in range(self.operacoes_list.count()):
                item = self.operacoes_list.item(i)
                op_id = item.data(Qt.ItemDataRole.UserRole)
                for op in operacoes_vinculadas:
                    if op["id"] == op_id:
                        item.setSelected(True)
                        break
            
            # Carregar equipamentos vinculados
            self.carregar_equipamentos_vinculados()
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do produto é obrigatório.")
            return
        
        categoria_id = self.categoria_combo.currentData()
        unidade_id = self.unidade_combo.currentData()
        quantidade = self.quantidade_spin.value()
        preco = self.preco_spin.value()
        custo = self.custo_spin.value()
        ativo = self.ativo_check.isChecked()
        descricao = self.descricao_edit.toPlainText().strip()
        
        if self.produto_id is None:
            sucesso, novo_id, msg = CrudProduto.criar(nome, descricao, unidade_id, quantidade,
                                                     custo, preco, categoria_id)
            if sucesso:
                self.produto_id = novo_id
                for i in range(self.operacoes_list.count()):
                    item = self.operacoes_list.item(i)
                    if item.isSelected():
                        CrudProduto.vincular_operacao(self.produto_id, item.data(Qt.ItemDataRole.UserRole))
                for i in range(self.equipamentos_list.count()):
                    item = self.equipamentos_list.item(i)
                    equipamento_id = item.data(Qt.ItemDataRole.UserRole)
                    tempo = item.data(Qt.ItemDataRole.UserRole + 1)
                    if equipamento_id:
                        CrudProduto.vincular_equipamento(self.produto_id, equipamento_id, tempo)
            else:
                QMessageBox.critical(self, "Erro", msg)
                return
        else:
            sucesso, msg = CrudProduto.atualizar(self.produto_id, nome, descricao, unidade_id, quantidade,
                                                custo, preco, categoria_id, ativo)
            if not sucesso:
                QMessageBox.critical(self, "Erro", msg)
                return
            
            operacoes_atuais = [op["id"] for op in CrudProduto.listar_operacoes_vinculadas(self.produto_id)]
            novas_operacoes = []
            for i in range(self.operacoes_list.count()):
                item = self.operacoes_list.item(i)
                if item.isSelected():
                    novas_operacoes.append(item.data(Qt.ItemDataRole.UserRole))
            
            for op_id in operacoes_atuais:
                if op_id not in novas_operacoes:
                    CrudProduto.desvincular_operacao(self.produto_id, op_id)
            for op_id in novas_operacoes:
                if op_id not in operacoes_atuais:
                    CrudProduto.vincular_operacao(self.produto_id, op_id)
        
        QMessageBox.information(self, "Sucesso", msg)
        self.accept()