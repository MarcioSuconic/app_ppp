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