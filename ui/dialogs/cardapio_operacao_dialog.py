from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                               QLabel, QTabWidget, QTextEdit, QPushButton, 
                               QMessageBox, QAbstractItemView)
from PySide6.QtCore import Qt
from models.operacao import CrudOperacao
from views.cardapio_operacao import CardapioOperacao
from views.exportar_cardapio_excel_formatado import gerar_cardapio_excel_formatado

class CardapioOperacaoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PPP - Cardápio por Operação")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Seletor de operação
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Selecione a Operação:"))
        self.operacao_combo = QComboBox()
        self.carregar_operacoes()
        self.operacao_combo.currentIndexChanged.connect(self.carregar_cardapio)
        selector_layout.addWidget(self.operacao_combo)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Botões
        botoes_layout = QHBoxLayout()
        self.btn_exportar = QPushButton("📊 Exportar Cardápio para Excel")
        self.btn_exportar.clicked.connect(self.exportar_excel)
        self.btn_fechar = QPushButton("✖️ Fechar")
        self.btn_fechar.clicked.connect(self.close)
        botoes_layout.addWidget(self.btn_exportar)
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_fechar)
        layout.addLayout(botoes_layout)
        
        # Abas com QTextEdit (formato texto, não tabela)
        self.tab_widget = QTabWidget()
        
        # Aba Produtos
        self.tab_produtos = QTextEdit()
        self.tab_produtos.setReadOnly(True)
        self.tab_produtos.setFontFamily("Courier New")
        self.tab_widget.addTab(self.tab_produtos, "🍺 Produtos")
        
        # Aba Serviços
        self.tab_servicos = QTextEdit()
        self.tab_servicos.setReadOnly(True)
        self.tab_servicos.setFontFamily("Courier New")
        self.tab_widget.addTab(self.tab_servicos, "🔧 Serviços")
        
        layout.addWidget(self.tab_widget)
        
        if self.operacao_combo.count() > 0:
            self.carregar_cardapio()
    
    def carregar_operacoes(self):
        self.operacao_combo.clear()
        for op in CrudOperacao.listar_todos(apenas_ativos=True):
            self.operacao_combo.addItem(op["nome"], op["id"])
    
    def carregar_cardapio(self):
        operacao_id = self.operacao_combo.currentData()
        if not operacao_id:
            return
        
        # ========== PRODUTOS ==========
        produtos = CardapioOperacao.get_produtos_por_operacao(operacao_id)
        texto_produtos = ""
        
        if produtos:
            # Agrupar por categoria
            categorias = {}
            for p in produtos:
                cat = p['categoria']
                if cat not in categorias:
                    categorias[cat] = []
                categorias[cat].append(p)
            
            for categoria, itens in categorias.items():
                texto_produtos += f"\n{categoria}\n"
                for item in itens:
                    texto_produtos += f"   {item['nome']}\n"
                    descricao = item['descricao'] if item['descricao'] != '-' else ''
                    preco = f"R$ {item['preco']:.2f}"
                    if descricao:
                        texto_produtos += f"      {descricao}   {preco}\n"
                    else:
                        texto_produtos += f"      {preco}\n"
                texto_produtos += "\n"
        
        if not texto_produtos:
            texto_produtos = "Nenhum produto cadastrado para esta operação."
        
        self.tab_produtos.setText(texto_produtos)
        
        # ========== SERVIÇOS ==========
        servicos = CardapioOperacao.get_servicos_por_operacao(operacao_id)
        texto_servicos = ""
        
        if servicos:
            categorias = {}
            for s in servicos:
                cat = s['categoria']
                if cat not in categorias:
                    categorias[cat] = []
                categorias[cat].append(s)
            
            for categoria, itens in categorias.items():
                texto_servicos += f"\n{categoria}\n"
                for item in itens:
                    nome = item['nome']
                    duracao = f" ({item['duracao']} min)" if item['duracao'] > 0 else ''
                    texto_servicos += f"   {nome}{duracao}\n"
                    descricao = item['descricao'] if item['descricao'] != '-' else ''
                    preco = f"R$ {item['preco']:.2f}"
                    if descricao:
                        texto_servicos += f"      {descricao}   {preco}\n"
                    else:
                        texto_servicos += f"      {preco}\n"
                texto_servicos += "\n"
        
        if not texto_servicos:
            texto_servicos = "Nenhum serviço cadastrado para esta operação."
        
        self.tab_servicos.setText(texto_servicos)
    
    def exportar_excel(self):
        operacao_id = self.operacao_combo.currentData()
        operacao_nome = self.operacao_combo.currentText()
        if not operacao_id:
            QMessageBox.warning(self, "Aviso", "Selecione uma operação primeiro.")
            return
        
        try:
            caminho = gerar_cardapio_excel_formatado(operacao_id, operacao_nome)
            QMessageBox.information(self, "✅ Exportado", 
                                   f"Cardápio da operação {operacao_nome}\ngerado em:\n{caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar:\n{str(e)}")