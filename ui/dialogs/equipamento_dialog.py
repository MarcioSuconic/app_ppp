from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QTextEdit, QDoubleSpinBox, QSpinBox,
                               QDialogButtonBox, QMessageBox, QLabel, QCheckBox)
from models.equipamento import CrudEquipamento
from models.ambiente import CrudAmbiente

class EquipamentoDialog(QDialog):
    def __init__(self, parent=None, equipamento_id=None):
        super().__init__(parent)
        self.equipamento_id = equipamento_id
        self.setWindowTitle("Novo Equipamento" if equipamento_id is None else "Editar Equipamento")
        self.setMinimumWidth(700)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Nome
        self.nome_edit = QLineEdit()
        form_layout.addRow(QLabel("Nome do Equipamento:*"), self.nome_edit)
        
        # Marca e Modelo
        self.marca_edit = QLineEdit()
        form_layout.addRow(QLabel("Marca:"), self.marca_edit)
        
        self.modelo_edit = QLineEdit()
        form_layout.addRow(QLabel("Modelo:"), self.modelo_edit)
        
        # Capacidade
        self.capacidade_edit = QLineEdit()
        self.capacidade_edit.setPlaceholderText("Ex: 50L, 10kg, etc.")
        form_layout.addRow(QLabel("Capacidade:"), self.capacidade_edit)
        
        # Potência e Energia
        self.potencia_spin = QSpinBox()
        self.potencia_spin.setRange(0, 999999)
        self.potencia_spin.setSuffix(" W")
        self.potencia_spin.setSpecialValueText("não informado")
        form_layout.addRow(QLabel("Potência (Watts):"), self.potencia_spin)
        
        self.energia_combo = QComboBox()
        self.energia_combo.addItems(["elétrica", "gás", "outros"])
        form_layout.addRow(QLabel("Tipo de Energia:"), self.energia_combo)
        
        # Preço
        self.preco_spin = QDoubleSpinBox()
        self.preco_spin.setRange(0, 9999999)
        self.preco_spin.setPrefix("R$ ")
        form_layout.addRow(QLabel("Preço Estimado:"), self.preco_spin)
        
        # Dimensões
        self.altura_spin = QSpinBox()
        self.altura_spin.setRange(0, 99999)
        self.altura_spin.setSuffix(" mm")
        self.altura_spin.setSpecialValueText("não informado")
        form_layout.addRow(QLabel("Altura (mm):"), self.altura_spin)
        
        self.largura_spin = QSpinBox()
        self.largura_spin.setRange(0, 99999)
        self.largura_spin.setSuffix(" mm")
        self.largura_spin.setSpecialValueText("não informado")
        form_layout.addRow(QLabel("Largura (mm):"), self.largura_spin)
        
        self.profundidade_spin = QSpinBox()
        self.profundidade_spin.setRange(0, 99999)
        self.profundidade_spin.setSuffix(" mm")
        self.profundidade_spin.setSpecialValueText("não informado")
        form_layout.addRow(QLabel("Profundidade (mm):"), self.profundidade_spin)
        
        # Datas e fornecedor
        self.data_compra_edit = QLineEdit()
        self.data_compra_edit.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow(QLabel("Data de Compra:"), self.data_compra_edit)
        
        self.fornecedor_edit = QLineEdit()
        form_layout.addRow(QLabel("Fornecedor:"), self.fornecedor_edit)
        
        self.numero_serie_edit = QLineEdit()
        form_layout.addRow(QLabel("Número de Série:"), self.numero_serie_edit)
        
        self.ultima_manutencao_edit = QLineEdit()
        self.ultima_manutencao_edit.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow(QLabel("Última Manutenção:"), self.ultima_manutencao_edit)
        
        # Ambiente
        self.ambiente_combo = QComboBox()
        self.carregar_ambientes()
        form_layout.addRow(QLabel("Ambiente:"), self.ambiente_combo)
        
        # Ativo
        self.ativo_check = QCheckBox("Equipamento ativo")
        self.ativo_check.setChecked(True)
        form_layout.addRow(QLabel(""), self.ativo_check)
        
        # Observação
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
    
    def carregar_ambientes(self):
        self.ambiente_combo.clear()
        self.ambiente_combo.addItem("(Nenhum / Uso geral)", None)
        for amb in CrudAmbiente.listar_todos():
            texto = f"{amb['operacao']} → {amb['nome']}"
            self.ambiente_combo.addItem(texto, amb["id"])
    
    def carregar_dados(self):
        dados = CrudEquipamento.buscar_por_id(self.equipamento_id)
        if dados:
            self.nome_edit.setText(dados["nome"] or "")
            self.marca_edit.setText(dados["marca"] or "")
            self.modelo_edit.setText(dados["modelo"] or "")
            self.capacidade_edit.setText(dados["capacidade"] or "")
            self.preco_spin.setValue(dados["preco_estimado"] or 0)
            self.potencia_spin.setValue(dados["potencia"] or 0)
            
            energia = dados["tipo_energia"] or "elétrica"
            idx = self.energia_combo.findText(energia)
            if idx >= 0:
                self.energia_combo.setCurrentIndex(idx)
            
            self.altura_spin.setValue(dados["altura_mm"] or 0)
            self.largura_spin.setValue(dados["largura_mm"] or 0)
            self.profundidade_spin.setValue(dados["profundidade_mm"] or 0)
            self.data_compra_edit.setText(dados["data_compra"] or "")
            self.fornecedor_edit.setText(dados["fornecedor"] or "")
            self.numero_serie_edit.setText(dados["numero_serie"] or "")
            self.ultima_manutencao_edit.setText(dados["ultima_manutencao"] or "")
            self.observacao_edit.setText(dados["observacao"] or "")
            self.ativo_check.setChecked(dados["ativo"] == 1)
            
            if dados["ambiente_id"]:
                idx = self.ambiente_combo.findData(dados["ambiente_id"])
                if idx >= 0:
                    self.ambiente_combo.setCurrentIndex(idx)
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do equipamento é obrigatório.")
            return
        
        marca = self.marca_edit.text().strip()
        modelo = self.modelo_edit.text().strip()
        capacidade = self.capacidade_edit.text().strip()
        preco = self.preco_spin.value()
        potencia = self.potencia_spin.value()
        tipo_energia = self.energia_combo.currentText()
        altura = self.altura_spin.value() if self.altura_spin.value() > 0 else None
        largura = self.largura_spin.value() if self.largura_spin.value() > 0 else None
        profundidade = self.profundidade_spin.value() if self.profundidade_spin.value() > 0 else None
        data_compra = self.data_compra_edit.text().strip()
        fornecedor = self.fornecedor_edit.text().strip()
        numero_serie = self.numero_serie_edit.text().strip()
        ultima_manutencao = self.ultima_manutencao_edit.text().strip()
        observacao = self.observacao_edit.toPlainText().strip()
        ambiente_id = self.ambiente_combo.currentData()
        ativo = self.ativo_check.isChecked()
        
        if self.equipamento_id is None:
            sucesso, msg = CrudEquipamento.criar(
                nome=nome, marca=marca, modelo=modelo, capacidade=capacidade,
                preco_estimado=preco, data_compra=data_compra, fornecedor=fornecedor,
                numero_serie=numero_serie, ultima_manutencao=ultima_manutencao,
                observacao=observacao, ambiente_id=ambiente_id,
                altura_mm=altura, largura_mm=largura, profundidade_mm=profundidade,
                potencia=potencia, tipo_energia=tipo_energia, ativo=ativo)
        else:
            sucesso, msg = CrudEquipamento.atualizar(
                eid=self.equipamento_id, nome=nome, marca=marca, modelo=modelo,
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