from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                               QLabel, QTabWidget, QTableView, QHeaderView,
                               QPushButton, QMessageBox, QAbstractItemView)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.operacao import CrudOperacao
from views.resumo_operacao import ResumoOperacao
from views.excel_export import gerar_relatorio_excel_com_abas_operacao

class TableModelResumo(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            if row < len(self._data) and col < len(self._headers):
                keys = list(self._data[row].keys())
                if col < len(keys):
                    value = self._data[row][keys[col]]
                    return str(value) if value is not None else ""
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section < len(self._headers):
                return self._headers[section]
        return None

class ResumoOperacaoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PPP - Resumo por Operação")
        self.setMinimumSize(1000, 700)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Seletor de operação
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Selecione a Operação:"))
        self.operacao_combo = QComboBox()
        self.carregar_operacoes()
        self.operacao_combo.currentIndexChanged.connect(self.carregar_resumos)
        selector_layout.addWidget(self.operacao_combo)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Botões: Exportar e Fechar
        botoes_layout = QHBoxLayout()
        self.btn_exportar = QPushButton("📊 Exportar Resumo para Excel")
        self.btn_exportar.clicked.connect(self.exportar_excel)
        self.btn_fechar = QPushButton("✖️ Fechar")
        self.btn_fechar.clicked.connect(self.close)
        botoes_layout.addWidget(self.btn_exportar)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_fechar)
        layout.addLayout(botoes_layout)
        
        # Abas
        self.tab_widget = QTabWidget()
        
        # Aba 1: Tarefas (nova!)
        self.tab_tarefas = QTableView()
        self.tab_tarefas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_widget.addTab(self.tab_tarefas, "✅ Tarefas")
        
        # Aba 2: Equipamentos
        self.tab_equipamentos = QTableView()
        self.tab_equipamentos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_widget.addTab(self.tab_equipamentos, "🔧 Equipamentos")
        
        # Aba 3: Horas por Função
        self.tab_horas = QTableView()
        self.tab_horas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_widget.addTab(self.tab_horas, "⏱️ Horas/Mês por Função")
        
        layout.addWidget(self.tab_widget)
        
        if self.operacao_combo.count() > 0:
            self.carregar_resumos()
    
    def carregar_operacoes(self):
        self.operacao_combo.clear()
        for op in CrudOperacao.listar_todos():
            self.operacao_combo.addItem(op["nome"], op["id"])
    
    def carregar_resumos(self):
        operacao_id = self.operacao_combo.currentData()
        if not operacao_id:
            return
        
        # Tarefas da operação
        tarefas = ResumoOperacao.get_tarefas_por_operacao(operacao_id)
        if tarefas:
            headers = ["ID", "Tarefa", "Duração (h)", "Frequência", "Vezes/Mês", "Horas/Mês", "Função", "Colaborador", "Ambiente", "Equipamento", "Obs"]
            model = TableModelResumo(tarefas, headers)
            self.tab_tarefas.setModel(model)
            for i in range(len(headers)):
                self.tab_tarefas.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        else:
            self.tab_tarefas.setModel(None)
        
        # Equipamentos
        equipamentos = ResumoOperacao.get_equipamentos_por_operacao(operacao_id)
        if equipamentos:
            headers = ["ID", "Nome", "Marca", "Modelo", "Capacidade", "Ambiente", "Preço (R$)"]
            dados = []
            for eq in equipamentos:
                dados.append({
                    "id": eq["id"],
                    "nome": eq["nome"],
                    "marca": eq["marca"] or "-",
                    "modelo": eq["modelo"] or "-",
                    "capacidade": eq["capacidade"] or "-",
                    "ambiente": eq["ambiente_nome"] or "-",
                    "preco": eq["preco_estimado"] or 0
                })
            model = TableModelResumo(dados, headers)
            self.tab_equipamentos.setModel(model)
            for i in range(len(headers)):
                self.tab_equipamentos.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        else:
            self.tab_equipamentos.setModel(None)
        
        # Horas por função
        horas = ResumoOperacao.get_horas_por_funcao_na_operacao(operacao_id)
        if horas:
            headers = ["Função", "Horas/Mês"]
            model = TableModelResumo(horas, headers)
            self.tab_horas.setModel(model)
            for i in range(len(headers)):
                self.tab_horas.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        else:
            self.tab_horas.setModel(None)
    
    def exportar_excel(self):
        operacao_id = self.operacao_combo.currentData()
        operacao_nome = self.operacao_combo.currentText()
        if not operacao_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma operação primeiro.")
            return
        
        try:
            caminho = gerar_relatorio_excel_com_abas_operacao(operacao_id, operacao_nome)
            QMessageBox.information(self, "✅ Exportado", f"Relatório da operação {operacao_nome}\ngerado em:\n{caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar:\n{str(e)}")