from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                               QMessageBox, QLabel, QMenuBar, QMenu, QTableView,
                               QHeaderView, QHBoxLayout)
from PySide6.QtCore import Qt, QAbstractTableModel
from views.excel_export import gerar_relatorio_excel
from models.operacao import CrudOperacao
from models.ambiente import CrudAmbiente
from models.equipamento import CrudEquipamento
from models.funcao import CrudFuncao
from models.colaborador import CrudColaborador
from models.tarefa import CrudTarefa
from models.categoria_produto import CrudCategoriaProduto
from models.produto import CrudProduto
from models.categoria_servico import CrudCategoriaServico
from models.servico import CrudServico
from models.marca import CrudMarca
from models.tipo_ferramenta import CrudTipoFerramenta
from models.ferramenta import CrudFerramenta
from ui.dialogs.operacao_dialog import OperacaoDialog
from ui.dialogs.ambiente_dialog import AmbienteDialog
from ui.dialogs.equipamento_dialog import EquipamentoDialog
from ui.dialogs.funcao_dialog import FuncaoDialog
from ui.dialogs.colaborador_dialog import ColaboradorDialog
from ui.dialogs.tarefa_dialog import TarefaDialog
from ui.dialogs.categoria_produto_dialog import CategoriaProdutoDialog
from ui.dialogs.produto_dialog import ProdutoDialog
from ui.dialogs.categoria_servico_dialog import CategoriaServicoDialog
from ui.dialogs.servico_dialog import ServicoDialog
from ui.dialogs.marca_dialog import MarcaDialog
from ui.dialogs.tipo_ferramenta_dialog import TipoFerramentaDialog
from ui.dialogs.ferramenta_dialog import FerramentaDialog

class TableModel(QAbstractTableModel):
    def __init__(self, data, headers, keys=None):
        super().__init__()
        self._data = data
        self._headers = headers
        self._keys = keys if keys else ([list(data[0].keys()) if data else []])
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            if row < len(self._data) and col < len(self._headers):
                if col < len(self._keys):
                    key = self._keys[col]
                else:
                    keys = list(self._data[row].keys())
                    key = keys[col] if col < len(keys) else None
                if key:
                    value = self._data[row].get(key, "")
                    return str(value) if value is not None else ""
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section < len(self._headers):
                return self._headers[section]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PPP - Palmas Project Planner")
        self.setGeometry(100, 100, 1200, 700)
        
        self.current_crud = "operacao"
        self.criar_menu()
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Título
        self.intro_label = QLabel("📋 PPP - Planejamento de Viabilidade")
        self.intro_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #2c3e50; color: white;")
        layout.addWidget(self.intro_label)
        
        # Botão Excel
        self.btn_excel = QPushButton("📊 GERAR RELATÓRIO EXCEL COMPLETO")
        self.btn_excel.clicked.connect(self.gerar_excel)
        self.btn_excel.setStyleSheet("padding: 10px; font-weight: bold; background-color: #27ae60; color: white; font-size: 14px;")
        layout.addWidget(self.btn_excel)        
        
        # Botão Resumo
        self.btn_resumo = QPushButton("🔍 Resumo por Operação")
        self.btn_resumo.clicked.connect(self.abrir_resumo_operacao)
        self.btn_resumo.setStyleSheet("padding: 10px; font-weight: bold; background-color: #3498db; color: white; font-size: 14px;")
        layout.addWidget(self.btn_resumo) 
        
        # Botão Cardápio
        self.btn_cardapio = QPushButton("📋 Cardápio por Operação")
        self.btn_cardapio.clicked.connect(self.abrir_cardapio_operacao)
        self.btn_cardapio.setStyleSheet("padding: 10px; font-weight: bold; background-color: #e67e22; color: white; font-size: 14px;")
        layout.addWidget(self.btn_cardapio)
        
        # Status
        self.status_label = QLabel("✅ CRUD ativo: OPERAÇÕES")
        self.status_label.setStyleSheet("padding: 5px; background-color: #ecf0f1;")
        layout.addWidget(self.status_label)
        
        # Tabela
        self.tableView = QTableView()
        self.tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.verticalHeader().setDefaultSectionSize(30)
        self.tableView.setStyleSheet("""
            QTableView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableView::item:hover {
                background-color: #ecf0f1;
            }
        """)
        layout.addWidget(self.tableView)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        self.btn_novo = QPushButton("➕ NOVO")
        self.btn_editar = QPushButton("✏️ EDITAR")
        self.btn_excluir = QPushButton("🗑️ EXCLUIR")
        self.btn_refresh = QPushButton("🔄 ATUALIZAR")
        
        self.btn_novo.clicked.connect(self.novo_registro)
        self.btn_editar.clicked.connect(self.editar_registro)
        self.btn_excluir.clicked.connect(self.excluir_registro)
        self.btn_refresh.clicked.connect(self.carregar_tabela)
        
        self.btn_editar.setShortcut("Return")
        self.btn_excluir.setShortcut("Delete")
        
        btn_layout.addWidget(self.btn_novo)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_excluir)
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)
        
        self.carregar_tabela()
        self.mostrar_intro()
                      
    def criar_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        cadastro_menu = QMenu("📋 Cadastros", self)
        menubar.addMenu(cadastro_menu)
        
        acao_operacao = cadastro_menu.addAction("🏭 Operações")
        acao_operacao.triggered.connect(lambda: self.mudar_crud("operacao"))
        acao_ambiente = cadastro_menu.addAction("🏢 Ambientes")
        acao_ambiente.triggered.connect(lambda: self.mudar_crud("ambiente"))
        acao_equipamento = cadastro_menu.addAction("🔧 Equipamentos")
        acao_equipamento.triggered.connect(lambda: self.mudar_crud("equipamento"))
        acao_funcao = cadastro_menu.addAction("👔 Funções")
        acao_funcao.triggered.connect(lambda: self.mudar_crud("funcao"))
        acao_colaborador = cadastro_menu.addAction("👥 Colaboradores")
        acao_colaborador.triggered.connect(lambda: self.mudar_crud("colaborador"))
        acao_tarefa = cadastro_menu.addAction("✅ Tarefas")
        acao_tarefa.triggered.connect(lambda: self.mudar_crud("tarefa"))
        
        prod_menu = QMenu("📦 Produtos e Serviços", self)
        menubar.addMenu(prod_menu)

        acao_categoria_produto = prod_menu.addAction("📂 Categorias de Produtos")
        acao_categoria_produto.triggered.connect(lambda: self.mudar_crud("categoria_produto"))
        acao_produto = prod_menu.addAction("🍺 Produtos")
        acao_produto.triggered.connect(lambda: self.mudar_crud("produto"))
        prod_menu.addSeparator()
        acao_categoria_servico = prod_menu.addAction("🔧 Categorias de Serviços")
        acao_categoria_servico.triggered.connect(lambda: self.mudar_crud("categoria_servico"))
        acao_servico = prod_menu.addAction("🛠️ Serviços")
        acao_servico.triggered.connect(lambda: self.mudar_crud("servico"))
        
        # Menu de Ferramentas (antes chamado "Ativos")
        ferramentas_menu = QMenu("🔧 Ferramentas", self)
        menubar.addMenu(ferramentas_menu)
        
        acao_marcas = ferramentas_menu.addAction("🏷️ Marcas")
        acao_marcas.triggered.connect(lambda: self.mudar_crud("marca"))
        acao_tipo_ferramenta = ferramentas_menu.addAction("📂 Tipos de Ferramenta")
        acao_tipo_ferramenta.triggered.connect(lambda: self.mudar_crud("tipo_ferramenta"))
        acao_ferramenta = ferramentas_menu.addAction("🔧 Ferramentas")
        acao_ferramenta.triggered.connect(lambda: self.mudar_crud("ferramenta"))
        
        cadastro_menu.addSeparator()
        acao_sair = cadastro_menu.addAction("🚪 Sair")
        acao_sair.triggered.connect(self.close)
        
        ajuda_menu = QMenu("❓ Ajuda", self)
        menubar.addMenu(ajuda_menu)
        acao_intro = ajuda_menu.addAction("📖 Sobre o PPP")
        acao_intro.triggered.connect(self.mostrar_intro_dialog)
    
    def mostrar_intro(self):
        intro = "PPP - Palmas Project Planner | Ferramenta de Viabilidade | CNPJ único | Operações: Bar, Harmony, Lanchonete/Café, Ateliê"
        self.intro_label.setText(intro)
        
    def abrir_cardapio_operacao(self):
        from ui.dialogs.cardapio_operacao_dialog import CardapioOperacaoDialog
        dialog = CardapioOperacaoDialog(self)
        dialog.exec()
    
    def mostrar_intro_dialog(self):
        intro_texto = """
╔══════════════════════════════════════════════════════════════════╗
║                    PALMAS PROJECT PLANNER (PPP)                   ║
║              Ferramenta de Viabilidade do Negócio                 ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO PRINCIPAL:
Não é um sistema de gestão operacional. É uma CALCULADORA DE VIABILIDADE.

REGRAS DE NEGÓCIO:
• PP é um CNPJ único
• Operações: Bar, Harmony, Lanchonete/Café, Ateliê
• Tarefas são atreladas a UM ambiente OU equipamento
• Cálculo mostra horas/mês por função
• Sócios ajudam no início

FILOSOFIA:
"Primeiro entendo o que precisa ser feito. Depois vejo com quantas pessoas farei."
"""
        QMessageBox.information(self, "Sobre o PPP", intro_texto)
    
    def mudar_crud(self, crud):
        self.current_crud = crud
        nomes = {
            "operacao": "OPERAÇÕES",
            "ambiente": "AMBIENTES",
            "equipamento": "EQUIPAMENTOS",
            "funcao": "FUNÇÕES",
            "colaborador": "COLABORADORES",
            "tarefa": "TAREFAS",
            "categoria_produto": "CATEGORIAS DE PRODUTOS",
            "produto": "PRODUTOS",
            "categoria_servico": "CATEGORIAS DE SERVIÇOS",
            "servico": "SERVIÇOS",
            "marca": "MARCAS",
            "tipo_ferramenta": "TIPOS DE FERRAMENTA",
            "ferramenta": "FERRAMENTAS",
        }
        self.status_label.setText(f"✅ CRUD ativo: {nomes.get(crud, '')}")
        self.setWindowTitle(f"PPP - {nomes.get(crud, '')}")
        self.carregar_tabela()
    
    def carregar_tabela(self):
        dados = []
        headers = []
        keys = []
        
        if self.current_crud == "operacao":
            dados = CrudOperacao.listar_todos()
            headers = ["ID", "Nome", "Descrição", "Ativo"]
            keys = ["id", "nome", "descricao", "ativo"]
            
        elif self.current_crud == "ambiente":
            dados = CrudAmbiente.listar_todos()
            headers = ["ID", "Nome", "Operação", "Descrição", "Ativo"]
            keys = ["id", "nome", "operacao", "descricao", "ativo"]
            
        elif self.current_crud == "equipamento":
            dados = CrudEquipamento.listar_todos()
            headers = ["ID", "Nome", "Marca", "Modelo", "Capacidade", "Potência", "Energia", "Preço", "Ambiente", "Ativo"]
            keys = ["id", "nome", "marca_nome", "modelo", "capacidade", "potencia", "tipo_energia", "preco_estimado", "ambiente_nome", "ativo"]
            
        elif self.current_crud == "funcao":
            dados = CrudFuncao.listar_todos()
            headers = ["ID", "Nome", "Ativo"]
            keys = ["id", "nome", "ativo"]
            
        elif self.current_crud == "colaborador":
            dados = CrudColaborador.listar_todos()
            for d in dados:
                d["funcao_principal_nome"] = d.get("funcao_principal_nome") or "(nenhuma)"
                d["observacao"] = d.get("observacao") or "-"
            headers = ["ID", "Nome", "Sócio", "Função Principal", "Observação", "Ativo"]
            keys = ["id", "nome", "eh_socio", "funcao_principal_nome", "observacao", "ativo"]
            
        elif self.current_crud == "tarefa":
            dados = CrudTarefa.listar_todos()
            for d in dados:
                horas = d["duracao_minutos"] / 60
                d["duracao_minutos"] = f"{horas:.1f}h"
                d["colaborador_nome"] = d.get("colaborador_nome") or "(não atribuído)"
            headers = ["ID", "Tarefa", "Duração", "Frequência", "Função", "Colaborador", "Ambiente", "Equipamento", "Ativo"]
            keys = ["id", "nome", "duracao_minutos", "frequencia_tipo", "funcao_nome", "colaborador_nome", "ambiente_nome", "equipamento_nome", "ativo"]
            
        elif self.current_crud == "categoria_produto":
            dados = CrudCategoriaProduto.listar_todos(apenas_ativos=False)
            headers = ["ID", "Nome", "Descrição", "Ativo"]
            keys = ["id", "nome", "descricao", "ativo"]
            
        elif self.current_crud == "produto":
            dados = CrudProduto.listar_todos(apenas_ativos=False)
            for d in dados:
                d["unidade_nome"] = d.get("unidade_nome") or "-"
                d["categoria_nome"] = d.get("categoria_nome") or "-"
            headers = ["ID", "Nome", "Descrição", "Unidade", "Categoria", "Preço (R$)", "Custo (R$)", "Ativo"]
            keys = ["id", "nome", "descricao", "unidade_nome", "categoria_nome", "preco_sugerido", "custo_producao", "ativo"]
            
        elif self.current_crud == "categoria_servico":
            dados = CrudCategoriaServico.listar_todos(apenas_ativos=False)
            headers = ["ID", "Nome", "Descrição", "Ativo"]
            keys = ["id", "nome", "descricao", "ativo"]
            
        elif self.current_crud == "servico":
            dados = CrudServico.listar_todos(apenas_ativos=False)
            for d in dados:
                d["categoria_nome"] = d.get("categoria_nome") or "-"
            headers = ["ID", "Nome", "Descrição", "Duração (min)", "Categoria", "Preço (R$)", "Custo (R$)", "Ativo"]
            keys = ["id", "nome", "descricao", "duracao_padrao_minutos", "categoria_nome", "preco_sugerido", "custo_producao", "ativo"]
            
        elif self.current_crud == "marca":
            dados = CrudMarca.listar_todos()
            headers = ["ID", "Nome"]
            keys = ["id", "nome"]
            
        elif self.current_crud == "tipo_ferramenta":
            dados = CrudTipoFerramenta.listar_todos()
            headers = ["ID", "Nome"]
            keys = ["id", "nome"]
            
        elif self.current_crud == "ferramenta":
            dados = CrudFerramenta.listar_todos()
            for d in dados:
                d["valor_compra"] = d.get("valor_compra") or 0
                d["ambiente_nome"] = d.get("ambiente_nome") or "-"
                d["marca_nome"] = d.get("marca_nome") or "-"
                d["tipo_nome"] = d.get("tipo_nome") or "-"
            headers = ["ID", "Descrição", "Tipo", "Marca", "Valor (R$)", "Ambiente", "Ativo"]
            keys = ["id", "descricao", "tipo_nome", "marca_nome", "valor_compra", "ambiente_nome", "ativo"]
        
        if not dados:
            dados = []
        
        model = TableModel(dados, headers, keys)
        self.tableView.setModel(model)
        for i in range(len(headers)):
            self.tableView.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.status_label.setText(f"✅ {self.status_label.text().split('|')[0].strip()} | 📊 {len(dados)} registro(s)")
    
    def novo_registro(self):
        dialog = None
        if self.current_crud == "operacao":
            dialog = OperacaoDialog(self)
        elif self.current_crud == "ambiente":
            dialog = AmbienteDialog(self)
        elif self.current_crud == "equipamento":
            dialog = EquipamentoDialog(self)
        elif self.current_crud == "funcao":
            dialog = FuncaoDialog(self)
        elif self.current_crud == "colaborador":
            dialog = ColaboradorDialog(self)
        elif self.current_crud == "tarefa":
            dialog = TarefaDialog(self)
        elif self.current_crud == "categoria_produto":
            dialog = CategoriaProdutoDialog(self)
        elif self.current_crud == "produto":
            dialog = ProdutoDialog(self)
        elif self.current_crud == "categoria_servico":
            dialog = CategoriaServicoDialog(self)
        elif self.current_crud == "servico":
            dialog = ServicoDialog(self)
        elif self.current_crud == "marca":
            dialog = MarcaDialog(self)
        elif self.current_crud == "tipo_ferramenta":
            dialog = TipoFerramentaDialog(self)
        elif self.current_crud == "ferramenta":
            dialog = FerramentaDialog(self)
        
        if dialog and dialog.exec():
            self.carregar_tabela()
    
    def editar_registro(self):
        selection = self.tableView.selectionModel().selectedRows()
        if not selection:
            QMessageBox.warning(self, "Aviso", "Selecione um registro para editar.")
            return
        
        row = selection[0].row()
        model = self.tableView.model()
        id_index = model.index(row, 0)
        registro_id = model.data(id_index)
        
        if not registro_id:
            QMessageBox.warning(self, "Erro", "Não foi possível identificar o registro.")
            return
        
        dialog = None
        if self.current_crud == "operacao":
            dialog = OperacaoDialog(self, int(registro_id))
        elif self.current_crud == "ambiente":
            dialog = AmbienteDialog(self, int(registro_id))
        elif self.current_crud == "equipamento":
            dialog = EquipamentoDialog(self, int(registro_id))
        elif self.current_crud == "funcao":
            dialog = FuncaoDialog(self, int(registro_id))
        elif self.current_crud == "colaborador":
            dialog = ColaboradorDialog(self, int(registro_id))
        elif self.current_crud == "tarefa":
            dialog = TarefaDialog(self, int(registro_id))
        elif self.current_crud == "categoria_produto":
            dialog = CategoriaProdutoDialog(self, int(registro_id))
        elif self.current_crud == "produto":
            dialog = ProdutoDialog(self, int(registro_id))
        elif self.current_crud == "categoria_servico":
            dialog = CategoriaServicoDialog(self, int(registro_id))
        elif self.current_crud == "servico":
            dialog = ServicoDialog(self, int(registro_id))
        elif self.current_crud == "marca":
            dialog = MarcaDialog(self, int(registro_id))
        elif self.current_crud == "tipo_ferramenta":
            dialog = TipoFerramentaDialog(self, int(registro_id))
        elif self.current_crud == "ferramenta":
            dialog = FerramentaDialog(self, int(registro_id))
        
        if dialog and dialog.exec():
            self.carregar_tabela()
    
    def excluir_registro(self):
        selection = self.tableView.selectionModel().selectedRows()
        if not selection:
            QMessageBox.warning(self, "Aviso", "Selecione um registro para excluir.")
            return
        
        row = selection[0].row()
        model = self.tableView.model()
        id_index = model.index(row, 0)
        registro_id = model.data(id_index)
        
        resposta = QMessageBox.question(self, "Confirmar", 
                                        f"⚠️ Excluir registro #{registro_id}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if resposta == QMessageBox.StandardButton.Yes:
            sucesso, msg = False, ""
            if self.current_crud == "operacao":
                sucesso, msg = CrudOperacao.excluir(int(registro_id))
            elif self.current_crud == "ambiente":
                sucesso, msg = CrudAmbiente.excluir(int(registro_id))
            elif self.current_crud == "equipamento":
                sucesso, msg = CrudEquipamento.excluir(int(registro_id))
            elif self.current_crud == "funcao":
                sucesso, msg = CrudFuncao.excluir(int(registro_id))
            elif self.current_crud == "colaborador":
                sucesso, msg = CrudColaborador.excluir(int(registro_id))
            elif self.current_crud == "tarefa":
                sucesso, msg = CrudTarefa.excluir(int(registro_id))
            elif self.current_crud == "categoria_produto":
                sucesso, msg = CrudCategoriaProduto.excluir(int(registro_id))
            elif self.current_crud == "produto":
                sucesso, msg = CrudProduto.excluir(int(registro_id))
            elif self.current_crud == "categoria_servico":
                sucesso, msg = CrudCategoriaServico.excluir(int(registro_id))
            elif self.current_crud == "servico":
                sucesso, msg = CrudServico.excluir(int(registro_id))
            elif self.current_crud == "marca":
                sucesso, msg = CrudMarca.excluir(int(registro_id))
            elif self.current_crud == "tipo_ferramenta":
                sucesso, msg = CrudTipoFerramenta.excluir(int(registro_id))
            elif self.current_crud == "ferramenta":
                sucesso, msg = CrudFerramenta.excluir(int(registro_id))
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", msg)
                self.carregar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)
    
    def abrir_resumo_operacao(self):
        from ui.dialogs.resumo_operacao_dialog import ResumoOperacaoDialog
        dialog = ResumoOperacaoDialog(self)
        dialog.exec()

    def gerar_excel(self):
        try:
            caminho = gerar_relatorio_excel()
            QMessageBox.information(self, "✅ Relatório gerado", 
                                    f"Excel gerado com sucesso!\n\n📁 {caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar Excel:\n{str(e)}")