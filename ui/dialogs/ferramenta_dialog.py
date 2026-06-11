from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QTextEdit, QDoubleSpinBox, QDateEdit,
                               QDialogButtonBox, QMessageBox, QLabel, QCheckBox)
from PySide6.QtCore import QDate
from models.ferramenta import CrudFerramenta
from models.tipo_ferramenta import CrudTipoFerramenta
from models.marca import CrudMarca
from models.ambiente import CrudAmbiente

class FerramentaDialog(QDialog):
    def __init__(self, parent=None, ferramenta_id=None):
        super().__init__(parent)
        self.ferramenta_id = ferramenta_id
        self.setWindowTitle("Nova Ferramenta" if ferramenta_id is None else "Editar Ferramenta")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.descricao_edit = QLineEdit()
        form_layout.addRow(QLabel("Descrição:*"), self.descricao_edit)
        
        self.tipo_combo = QComboBox()
        self.carregar_tipos()
        form_layout.addRow(QLabel("Tipo:*"), self.tipo_combo)
        
        self.marca_combo = QComboBox()
        self.carregar_marcas()
        form_layout.addRow(QLabel("Marca:"), self.marca_combo)
        
        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setRange(0, 99999)
        self.valor_spin.setPrefix("R$ ")
        form_layout.addRow(QLabel("Valor de Compra:"), self.valor_spin)
        
        self.data_compra_edit = QDateEdit()
        self.data_compra_edit.setCalendarPopup(True)
        self.data_compra_edit.setDate(QDate.currentDate())
        self.data_compra_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow(QLabel("Data de Compra:"), self.data_compra_edit)
        
        self.ambiente_combo = QComboBox()
        self.carregar_ambientes()
        form_layout.addRow(QLabel("Ambiente:"), self.ambiente_combo)
        
        self.ativo_check = QCheckBox("Ferramenta ativa")
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
        
        if ferramenta_id:
            self.carregar_dados()
    
    def carregar_tipos(self):
        self.tipo_combo.clear()
        for tipo in CrudTipoFerramenta.listar_todos():
            self.tipo_combo.addItem(tipo["nome"], tipo["id"])
    
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
        dados = CrudFerramenta.buscar_por_id(self.ferramenta_id)
        if dados:
            self.descricao_edit.setText(dados["descricao"])
            
            idx_tipo = self.tipo_combo.findData(dados["tipo_ferramenta_id"])
            if idx_tipo >= 0: self.tipo_combo.setCurrentIndex(idx_tipo)
            
            if dados["marca_id"]:
                idx_marca = self.marca_combo.findData(dados["marca_id"])
                if idx_marca >= 0: self.marca_combo.setCurrentIndex(idx_marca)
            
            self.valor_spin.setValue(dados["valor_compra"] or 0)
            if dados["data_compra"]:
                date = QDate.fromString(dados["data_compra"], "yyyy-MM-dd")
                if date.isValid(): self.data_compra_edit.setDate(date)
            
            if dados["ambiente_id"]:
                idx_amb = self.ambiente_combo.findData(dados["ambiente_id"])
                if idx_amb >= 0: self.ambiente_combo.setCurrentIndex(idx_amb)
            
            self.ativo_check.setChecked(dados["ativo"] == 1)
            self.observacao_edit.setText(dados["observacao"] or "")
    
    def aceitar(self):
        descricao = self.descricao_edit.text().strip()
        if not descricao:
            QMessageBox.warning(self, "Aviso", "A descrição é obrigatória.")
            return
        
        tipo_id = self.tipo_combo.currentData()
        if not tipo_id:
            QMessageBox.warning(self, "Aviso", "Selecione um tipo.")
            return
        
        marca_id = self.marca_combo.currentData()
        valor = self.valor_spin.value()
        data_compra = self.data_compra_edit.date().toString("yyyy-MM-dd")
        ambiente_id = self.ambiente_combo.currentData()
        ativo = self.ativo_check.isChecked()
        observacao = self.observacao_edit.toPlainText().strip()
        
        if self.ferramenta_id is None:
            sucesso, msg = CrudFerramenta.criar(descricao, tipo_id, marca_id, valor,
                                               data_compra, ambiente_id, observacao, ativo)
        else:
            sucesso, msg = CrudFerramenta.atualizar(self.ferramenta_id, descricao, tipo_id, marca_id,
                                                   valor, data_compra, ambiente_id, observacao, ativo)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)