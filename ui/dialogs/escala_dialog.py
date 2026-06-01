from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                               QTimeEdit, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import QTime
from views.crud_escala import CrudEscala

class EscalaDialog(QDialog):
    def __init__(self, parent=None, escala_id=None):
        super().__init__(parent)
        self.escala_id = escala_id
        self.setWindowTitle("Nova Escala" if escala_id is None else "Editar Escala")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.colaborador_combo = QComboBox()
        self.carregar_colaboradores()
        form_layout.addRow("Colaborador:", self.colaborador_combo)
        
        self.operacao_combo = QComboBox()
        self.carregar_operacoes()
        form_layout.addRow("Operação:", self.operacao_combo)
        
        self.dia_combo = QComboBox()
        dias = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        for i, dia in enumerate(dias):
            self.dia_combo.addItem(dia, i)
        form_layout.addRow("Dia da Semana:", self.dia_combo)
        
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setTime(QTime(8, 0))
        form_layout.addRow("Início:", self.hora_inicio)
        
        self.hora_fim = QTimeEdit()
        self.hora_fim.setTime(QTime(17, 0))
        form_layout.addRow("Fim:", self.hora_fim)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Se for edição, carrega os dados
        if escala_id:
            self.carregar_dados()
    
    def carregar_colaboradores(self):
        self.colaborador_combo.clear()
        for colab in CrudEscala.listar_colaboradores():
            self.colaborador_combo.addItem(colab["nome"], colab["id"])
    
    def carregar_operacoes(self):
        self.operacao_combo.clear()
        for op in CrudEscala.listar_operacoes():
            self.operacao_combo.addItem(op["nome"], op["id"])
    
    def carregar_dados(self):
        dados = CrudEscala.buscar_por_id(self.escala_id)
        if dados:
            index_colab = self.colaborador_combo.findData(dados["colaborador_id"])
            if index_colab >= 0:
                self.colaborador_combo.setCurrentIndex(index_colab)
            
            index_op = self.operacao_combo.findData(dados["operacao_id"])
            if index_op >= 0:
                self.operacao_combo.setCurrentIndex(index_op)
            
            self.dia_combo.setCurrentIndex(dados["dia_semana"])
            self.hora_inicio.setTime(QTime.fromString(dados["hora_inicio"], "HH:MM:SS"))
            self.hora_fim.setTime(QTime.fromString(dados["hora_fim"], "HH:MM:SS"))
    
    def aceitar(self):
        colaborador_id = self.colaborador_combo.currentData()
        operacao_id = self.operacao_combo.currentData()
        dia_semana = self.dia_combo.currentData()
        hora_inicio = self.hora_inicio.time().toString("HH:MM:SS")
        hora_fim = self.hora_fim.time().toString("HH:MM:SS")
        
        if colaborador_id is None:
            QMessageBox.warning(self, "Aviso", "Selecione um colaborador.")
            return
        if operacao_id is None:
            QMessageBox.warning(self, "Aviso", "Selecione uma operação.")
            return
        
        if self.escala_id is None:
            sucesso, msg = CrudEscala.criar(colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim)
        else:
            sucesso, msg = CrudEscala.atualizar(self.escala_id, colaborador_id, operacao_id, dia_semana, hora_inicio, hora_fim)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)