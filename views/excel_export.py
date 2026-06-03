import openpyxl
from openpyxl.styles import Font, Alignment
from datetime import datetime
import os
from models.tarefa import CrudTarefa
from models.equipamento import CrudEquipamento
from views.resumo_operacao import ResumoOperacao

def gerar_relatorio_excel(caminho_saida=None):
    try:
        if not caminho_saida:
            os.makedirs('relatorios', exist_ok=True)
            caminho_saida = os.path.abspath(f'relatorios/PPP_Relatorio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        
        # ABA 1: Tarefas
        ws1 = wb.create_sheet("Tarefas")
        cabecalho1 = ["Tarefa", "Função", "Colaborador", "Duração (h)", "Frequência", "Vezes/Mês", "Horas/Mês", "Operação", "Ambiente", "Equipamento", "Observação"]
        ws1.append(cabecalho1)
        for t in CrudTarefa.lista_completa_relatorio():
            ws1.append([t["tarefa"], t["funcao"], t["colaborador"], round(t["duracao_minutos"]/60,1), t["frequencia_tipo"], round(t["vezes_mes"],2), round(t["horas_mes"],2), t["operacao"] or "-", t["ambiente"] or "-", t["equipamento"] or "-", t["observacao"] or "-"])
        for cell in ws1[1]: cell.font = Font(bold=True)
        
        # ABA 2: Equipamentos
        ws2 = wb.create_sheet("Equipamentos")
        ws2.append(["Operação", "Ambiente", "Equipamento", "Marca", "Modelo", "Capacidade", "Preço (R$)"])
        for eq in CrudEquipamento.listar_todos():
            ws2.append([eq.get("operacao_nome") or "-", eq.get("ambiente_nome") or "(Uso geral)", eq.get("nome") or "-", eq.get("marca") or "-", eq.get("modelo") or "-", eq.get("capacidade") or "-", eq.get("preco_estimado", 0)])
        for cell in ws2[1]: cell.font = Font(bold=True)
        
        # ABA 3: Resumo PP
        ws3 = wb.create_sheet("Resumo_PP")
        ws3.append(["RESUMO DE HORAS/MÊS POR FUNÇÃO"])
        ws3.append(["Função", "Horas/Mês"])
        for f, h in CrudTarefa.horas_mensais_por_funcao().items():
            ws3.append([f, round(h, 2)])
        ws3.append([])
        ws3.append(["RESUMO DE EQUIPAMENTOS POR OPERAÇÃO"])
        ws3.append(["Operação", "Total Investimento (R$)"])
        for item in CrudEquipamento.total_preco_por_operacao():
            ws3.append([item["operacao"], round(item["total"], 2)])
        ws3.append([])
        ws3.append(["DATAS E INFORMAÇÕES"])
        ws3.append(["Data de Geração", datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
        for cell in ws3[1]: cell.font = Font(bold=True)
        for cell in ws3[3]: cell.font = Font(bold=True)
        
        # ABA 4: Tarefas por Colaborador
        ws4 = wb.create_sheet("Tarefas_por_Colaborador")
        ws4.append(["Colaborador", "Tarefa", "Função", "Duração (h)", "Frequência", "Vezes/Mês", "Horas/Mês", "Operação", "Ambiente", "Equipamento"])
        for item in CrudTarefa.tarefas_por_colaborador():
            ws4.append([item["colaborador"], item["tarefa"], item["funcao"], item["duracao_horas"], item["frequencia"], item["vezes_mes"], item["horas_mes"], item["operacao"], item["ambiente"], item["equipamento"]])
        for cell in ws4[1]: cell.font = Font(bold=True)
        
        # ABA 5: Resumo por Colaborador
        ws5 = wb.create_sheet("Resumo_por_Colaborador")
        ws5.append(["Colaborador", "Total Horas/Mês"])
        for item in CrudTarefa.resumo_horas_por_colaborador():
            ws5.append([item["colaborador"], item["total_horas_mes"]])
        for cell in ws5[1]: cell.font = Font(bold=True)
        
        # ABA 6: Sobre
        ws6 = wb.create_sheet("Sobre_o_PPP")
        for linha in ["PPP - Palmas Project Planner", "Ferramenta de Viabilidade", "", f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"]:
            ws6.append([linha])
        
        for ws in [ws1, ws2, ws3, ws4, ws5, ws6]:
            for col in ws.columns:
                max_len = max([len(str(cell.value)) for cell in col if cell.value] or [10])
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
        
        wb.save(caminho_saida)
        return caminho_saida
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
    
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
    
    # Aba 1: Tarefas
    ws1 = wb.create_sheet("Tarefas")
    tarefas = ResumoOperacao.get_tarefas_por_operacao(operacao_id)
    if tarefas:
        ws1.append(["ID", "Tarefa", "Duração (h)", "Frequência", "Vezes/Mês", "Horas/Mês", "Função", "Colaborador", "Ambiente", "Equipamento", "Observação"])
        for t in tarefas:
            ws1.append([t["id"], t["tarefa"], t["duracao_horas"], t["frequencia"], 
                    t["vezes_mes"], t["horas_mes"], t["funcao"], t["colaborador"], 
                    t["ambiente"], t["equipamento"], t["observacao"]])
        for cell in ws1[1]:
            cell.font = Font(bold=True)
            
    # Aba 2: Cardápio (nova!)
    ws_cardapio = wb.create_sheet("Cardápio")
    produtos = ResumoOperacao.get_produtos_por_operacao(operacao_id)
    servicos = ResumoOperacao.get_servicos_por_operacao(operacao_id)

    row = 1
    if servicos:
        ws_cardapio.cell(row, 1, "SERVIÇOS")
        row += 1
        ws_cardapio.cell(row, 1, "Categoria")
        ws_cardapio.cell(row, 2, "Serviço")
        ws_cardapio.cell(row, 3, "Descrição")
        ws_cardapio.cell(row, 4, "Duração (min)")
        ws_cardapio.cell(row, 5, "Preço (R$)")
        ws_cardapio.cell(row, 6, "Custo (R$)")
        row += 1
        for s in servicos:
            ws_cardapio.cell(row, 1, s["categoria"])
            ws_cardapio.cell(row, 2, s["nome"])
            ws_cardapio.cell(row, 3, s["descricao"])
            ws_cardapio.cell(row, 4, s["duracao"])
            ws_cardapio.cell(row, 5, s["preco"])
            ws_cardapio.cell(row, 6, s["custo"])
            row += 1
        row += 1

    if produtos:
        ws_cardapio.cell(row, 1, "PRODUTOS")
        row += 1
        ws_cardapio.cell(row, 1, "Categoria")
        ws_cardapio.cell(row, 2, "Produto")
        ws_cardapio.cell(row, 3, "Descrição")
        ws_cardapio.cell(row, 4, "Unidade")
        ws_cardapio.cell(row, 5, "Preço (R$)")
        ws_cardapio.cell(row, 6, "Custo (R$)")
        row += 1
        for p in produtos:
            ws_cardapio.cell(row, 1, p["categoria"])
            ws_cardapio.cell(row, 2, p["nome"])
            ws_cardapio.cell(row, 3, p["descricao"])
            ws_cardapio.cell(row, 4, p["unidade"])
            ws_cardapio.cell(row, 5, p["preco"])
            ws_cardapio.cell(row, 6, p["custo"])
            row += 1

    # Ajustar larguras das colunas
    for col in range(1, 7):
        max_len = 0
        for r in range(1, row + 1):
            val = ws_cardapio.cell(r, col).value
            if val:
                max_len = max(max_len, len(str(val)))
        ws_cardapio.column_dimensions[chr(64 + col)].width = min(max_len + 2, 40)
    
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
            
    # ========== ABA 4: Tarefas por Colaborador ==========
    ws4 = wb.create_sheet("Tarefas_por_Colaborador")
    cabecalho4 = ["Colaborador", "Tarefa", "Função", "Duração (h)", "Frequência", "Vezes/Mês", "Horas/Mês", "Operação", "Ambiente", "Equipamento"]
    ws4.append(cabecalho4)

    for item in CrudTarefa.tarefas_por_colaborador():
        ws4.append([
            item["colaborador"],
            item["tarefa"],
            item["funcao"],
            item["duracao_horas"],
            item["frequencia"],
            item["vezes_mes"],
            item["horas_mes"],
            item["operacao"],
            item["ambiente"],
            item["equipamento"]
        ])

    for cell in ws4[1]:
        cell.font = Font(bold=True)

    # ========== ABA 5: Resumo por Colaborador ==========
    ws5 = wb.create_sheet("Resumo_por_Colaborador")
    cabecalho5 = ["Colaborador", "Total Horas/Mês"]
    ws5.append(cabecalho5)

    for item in CrudTarefa.resumo_horas_por_colaborador():
        ws5.append([item["colaborador"], item["total_horas_mes"]])

    for cell in ws5[1]:
        cell.font = Font(bold=True)
            
    # ========== ABA 6: Informações ==========
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

def gerar_aba_cardapio_por_operacao(wb, operacao_id, operacao_nome):
    """Gera aba de cardápio para uma operação específica"""
    from models.produto import CrudProduto
    from models.servico import CrudServico
    from models.categoria_produto import CrudCategoriaProduto
    from models.categoria_servico import CrudCategoriaServico
    
    ws = wb.create_sheet(f"Cardapio_{operacao_nome[:20]}")
    
    # Título
    ws.append([f"CARDÁPIO - {operacao_nome.upper()}"])
    ws.append([])
    
    # SERVIÇOS
    ws.append(["=== SERVIÇOS ==="])
    ws.append(["Categoria", "Serviço", "Descrição", "Duração (min)", "Preço Sugerido (R$)", "Custo (R$)"])
    
    servicos = CrudServico.listar_por_operacao(operacao_id)
    for s in servicos:
        ws.append([
            s.get("categoria_nome") or "-",
            s["nome"],
            s.get("descricao") or "-",
            s.get("duracao_padrao_minutos", 0),
            s.get("preco_sugerido", 0),
            s.get("custo_producao", 0)
        ])
    
    ws.append([])
    
    # PRODUTOS
    ws.append(["=== PRODUTOS ==="])
    ws.append(["Categoria", "Produto", "Descrição", "Unidade", "Preço Sugerido (R$)", "Custo (R$)"])
    
    produtos = CrudProduto.listar_por_operacao(operacao_id)
    for p in produtos:
        unidade = f"{p.get('quantidade_por_unidade', 1)} {p.get('unidade_sigla', 'un')}" if p.get('unidade_sigla') else "-"
        ws.append([
            p.get("categoria_nome") or "-",
            p["nome"],
            p.get("descricao") or "-",
            unidade,
            p.get("preco_sugerido", 0),
            p.get("custo_producao", 0)
        ])
    
    # Ajustar larguras
    for col in ws.columns:
        max_len = max([len(str(cell.value)) for cell in col if cell.value] or [10])
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)