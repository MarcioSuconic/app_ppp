import openpyxl
from openpyxl.styles import Font, Alignment
from datetime import datetime
import os
from models.tarefa import CrudTarefa
from models.equipamento import CrudEquipamento
from views.resumo_operacao import ResumoOperacao

def gerar_relatorio_excel(caminho_saida=None):
    if not caminho_saida:
        os.makedirs('relatorios', exist_ok=True)
        caminho_saida = f'relatorios/PPP_Relatorio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    wb = openpyxl.Workbook()
    
    # Remove aba padrão
    wb.remove(wb.active)
    
    # ========== ABA 1: Tarefas por Função ==========
    ws1 = wb.create_sheet("Tarefas_por_Funcao")
    cabecalho1 = ["Tarefa", "Função", "Duração (min)", "Frequência", "Vezes/Mês", "Horas/Mês", "Operação", "Ambiente", "Equipamento", "Observação"]
    ws1.append(cabecalho1)
    
    for linha in CrudTarefa.lista_completa_relatorio():
        ws1.append([
            linha["tarefa"],
            linha["funcao"],
            round(linha["duracao_minutos"] / 60, 1),
            linha["frequencia_tipo"],
            round(linha["vezes_mes"], 2),
            round(linha["horas_mes"], 2),
            linha["operacao"] or "-",
            linha["ambiente"] or "-",
            linha["equipamento"] or "-",
            linha["observacao"] or "-"
        ])
    
    # Estilo cabeçalho
    for cell in ws1[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Ajustar larguras
    for col in ws1.columns:
        max_len = 0
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws1.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)
    
    # ========== ABA 2: Equipamentos por Ambiente ==========
    ws2 = wb.create_sheet("Equipamentos")
    cabecalho2 = ["Operação", "Ambiente", "Equipamento", "Marca", "Modelo", "Capacidade", "Preço (R$)", "Data Compra", "Fornecedor", "Série", "Últ. Manutenção", "Observação"]
    ws2.append(cabecalho2)
    
    for eq in CrudEquipamento.listar_todos():
        ws2.append([
            eq.get("operacao_nome") or "-",
            eq.get("ambiente_nome") or "(Uso geral)",
            eq.get("nome") or "-",
            eq.get("marca") or "-",
            eq.get("modelo") or "-",
            eq.get("capacidade") or "-",
            eq.get("preco_estimado", 0),
            eq.get("data_compra") or "-",
            eq.get("fornecedor") or "-",
            eq.get("numero_serie") or "-",
            eq.get("ultima_manutencao") or "-",
            eq.get("observacao") or "-"
        ])
    
    for cell in ws2[1]:
        cell.font = Font(bold=True)
    
    # ========== ABA 3: Resumo PP ==========
    ws3 = wb.create_sheet("Resumo_PP")
    
    # Horas por função
    ws3.append(["RESUMO DE HORAS/MÊS POR FUNÇÃO"])
    ws3.append(["Função", "Horas/Mês"])
    horas_por_funcao = CrudTarefa.horas_mensais_por_funcao()
    for funcao, horas in horas_por_funcao.items():
        ws3.append([funcao, round(horas, 2)])
    
    ws3.append([])
    ws3.append(["RESUMO DE EQUIPAMENTOS POR OPERAÇÃO"])
    ws3.append(["Operação", "Total Investimento (R$)"])
    for item in CrudEquipamento.total_preco_por_operacao():
        ws3.append([item["operacao"], round(item["total"], 2)])
    
    ws3.append([])
    ws3.append(["DATAS E INFORMAÇÕES"])
    ws3.append(["Data de Geração", datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
    
    for cell in ws3[1]:
        cell.font = Font(bold=True)
    for cell in ws3[3]:
        cell.font = Font(bold=True)
    
    # ========== ABA 4: Introdução do Projeto ==========
    ws4 = wb.create_sheet("Sobre_o_PPP")
    intro_texto = [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║                    PALMAS PROJECT PLANNER (PPP)                   ║",
        "║              Ferramenta de Viabilidade do Negócio                 ║",
        "╚══════════════════════════════════════════════════════════════════╝",
        "",
        "OBJETIVO PRINCIPAL:",
        "Não é um sistema de gestão operacional. É uma CALCULADORA DE VIABILIDADE.",
        "Serve para responder: \"O PP dá certo? Quantos funcionários precisamos? O que os sócios farão no início?\"",
        "",
        "REGRAS DE NEGÓCIO:",
        "1. O PP é um CNPJ único. Todas as operações pertencem à mesma empresa.",
        "",
        "2. Operações e seus ambientes:",
        "   - BAR: Cozinha Principal, Cervejaria Baixo, Cervejaria Cima, Produção de Cerveja, Salão Bar, Varanda dos Espetos, Área Kids, Banheiros",
        "   - HARMONY: Palco, Expositor 1, Expositor 2, Expositor 3, Caixa Harmony",
        "   - LANCHONETE/CAFÉ: Cozinha de Apoio, Área Clientes (térreo), Balcão",
        "   - ATELIÊ: Depósito de Tecidos, Área de Costura, Balcão de Atendimento, Provadores, Manequins (vitrine_1), Manequins (vitrine_2)",
        "",
        "3. Harmony funciona à noite, junto com o Bar. A operação Harmony é responsável por cuidar do Palco (que fica no Bar).",
        "",
        "4. Tarefas são atreladas a APENAS UM ambiente OU equipamento.",
        "",
        "5. O cálculo final mostra: tarefa → função → horas por mês necessárias.",
        "",
        "6. Sócios vão 'se lascar' no início, fazendo tarefas de todas as funções.",
        "",
        "FILOSOFIA:",
        "\"Primeiro entendo o que precisa ser feito. Depois vejo com quantas pessoas farei.\"",
        "",
        f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
    ]
    
    for linha in intro_texto:
        ws4.append([linha])
    
    for col in ws4.columns:
        max_len = 0
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws4.column_dimensions[col[0].column_letter].width = min(max_len + 2, 80)
    
    wb.save(caminho_saida)
    return caminho_saida

def gerar_relatorio_excel_com_abas_operacao(operacao_id, operacao_nome, caminho_saida=None):
    """Gera um Excel específico para uma operação, com abas de resumo"""
    from views.resumo_operacao import ResumoOperacao
    from openpyxl.styles import Font
    from datetime import datetime
    import os
    
    if not caminho_saida:
        os.makedirs('relatorios', exist_ok=True)
        caminho_saida = f'relatorios/PPP_{operacao_nome}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    # ========== ABA 1: Tarefas ==========
    ws1 = wb.create_sheet("Tarefas")
    tarefas = ResumoOperacao.get_tarefas_por_operacao(operacao_id)
    if tarefas:
        ws1.append(["ID", "Tarefa", "Duração (h)", "Frequência", "Vezes/Mês", "Horas/Mês", "Função", "Ambiente", "Equipamento", "Observação"])
        for t in tarefas:
            ws1.append([t["id"], t["tarefa"], t["duracao_horas"], t["frequencia"], 
                       t["vezes_mes"], t["horas_mes"], t["funcao"], t["ambiente"], 
                       t["equipamento"], t["observacao"]])
        for cell in ws1[1]:
            cell.font = Font(bold=True)
    
    # ========== ABA 2: Equipamentos ==========
    ws2 = wb.create_sheet("Equipamentos")
    equipamentos = ResumoOperacao.get_equipamentos_por_operacao(operacao_id)
    if equipamentos:
        ws2.append(["ID", "Nome", "Marca", "Modelo", "Capacidade", "Ambiente", "Preço (R$)"])
        for eq in equipamentos:
            ws2.append([eq["id"], eq["nome"], eq["marca"] or "-", eq["modelo"] or "-",
                       eq["capacidade"] or "-", eq["ambiente_nome"] or "-", eq["preco_estimado"] or 0])
        for cell in ws2[1]:
            cell.font = Font(bold=True)
    
    # ========== ABA 3: Horas por Função ==========
    ws3 = wb.create_sheet("Horas_por_Funcao")
    horas = ResumoOperacao.get_horas_por_funcao_na_operacao(operacao_id)
    if horas:
        ws3.append(["Função", "Horas/Mês"])
        for h in horas:
            ws3.append([h["funcao"], round(h["horas_mes"], 2)])
        for cell in ws3[1]:
            cell.font = Font(bold=True)
    
    # ========== ABA 4: Informações ==========
    ws4 = wb.create_sheet("Informações")
    ws4.append(["Operação", operacao_nome])
    ws4.append(["Data de Geração", datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
    
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = 0
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
    
    wb.save(caminho_saida)
    return caminho_saida