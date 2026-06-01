from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QTextEdit, QDoubleSpinBox, QDialogButtonBox, QMessageBox)
from models.equipamento import CrudEquipamento
from models.ambiente import CrudAmbiente

class EquipamentoDialog(QDialog):
    def __init__(self, parent=None, equipamento_id=None):
        super().__init__(parent)
        self.equipamento_id = equipamento_id
        self.setWindowTitle("Novo Equipamento" if equipamento_id is None else "Editar Equipamento")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow("Nome do Equipamento:*", self.nome_edit)
        
        self.marca_edit = QLineEdit()
        form_layout.addRow("Marca:", self.marca_edit)
        
        self.modelo_edit = QLineEdit()
        form_layout.addRow("Modelo:", self.modelo_edit)
        
        self.capacidade_edit = QLineEdit()
        form_layout.addRow("Capacidade:", self.capacidade_edit)
        
        self.preco_spin = QDoubleSpinBox()
        self.preco_spin.setRange(0, 9999999)
        self.preco_spin.setPrefix("R$ ")
        self.preco_spin.setMaximumWidth(150)
        form_layout.addRow("Preço Estimado:", self.preco_spin)
        
        self.data_compra_edit = QLineEdit()
        self.data_compra_edit.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow("Data de Compra:", self.data_compra_edit)
        
        self.fornecedor_edit = QLineEdit()
        form_layout.addRow("Fornecedor:", self.fornecedor_edit)
        
        self.numero_serie_edit = QLineEdit()
        form_layout.addRow("Número de Série:", self.numero_serie_edit)
        
        self.ultima_manutencao_edit = QLineEdit()
        self.ultima_manutencao_edit.setPlaceholderText("DD/MM/AAAA")
        form_layout.addRow("Última Manutenção:", self.ultima_manutencao_edit)
        
        self.ambiente_combo = QComboBox()
        self.carregar_ambientes()
        form_layout.addRow("Ambiente:", self.ambiente_combo)
        
        self.observacao_edit = QTextEdit()
        self.observacao_edit.setMaximumHeight(80)
        form_layout.addRow("Observação:", self.observacao_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if equipamento_id:
            self.carregar_dados()
    
    def carregar_ambientes(self):
        self.ambiente_combo.clear()
        self.ambiente_combo.addItem("(Uso geral - sem ambiente definido)", None)
        for amb in CrudAmbiente.listar_todos():
            texto = f"{amb['operacao_nome']} → {amb['nome']}"
            self.ambiente_combo.addItem(texto, amb["id"])
    
    def carregar_dados(self):
        dados = CrudEquipamento.buscar_por_id(self.equipamento_id)
        if dados:
            self.nome_edit.setText(dados["nome"] or "")
            self.marca_edit.setText(dados["marca"] or "")
            self.modelo_edit.setText(dados["modelo"] or "")
            self.capacidade_edit.setText(dados["capacidade"] or "")
            self.preco_spin.setValue(dados["preco_estimado"] or 0)
            self.data_compra_edit.setText(dados["data_compra"] or "")
            self.fornecedor_edit.setText(dados["fornecedor"] or "")
            self.numero_serie_edit.setText(dados["numero_serie"] or "")
            self.ultima_manutencao_edit.setText(dados["ultima_manutencao"] or "")
            self.observacao_edit.setText(dados["observacao"] or "")
            
            if dados["ambiente_id"]:
                idx = self.ambiente_combo.findData(dados["ambiente_id"])
                if idx >= 0:
                    self.ambiente_combo.setCurrentIndex(idx)
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do equipamento é obrigatório.")
            return
        
        preco = self.preco_spin.value()
        ambiente_id = self.ambiente_combo.currentData()
        # Se for None (uso geral), passa None para o banco
        
        if self.equipamento_id is None:
            sucesso, msg = CrudEquipamento.criar(
                nome=nome,
                marca=self.marca_edit.text().strip(),
                modelo=self.modelo_edit.text().strip(),
                capacidade=self.capacidade_edit.text().strip(),
                preco_estimado=preco,
                data_compra=self.data_compra_edit.text().strip(),
                fornecedor=self.fornecedor_edit.text().strip(),
                numero_serie=self.numero_serie_edit.text().strip(),
                ultima_manutencao=self.ultima_manutencao_edit.text().strip(),
                observacao=self.observacao_edit.toPlainText().strip(),
                ambiente_id=ambiente_id
            )
        else:
            sucesso, msg = CrudEquipamento.atualizar(
                eid=self.equipamento_id,
                nome=nome,
                marca=self.marca_edit.text().strip(),
                modelo=self.modelo_edit.text().strip(),
                capacidade=self.capacidade_edit.text().strip(),
                preco_estimado=preco,
                data_compra=self.data_compra_edit.text().strip(),
                fornecedor=self.fornecedor_edit.text().strip(),
                numero_serie=self.numero_serie_edit.text().strip(),
                ultima_manutencao=self.ultima_manutencao_edit.text().strip(),
                observacao=self.observacao_edit.toPlainText().strip(),
                ambiente_id=ambiente_id
            )
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)