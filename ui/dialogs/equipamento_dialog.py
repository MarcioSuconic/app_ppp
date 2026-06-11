from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QTextEdit, QDoubleSpinBox, QSpinBox,
                               QDialogButtonBox, QMessageBox, QLabel, QCheckBox,
                               QDateEdit)
from PySide6.QtCore import QDate
from models.equipamento import CrudEquipamento
from models.marca import CrudMarca
from models.ambiente import CrudAmbiente

class EquipamentoDialog(QDialog):
    def __init__(self, parent=None, equipamento_id=None):
        super().__init__(parent)
        self.equipamento_id = equipamento_id
        self.setWindowTitle("Novo Equipamento" if equipamento_id is None else "Editar Equipamento")
        self.setMinimumWidth(700)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow(QLabel("Nome do Equipamento:*"), self.nome_edit)
        
        self.marca_combo = QComboBox()
        self.carregar_marcas()
        form_layout.addRow(QLabel("Marca:"), self.marca_combo)
        
        self.modelo_edit = QLineEdit()
        form_layout.addRow(QLabel("Modelo:"), self.modelo_edit)
        
        self.capacidade_edit = QLineEdit()
        self.capacidade_edit.setPlaceholderText("Ex: 50L, 10kg...")
        form_layout.addRow(QLabel("Capacidade:"), self.capacidade_edit)
        
        self.preco_spin = QDoubleSpinBox()
        self.preco_spin.setRange(0, 9999999)
        self.preco_spin.setPrefix("R$ ")
        form_layout.addRow(QLabel("Preço Estimado:"), self.preco_spin)
        
        self.potencia_spin = QSpinBox()
        self.potencia_spin.setRange(0, 999999)
        self.potencia_spin.setSuffix(" W")
        form_layout.addRow(QLabel("Potência (Watts):"), self.potencia_spin)
        
        self.energia_combo = QComboBox()
        self.energia_combo.addItems(["elétrica", "gás", "outros"])
        form_layout.addRow(QLabel("Tipo de Energia:"), self.energia_combo)
        
        self.altura_spin = QSpinBox()
        self.altura_spin.setRange(0, 99999)
        self.altura_spin.setSuffix(" mm")
        form_layout.addRow(QLabel("Altura (mm):"), self.altura_spin)
        
        self.largura_spin = QSpinBox()
        self.largura_spin.setRange(0, 99999)
        self.largura_spin.setSuffix(" mm")
        form_layout.addRow(QLabel("Largura (mm):"), self.largura_spin)
        
        self.profundidade_spin = QSpinBox()
        self.profundidade_spin.setRange(0, 99999)
        self.profundidade_spin.setSuffix(" mm")
        form_layout.addRow(QLabel("Profundidade (mm):"), self.profundidade_spin)
        
        self.data_compra_edit = QDateEdit()
        self.data_compra_edit.setCalendarPopup(True)
        self.data_compra_edit.setDate(QDate.currentDate())
        self.data_compra_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(QLabel("Data de Compra:"), self.data_compra_edit)
        
        self.fornecedor_edit = QLineEdit()
        form_layout.addRow(QLabel("Fornecedor:"), self.fornecedor_edit)
        
        self.numero_serie_edit = QLineEdit()
        form_layout.addRow(QLabel("Número de Série:"), self.numero_serie_edit)
        
        self.ultima_manutencao_edit = QDateEdit()
        self.ultima_manutencao_edit.setCalendarPopup(True)
        self.ultima_manutencao_edit.setDate(QDate.currentDate())
        self.ultima_manutencao_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(QLabel("Última Manutenção:"), self.ultima_manutencao_edit)
        
        self.ambiente_combo = QComboBox()
        self.carregar_ambientes()
        form_layout.addRow(QLabel("Ambiente:"), self.ambiente_combo)
        
        self.ativo_check = QCheckBox("Equipamento ativo")
        self.ativo_check.setChecked(True)
        form_layout.addRow(QLabel(""), self.ativo_check)
        
        self.observacao_edit = QTextEdit()
        self.observacao_edit.setMaximumHeight(80)
        form_layout.addRow(QLabel("Observação:"), self.observacao_edit)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if equipamento_id:
            self.carregar_dados()
    
    def carregar_marcas(self):
        self.marca_combo.clear()
        self.marca_combo.addItem("(Nenhuma)", None)
        for marca in CrudMarca.listar_todos():
            self.marca_combo.addItem(marca["nome"], marca["id"])
    
    def carregar_ambientes(self):
        self.ambiente_combo.clear()
        self.ambiente_combo.addItem("(Nenhum)", None)
        for amb in CrudAmbiente.listar_todos():
            texto = f"{amb['operacao']} → {amb['nome']}"
            self.ambiente_combo.addItem(texto, amb["id"])
    
    def carregar_dados(self):
        dados = CrudEquipamento.buscar_por_id(self.equipamento_id)
        if dados:
            self.nome_edit.setText(dados["nome"] or "")
            
            if dados["marca_id"]:
                idx = self.marca_combo.findData(dados["marca_id"])
                if idx >= 0: self.marca_combo.setCurrentIndex(idx)
            
            self.modelo_edit.setText(dados["modelo"] or "")
            self.capacidade_edit.setText(dados["capacidade"] or "")
            self.preco_spin.setValue(dados["preco_estimado"] or 0)
            self.potencia_spin.setValue(dados["potencia"] or 0)
            
            energia = dados["tipo_energia"] or "elétrica"
            idx_energia = self.energia_combo.findText(energia)
            if idx_energia >= 0: self.energia_combo.setCurrentIndex(idx_energia)
            
            self.altura_spin.setValue(dados["altura_mm"] or 0)
            self.largura_spin.setValue(dados["largura_mm"] or 0)
            self.profundidade_spin.setValue(dados["profundidade_mm"] or 0)
            
            if dados["data_compra"]:
                date = QDate.fromString(dados["data_compra"], "yyyy-MM-dd")
                if date.isValid(): self.data_compra_edit.setDate(date)
            
            self.fornecedor_edit.setText(dados["fornecedor"] or "")
            self.numero_serie_edit.setText(dados["numero_serie"] or "")
            
            if dados["ultima_manutencao"]:
                date = QDate.fromString(dados["ultima_manutencao"], "yyyy-MM-dd")
                if date.isValid(): self.ultima_manutencao_edit.setDate(date)
            
            if dados["ambiente_id"]:
                idx_amb = self.ambiente_combo.findData(dados["ambiente_id"])
                if idx_amb >= 0: self.ambiente_combo.setCurrentIndex(idx_amb)
            
            self.ativo_check.setChecked(dados["ativo"] == 1)
            self.observacao_edit.setText(dados["observacao"] or "")
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "Nome do equipamento é obrigatório.")
            return
        
        marca_id = self.marca_combo.currentData()
        modelo = self.modelo_edit.text().strip()
        capacidade = self.capacidade_edit.text().strip()
        preco = self.preco_spin.value()
        potencia = self.potencia_spin.value()
        tipo_energia = self.energia_combo.currentText()
        altura = self.altura_spin.value()
        largura = self.largura_spin.value()
        profundidade = self.profundidade_spin.value()
        data_compra = self.data_compra_edit.date().toString("yyyy-MM-dd")
        fornecedor = self.fornecedor_edit.text().strip()
        numero_serie = self.numero_serie_edit.text().strip()
        ultima_manutencao = self.ultima_manutencao_edit.date().toString("yyyy-MM-dd")
        ambiente_id = self.ambiente_combo.currentData()
        ativo = self.ativo_check.isChecked()
        observacao = self.observacao_edit.toPlainText().strip()
        
        if self.equipamento_id is None:
            sucesso, msg = CrudEquipamento.criar(
                nome=nome, marca_id=marca_id, modelo=modelo, capacidade=capacidade,
                preco_estimado=preco, data_compra=data_compra, fornecedor=fornecedor,
                numero_serie=numero_serie, ultima_manutencao=ultima_manutencao,
                observacao=observacao, ambiente_id=ambiente_id,
                altura_mm=altura, largura_mm=largura, profundidade_mm=profundidade,
                potencia=potencia, tipo_energia=tipo_energia, ativo=ativo)
        else:
            sucesso, msg = CrudEquipamento.atualizar(
                eid=self.equipamento_id, nome=nome, marca_id=marca_id, modelo=modelo,
                capacidade=capacidade, preco_estimado=preco, data_compra=data_compra,
                fornecedor=fornecedor, numero_serie=numero_serie,
                ultima_manutencao=ultima_manutencao, observacao=observacao,
                ambiente_id=ambiente_id, altura_mm=altura, largura_mm=largura,
                profundidade_mm=profundidade, potencia=potencia,
                tipo_energia=tipo_energia, ativo=ativo)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)