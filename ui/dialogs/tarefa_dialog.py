from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QDoubleSpinBox, QTextEdit, QDialogButtonBox, 
                               QMessageBox, QLabel)
from models.tarefa import CrudTarefa
from models.funcao import CrudFuncao
from models.ambiente import CrudAmbiente
from models.equipamento import CrudEquipamento

class TarefaDialog(QDialog):
    def __init__(self, parent=None, tarefa_id=None):
        super().__init__(parent)
        self.tarefa_id = tarefa_id
        self.setWindowTitle("Nova Tarefa" if tarefa_id is None else "Editar Tarefa")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        self.nome_edit = QLineEdit()
        form_layout.addRow("Nome da Tarefa:*", self.nome_edit)
        
        # Duração em HORAS
        self.duracao_horas = QDoubleSpinBox()
        self.duracao_horas.setRange(0.1, 24)
        self.duracao_horas.setSingleStep(0.5)
        self.duracao_horas.setSuffix(" horas")
        self.duracao_horas.setDecimals(1)
        form_layout.addRow("Duração:*", self.duracao_horas)
        
        self.frequencia_combo = QComboBox()
        self.frequencia_combo.addItems(['diaria', 'semanal', 'quinzenal', 'mensal', 'unica'])
        form_layout.addRow("Frequência:*", self.frequencia_combo)
        
        self.funcao_combo = QComboBox()
        self.carregar_funcoes()
        self.funcao_combo.currentIndexChanged.connect(self.mostrar_aviso_funcionarios)
        form_layout.addRow("Função Responsável:*", self.funcao_combo)
        
        self.aviso_label = QLabel("")
        self.aviso_label.setStyleSheet("font-size: 11px;")
        form_layout.addRow("", self.aviso_label)
        
        self.ambiente_combo = QComboBox()
        self.carregar_ambientes()
        form_layout.addRow("Ambiente (opcional):", self.ambiente_combo)
        
        self.equipamento_combo = QComboBox()
        self.carregar_equipamentos()
        form_layout.addRow("Equipamento (opcional):", self.equipamento_combo)
        
        self.observacao_edit = QTextEdit()
        self.observacao_edit.setMaximumHeight(80)
        form_layout.addRow("Observação:", self.observacao_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if tarefa_id:
            self.carregar_dados()
    
    def carregar_funcoes(self):
        self.funcao_combo.clear()
        for func in CrudFuncao.listar_todos():
            self.funcao_combo.addItem(func["nome"], func["id"])
    
    def mostrar_aviso_funcionarios(self):
        funcao_id = self.funcao_combo.currentData()
        if funcao_id:
            if not CrudTarefa.validar_funcao_tem_colaborador(funcao_id):
                self.aviso_label.setText("⚠️ Nenhum colaborador cadastrado com esta função. Cadastre um colaborador antes de criar a tarefa.")
                self.aviso_label.setStyleSheet("color: red; font-size: 11px;")
            else:
                self.aviso_label.setText("✅ Função válida: há colaborador(es) disponível(eis).")
                self.aviso_label.setStyleSheet("color: green; font-size: 11px;")
        else:
            self.aviso_label.setText("")
    
    def carregar_ambientes(self):
        self.ambiente_combo.clear()
        self.ambiente_combo.addItem("(Nenhum)", None)
        for amb in CrudAmbiente.listar_todos():
            texto = f"{amb['operacao_nome']} → {amb['nome']}"
            self.ambiente_combo.addItem(texto, amb["id"])
    
    def carregar_equipamentos(self):
        self.equipamento_combo.clear()
        self.equipamento_combo.addItem("(Nenhum)", None)
        for eq in CrudEquipamento.listar_todos():
            texto = eq["nome"]
            if eq.get("ambiente_nome"):
                texto += f" ({eq['ambiente_nome']})"
            self.equipamento_combo.addItem(texto, eq["id"])
    
    def carregar_dados(self):
        dados = CrudTarefa.buscar_por_id(self.tarefa_id)
        if dados:
            self.nome_edit.setText(dados["nome"])
            self.duracao_horas.setValue(dados["duracao_minutos"] / 60)
            
            freq_idx = self.frequencia_combo.findText(dados["frequencia_tipo"])
            if freq_idx >= 0:
                self.frequencia_combo.setCurrentIndex(freq_idx)
            
            func_idx = self.funcao_combo.findData(dados["funcao_id"])
            if func_idx >= 0:
                self.funcao_combo.setCurrentIndex(func_idx)
                self.mostrar_aviso_funcionarios()
            
            if dados["ambiente_id"]:
                amb_idx = self.ambiente_combo.findData(dados["ambiente_id"])
                if amb_idx >= 0:
                    self.ambiente_combo.setCurrentIndex(amb_idx)
            
            if dados["equipamento_id"]:
                eq_idx = self.equipamento_combo.findData(dados["equipamento_id"])
                if eq_idx >= 0:
                    self.equipamento_combo.setCurrentIndex(eq_idx)
            
            self.observacao_edit.setText(dados["observacao"] or "")
    
    def aceitar(self):
        nome = self.nome_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome da tarefa é obrigatório.")
            return
        
        duracao_minutos = int(self.duracao_horas.value() * 60)
        frequencia = self.frequencia_combo.currentText()
        funcao_id = self.funcao_combo.currentData()
        ambiente_id = self.ambiente_combo.currentData()
        equipamento_id = self.equipamento_combo.currentData()
        observacao = self.observacao_edit.toPlainText().strip()
        
        if funcao_id is None:
            QMessageBox.warning(self, "Aviso", "Selecione uma função responsável.")
            return
        
        # VALIDAÇÃO ANTES DE SALVAR
        if not CrudTarefa.validar_funcao_tem_colaborador(funcao_id):
            QMessageBox.critical(self, "Erro de Validação", 
                                 "Não é possível salvar esta tarefa.\n\n"
                                 f"Não há nenhum colaborador cadastrado com a função '{self.funcao_combo.currentText()}'.\n\n"
                                 "Cadastre um colaborador e associe a esta função antes de criar a tarefa.")
            return
        
        if self.tarefa_id is None:
            sucesso, msg = CrudTarefa.criar(nome, duracao_minutos, frequencia, funcao_id,
                                           ambiente_id, equipamento_id, observacao)
        else:
            sucesso, msg = CrudTarefa.atualizar(self.tarefa_id, nome, duracao_minutos, frequencia,
                                                funcao_id, ambiente_id, equipamento_id, observacao)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)