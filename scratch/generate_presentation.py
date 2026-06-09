import os
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

class PresentationCanvas(canvas.Canvas):
    """
    Canvas customizado para desenhar elementos de fundo (headers, footers e numeração)
    nas páginas de uma apresentação em formato Landscape (A4 horizontal).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_decorations(page_count)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # A4 em modo paisagem: Largura = 841.89, Altura = 595.27
        w, h = 841.89, 595.27
        
        if self._pageNumber > 1:
            # --- HEADER DA TELA (SLIDES) ---
            # Faixa superior azul-escura/navy
            self.setFillColor(HexColor("#1A1C23"))
            self.rect(0, h - 60, w, 60, fill=True, stroke=False)
            
            # Linha de destaque Neon Teal abaixo da faixa superior
            self.setFillColor(HexColor("#00FFCC"))
            self.rect(0, h - 63, w, 3, fill=True, stroke=False)
            
            # --- FOOTER DA TELA (SLIDES) ---
            # Faixa inferior cinza claro
            self.setFillColor(HexColor("#F8F9FA"))
            self.rect(0, 0, w, 35, fill=True, stroke=False)
            
            # Linha de destaque Neon Teal acima do footer
            self.setFillColor(HexColor("#00FFCC"))
            self.rect(0, 35, w, 2, fill=True, stroke=False)
            
            # Texto da marca (Esquerda)
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(HexColor("#7000FF"))
            self.drawString(36, 15, "BESx SIMULATOR")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(HexColor("#666666"))
            self.drawString(130, 15, "|   Apresentação de Telas e Manual Operacional")
            
            # Numeração das páginas (Direita)
            page_str = f"Slide {self._pageNumber} de {page_count}"
            self.setFont("Helvetica", 8)
            self.setFillColor(HexColor("#666666"))
            self.drawRightString(w - 36, 15, page_str)
            
        else:
            # --- CAPA (PÁGINA 1) DECORAÇÕES ---
            # Faixa vertical decorativa azul-escura à esquerda
            self.setFillColor(HexColor("#1A1C23"))
            self.rect(0, 0, 240, h, fill=True, stroke=False)
            
            # Linha Neon Teal vertical separando a faixa escura da parte clara
            self.setFillColor(HexColor("#00FFCC"))
            self.rect(240, 0, 5, h, fill=True, stroke=False)
            
            # Watermark vertical na barra esquerda
            self.saveState()
            self.translate(70, 80)
            self.rotate(90)
            self.setFont("Helvetica-Bold", 46)
            self.setFillColor(HexColor("#2C2E38")) # Cor escura para baixo contraste na barra
            self.drawString(0, 0, "B E S x   S I M U L A T O R")
            self.restoreState()
            
            # Canto superior direito com detalhe roxo tecnológico
            self.setFillColor(HexColor("#7000FF"))
            p = self.beginPath()
            p.moveTo(w - 120, h)
            p.lineTo(w, h)
            p.lineTo(w, h - 120)
            p.close()
            self.drawPath(p, fill=True, stroke=False)
            
        self.restoreState()

def create_placeholder_table(html_message, width, height):
    """Gera uma tabela estilizada atuando como placeholder com borda arredondada."""
    styles = getSampleStyleSheet()
    p_style = ParagraphStyle(
        'PlaceholderMsg',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=15,
        textColor=HexColor('#555555'),
        alignment=1 # Center
    )
    p = Paragraph(html_message, p_style)
    tb = Table([[p]], colWidths=[width], rowHeights=[height])
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#F8F9FA")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1.5, HexColor("#DDE1E5")),
        ('LEFTPADDING', (0,0), (-1,-1), 25),
        ('RIGHTPADDING', (0,0), (-1,-1), 25),
    ]))
    return tb

def get_slide_image(filename, width=760, height=410):
    """
    Retorna a captura de tela (Image flowable) caso ela exista na pasta 'docs/images/'.
    Caso contrário, retorna um card de placeholder informando ao usuário como salvar o print correspondente.
    """
    img_dir = os.path.join("docs", "images")
    os.makedirs(img_dir, exist_ok=True)
    filepath = os.path.join(img_dir, filename)
    
    if os.path.exists(filepath):
        try:
            return Image(filepath, width=width, height=height)
        except Exception as e:
            return create_placeholder_table(
                f"<b>Erro ao carregar arquivo de imagem:</b><br/>"
                f"<font color='#FF0055'>{filename}</font><br/><br/>"
                f"Erro físico: {str(e)}", 
                width, 
                height
            )
    else:
        msg = (
            f"<b>Captura de Tela Pendente (Prints Automatizados):</b><br/><br/>"
            f"O sistema não localizou a imagem widescreen da interface em alta definição.<br/>"
            f"Por favor, execute o script de automação de capturas no terminal:<br/>"
            f"<font color='#7000FF'><b>python scratch/automate_screenshots.py</b></font><br/><br/>"
            f"Isso salvará automaticamente o print PNG com as simulações executadas no caminho:<br/>"
            f"<font color='#00a385'><b>{filepath}</b></font>"
        )
        return create_placeholder_table(msg, width, height)

def create_presentation_pdf(output_filename="Apresentacao_Telas_BESx.pdf"):
    # Configuração do documento (Margens de 36pt = 0.5 inch em todas as direções)
    # Largura útil: 841.89 - 72 = 769.89 pt
    # Altura útil: 595.27 - 72 = 523.27 pt (com cabeçalho e rodapé, a altura do flowable útil será menor)
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=landscape(A4),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # --- CUSTOM STYLES ---
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=HexColor('#1A1C23'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=15,
        leading=20,
        textColor=HexColor('#7000FF'),
        spaceAfter=30
    )
    
    cover_desc_style = ParagraphStyle(
        'CoverDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=HexColor('#555555')
    )
    
    cover_meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=14,
        textColor=HexColor('#7000FF')
    )
    
    slide_title_style = ParagraphStyle(
        'SlideHeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=HexColor('#FFFFFF'), 
        spaceAfter=0
    )
    
    section_title_style = ParagraphStyle(
        'SlideSectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=HexColor('#7000FF'),
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15.5,
        textColor=HexColor('#333333'),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    table_lbl_style = ParagraphStyle(
        'TableLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=HexColor('#1A1C23')
    )
    
    table_val_style = ParagraphStyle(
        'TableVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=HexColor('#444444')
    )
    
    table_val_bold_style = ParagraphStyle(
        'TableValBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=HexColor('#7000FF')
    )

    story = []
    
    # ==========================================
    # SLIDE 1: CAPA DA APRESENTAÇÃO
    # ==========================================
    cover_text_elements = [
        Spacer(1, 40),
        Paragraph("BESx", title_style),
        Paragraph("Battery Energy Storage System Simulator", ParagraphStyle('CoverSub1', parent=title_style, fontSize=20, leading=24, spaceAfter=8)),
        Paragraph("MANUAL VISUAL & OPERACIONAL DE TELAS", subtitle_style),
        Paragraph(
            "Apresentação técnica passo a passo das telas do ecossistema BESx: "
            "do upload do perfil de carga do cliente e modelagem termodinâmica de hardware "
            "ao processamento avançado de fadiga (Rainflow) e auditoria física de motores de cálculo. "
            "Inclui imagens widescreen em alta resolução capturadas automaticamente do sistema sob simulações reais.",
            cover_desc_style
        ),
        Spacer(1, 80),
        Paragraph("<b>Desenvolvido por:</b> Diretoria de Tecnologia & P&D LEDAX", cover_meta_style),
        Paragraph("<b>Versão do Sistema:</b> v2.0 (Kinetic Blueprint)", cover_meta_style),
        Paragraph("<b>Tecnologias:</b> Streamlit, Playwright, ReportLab, PLECS Solver, Gemini IA", cover_meta_style),
        Paragraph("<b>Data de Publicação:</b> Junho de 2026", cover_meta_style)
    ]
    
    cover_table = Table(
        [[Spacer(1, 10), cover_text_elements]], 
        colWidths=[220, 510]
    )
    cover_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (1,0), (1,0), 20),
        ('RIGHTPADDING', (1,0), (1,0), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(cover_table)
    story.append(PageBreak())
    
    # ==========================================
    # FUNÇÕES AUXILIARES DE RENDERIZAÇÃO
    # ==========================================
    def add_slide_header(title_text):
        p = Paragraph(title_text, slide_title_style)
        tb = Table([[p]], colWidths=[769.89])
        tb.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(tb)
        story.append(Spacer(1, 25))
        
    def add_full_image_slide(title_text, filename):
        add_slide_header(title_text)
        img = get_slide_image(filename, width=760, height=410)
        tb = Table([[img]], colWidths=[769.89], rowHeights=[415])
        tb.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(tb)
        story.append(PageBreak())

    # ==========================================
    # SLIDE 2: INTRODUÇÃO E ARQUITETURA GERAL
    # ==========================================
    add_slide_header("Arquitetura de Domínio & Fluxo de Operação")
    
    col1_content = [
        Paragraph("A Filosofia do BESx", section_title_style),
        Paragraph(
            "O BESx foi concebido para resolver o gargalo do dimensionamento e simulação físico-química "
            "de sistemas de armazenamento de energia em baterias (BESS) aplicados a consumidores industriais/comerciais. "
            "Seguindo o paradigma de <b>Clean Architecture</b>, a lógica de domínio matemático de física e degradação "
            "é totalmente agnóstica em relação à interface do usuário (UI Streamlit).",
            body_style
        ),
        Paragraph(
            "Esta estrutura garante robustez na integração com fontes de dados variadas e permite que os "
            "motores computacionais sejam auditados por suites de testes automatizadas no backend.",
            body_style
        ),
        Spacer(1, 10),
        Paragraph("Os 3 Pilares Científicos do Core:", section_title_style),
        Paragraph("<b>1. Contagem de Fadiga Rainflow Incremental:</b> Extração ponto a ponto de microciclos de DOD (Depth of Discharge), prevenindo reprocessamentos desnecessários e mantendo a agilidade da UI.", bullet_style),
        Paragraph("<b>2. Acumulação de Dano Não-Linear (Stroe):</b> A degradação cíclica não é linear. O BESx aplica a lei geométrica para fadiga cíclica e lei de potência exponencial para degradação em repouso (calendária).", bullet_style),
        Paragraph("<b>3. Motor de Qualidade de Energia:</b> Processamento de triângulo de potências (Ativa, Reativa e Aparente) para simular compensação de reativos e correção ativa do fator de potência.", bullet_style)
    ]
    
    col2_content = [
        Paragraph("A Jornada de Operação do Usuário", section_title_style),
        Paragraph(
            "O sistema é estruturado em um assistente de <b>6 passos ordenados</b> na barra lateral. "
            "Abaixo estão os resumos operacionais de cada tela que detalharemos a seguir:",
            body_style
        )
    ]
    
    steps_data = [
        [Paragraph("<b>Passo 1</b>", table_lbl_style), Paragraph("<b>Regras do Local & EMS</b>", table_val_bold_style), Paragraph("Upload de dados, análise do fator de carga e definição da lógica de despacho.", table_val_style)],
        [Paragraph("<b>Passo 2</b>", table_lbl_style), Paragraph("<b>Hardware da Bateria</b>", table_val_bold_style), Paragraph("Química (LFP/NMC), capacidade total, limites de SOC e faixas de temperatura.", table_val_style)],
        [Paragraph("<b>Passo 3</b>", table_lbl_style), Paragraph("<b>Execução Física</b>", table_val_bold_style), Paragraph("Configuração do motor (Python vs PLECS), tempo de vida e dashboard de execução.", table_val_style)],
        [Paragraph("<b>Passo 4</b>", table_lbl_style), Paragraph("<b>Resultados Detalhados</b>", table_val_bold_style), Paragraph("Fadiga por Rainflow, curvas SOH/SOC elétricas e exportação de relatórios.", table_val_style)],
        [Paragraph("<b>Passo 5</b>", table_lbl_style), Paragraph("<b>Comparativo A/B</b>", table_val_bold_style), Paragraph("Cruzamento múltiplo de simulações, realce de divergências e insights com IA.", table_val_style)],
        [Paragraph("<b>Passo 6</b>", table_lbl_style), Paragraph("<b>Configurações & Validação</b>", table_val_bold_style), Paragraph("Calibração de coeficientes químicos e auditoria de simulação (TC1/2/3).", table_val_style)],
    ]
    
    st_table = Table(steps_data, colWidths=[55, 115, 205])
    st_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#F8F9FA")),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [HexColor("#F8F9FA"), HexColor("#FFFFFF")]),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#E9ECEF")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    col2_content.append(Spacer(1, 5))
    col2_content.append(st_table)
    
    slide_table = Table([[col1_content, col2_content]], colWidths=[370, 390])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 3: PASSO 1 - REGRAS DO LOCAL (CONTEÚDO)
    # ==========================================
    add_slide_header("Passo 1: Regras do Local & Estratégia EMS - Especificação")
    
    col1_p1 = [
        Paragraph("Módulo de Carga e Mapeamento Eletrotécnico", section_title_style),
        Paragraph(
            "Esta tela é a porta de entrada para a simulação do cliente. "
            "O engenheiro insere os nomes identificadores e faz o upload "
            "do perfil de consumo (CSV/Excel).",
            body_style
        ),
        Paragraph("<b>Mapeamento Inteligente:</b> Seleção de colunas de Tempo, Carga ativa e opcionais de Fator de Potência, Reativos (kVARh) e Aparente (kVAh) para calibração fina.", bullet_style),
        Paragraph("<b>Normalização Física (REQ-08):</b> Conversão automática de dados brutos de energia (Wh/kWh) para potência instantânea (W) baseando-se no delta amostral ($dt$), escalonando tudo para Watts.", bullet_style),
        Paragraph("<b>Lógicas de Despacho Operacional (EMS):</b>", section_title_style),
        Paragraph("<b>• Peak Shaving:</b> Apara picos de demanda acima do limite em kW com margens configuráveis.", bullet_style),
        Paragraph("<b>• Load Shifting:</b> Carga em horário barato e descarga na ponta, integrando feriados da UF selecionada.", bullet_style),
        Paragraph("<b>• Power Factor Correction:</b> Despacho de potência reativa capacitiva/indutiva limitado pelo inversor.", bullet_style),
        Paragraph("<b>• Combined:</b> Une limites do Peak Shaving com janelas horárias do Load Shifting.", bullet_style),
    ]
    
    col2_p1 = [
        Paragraph("Diagnóstico Avançado de Carga (Tabs do Painel)", section_title_style),
        Paragraph(
            "Ao processar os dados, a interface exibe abas interativas com gráficos Plotly "
            "e métricas consolidadas em tempo real:",
            body_style
        ),
        Paragraph("<b>1. Aba Resumo Geral:</b> Exibe KPIs essenciais (Pmax, percentil P95, fator de carga) e o gráfico interativo 'Comparativo de Despacho EMS'.", bullet_style),
        Paragraph("<b>2. Aba Ponta & Energia:</b> Mostra a energia total em kWh, consumo médio diário, projeções mensais e a participação de energia na ponta.", bullet_style),
        Paragraph("<b>3. Aba Padrões:</b> Apresenta um mapa térmico bidimensional da demanda média por hora e dia da semana, identificando padrões sazonais.", bullet_style),
        Paragraph("<b>4. Aba Qualidade de Energia (PFC):</b> Compara o Fator de Potência original contra a curva ajustada após a compensação do BESS.", bullet_style),
        Paragraph("<b>5. Aba Diagnóstico Técnico:</b> Valida a consistência temporal (amostragem dT, quantidade de registros, dias úteis). O sistema exige um mínimo de 24 horas de telemetria para desbloquear a simulação.", bullet_style),
        Paragraph("<b>Injeção na Base:</b> Salva os dados processados em um arquivo binário serializado (.pkl) de alta performance no banco de dados.", bullet_style),
    ]
    
    slide_table = Table([[col1_p1, col2_p1]], colWidths=[385, 385])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 4: PASSO 1 - REGRAS DO LOCAL (VISUAL)
    # ==========================================
    add_full_image_slide("Passo 1: Regras do Local & Estratégia EMS - Interface Visual", "step1_rules.png")
    
    # ==========================================
    # SLIDE 5: PASSO 2 - HARDWARE DA BATERIA (CONTEÚDO)
    # ==========================================
    add_slide_header("Passo 2: Hardware da Bateria & Limites - Especificação")
    
    col1_p2 = [
        Paragraph("Modelagem Química de Células de Lítio", section_title_style),
        Paragraph(
            "O comportamento eletrotérmico e químico da bateria é configurado neste passo. "
            "O BESx traz um banco de perfis químicos pré-configurados e curvas científicas mapeadas no <i>config.py</i>.",
            body_style
        ),
        Paragraph("<b>Seleção de Perfil (Química):</b> Seleção de modelos com curvas de Tensão de Circuito Aberto (OCV) e resistências internas associadas ao SOC e à temperatura (ex: LFP ou NMC).", bullet_style),
        Paragraph("<b>Associação Paralela:</b> Ajuste do número de contêineres BESS operando em paralelo. O sistema calcula automaticamente a capacidade total (kWh), potência de despacho máxima (kW) e as strings totais.", bullet_style),
        Paragraph("<b>Divisão de Corrente:</b> Divisão automática de corrente por string para cálculos de perdas de efeito Joule nas equações de temperatura das células.", bullet_style),
    ]
    
    col2_p2 = [
        Paragraph("Limites Operacionais & Proteções de Segurança", section_title_style),
        Paragraph(
            "Os limites definidos nesta tela atuam como 'guardrails' físicos durante o despacho "
            "e alimentam as equações físico-químicas de envelhecimento acelerado do motor.",
            body_style
        ),
        Paragraph("<b>• Guardrails de SOC:</b> Slider interativo (ex: 20% a 80%) para evitar operação em zonas de degradação acelerada ou perigo elétrico de sobretensão/subtensão.", bullet_style),
        Paragraph("<b>• Temperatura de Ciclo:</b> Ajusta a temperatura operacional média (°C) sob ciclo de recarga ativa, ditando o desgaste na regressão de Stroe.", bullet_style),
        Paragraph("<b>• Temperatura de Standby:</b> Ajusta a temperatura das células em estado idle (repouso) para alimentar a lei calendária de Arrhenius.", bullet_style),
    ]
    
    slide_table = Table([[col1_p2, col2_p2]], colWidths=[385, 385])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 6: PASSO 2 - HARDWARE DA BATERIA (VISUAL)
    # ==========================================
    add_full_image_slide("Passo 2: Hardware da Bateria & Limites - Interface Visual", "step2_battery.png")
    
    # ==========================================
    # SLIDE 7: PASSO 3 - EXECUÇÃO DA SIMULAÇÃO (CONTEÚDO)
    # ==========================================
    add_slide_header("Passo 3: Execução da Simulação Eletrotérmica - Especificação")
    
    col1_p3 = [
        Paragraph("Controle de Motor, Dados e Duração", section_title_style),
        Paragraph(
            "Nesta tela, configuram-se as diretivas de processamento e inicia-se "
            "o integrador numérico eletrotérmico do BESx.",
            body_style
        ),
        Paragraph("<b>Motor Computacional (Backend):</b> Seleção entre o solucionador Python vetorizado (rápido e compatível com a nuvem) ou o solver transiente acoplado do <i>PLECS</i> (para análise detalhada de inversores e transientes chaveados).", bullet_style),
        Paragraph("<b>Temporalidade:</b> Duração configurável em Meses (1 a 12) ou Anos (1 a 15) para fatiamento do perfil de carga.", bullet_style),
        Paragraph("<b>Modo End-of-Life (EOL):</b> Dispara o motor numérico sem limite de tempo, interrompendo a simulação exclusivamente quando a capacidade da bateria atingir 80% do SOH inicial.", bullet_style),
        Paragraph("<b>Mapeamento Automático:</b> Detecção e atalho verde indicando o último perfil EMS injetado na base de dados no Passo 1, prevenindo erros de carregamento manual.", bullet_style),
    ]
    
    col2_p3 = [
        Paragraph("Métricas e Feedback ao Vivo", section_title_style),
        Paragraph(
            "Durante o processamento do motor físico-químico, o painel é atualizado via callbacks leves "
            "para exibir o avanço físico do BESS e manter a estabilidade do Streamlit:",
            body_style
        ),
        Paragraph("<b>• Design de Vidro Neon (Glassmorphism):</b> Animação em formato de bateria cujo nível e cores neon (verde, laranja, vermelho) alteram-se com a perda de capacidade.", bullet_style),
        Paragraph("<b>• SOH ao Vivo (%):</b> Percentual de capacidade restante atualizado a cada ciclo.", bullet_style),
        Paragraph("<b>• Ciclos EFC:</b> Equivalentes de ciclos completos acumulados pela contagem Rainflow.", bullet_style),
        Paragraph("<b>• Velocidade & ETA:</b> Taxa de processamento físico (meses/s) e cronômetro estimado em segundos.", bullet_style),
        Paragraph("<b>• Barra de Progresso:</b> Exibe a varredura temporal (mês atual de simulação / total de meses).", bullet_style),
    ]
    
    slide_table = Table([[col1_p3, col2_p3]], colWidths=[385, 385])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 8: PASSO 3 - EXECUÇÃO DA SIMULAÇÃO (VISUAL)
    # ==========================================
    add_full_image_slide("Passo 3: Execução da Simulação Eletrotérmica - Interface Visual", "step3_simulation.png")
    
    # ==========================================
    # SLIDE 9: PASSO 4 - RESULTADOS (CONTEÚDO)
    # ==========================================
    add_slide_header("Passo 4: Resultados da Simulação - Especificação")
    
    col1_p4 = [
        Paragraph("Painel Consolidado de Saúde e RUL", section_title_style),
        Paragraph(
            "Após a simulação, a tela exibe um dashboard completo de degradometria "
            "e telemetria elétrica amostrada.",
            body_style
        ),
        Paragraph("<b>Seletor de Histórico:</b> Carregamento de qualquer simulação passada do diretório local, formatada dinamicamente com informações do motor, modelo e data/hora.", bullet_style),
        Paragraph("<b>Foco de Análise:</b> Filtro interativo para alternar entre as métricas consolidadas ('Resumo Geral') ou isolar dados específicos de qualquer mês (ex: Mês 5) para examinar estresses sazonais.", bullet_style),
        Paragraph("<b>Indicador Segmentado EV:</b> Desenha um ícone de bateria automotiva colorida indicando a saúde global e a degradação acumulada da simulação.", bullet_style),
        Paragraph("<b>Cálculo de Longevidade (RUL):</b> Integra de forma analítica a lei de potência e Arrhenius para estimar os anos de vida útil restantes da bateria sob as lógicas simuladas.", bullet_style),
        Paragraph("<b>Indicador de Severidade (Is):</b> Normaliza a agressividade do desgaste comparando o dano calculado com o ciclo de referência química de laboratório.", bullet_style),
    ]
    
    col2_p4 = [
        Paragraph("Abas de Visualização Eletrotérmica & Exportação", section_title_style),
        Paragraph(
            "A tela divide a apresentação dos dados e gráficos Plotly em 3 categorias estratégicas:",
            body_style
        ),
        Paragraph("<b>1. Visão Geral:</b> Exibe a curva de decaimento mensal do SOH (%) até o teto de 80%, a curva horária de SOC para o mês selecionado e barras empilhadas de dano acumulado.", bullet_style),
        Paragraph("<b>2. Aba Degradação (Científica):</b> DOD médio operacional. Histograma de microciclos de DOD extraídos pelo Rainflow e gráfico de dispersão bidimensional (DOD vs SOC médio da Matriz de Fadiga).", bullet_style),
        Paragraph("<b>3. Aba Operacional (Física):</b> Gráfico elétrico de alta frequência de 4 eixos (Tensão Terminal, Corrente, Potência ativa e SOC horários), permitindo depurar o comportamento elétrico instante a instante.", bullet_style),
        Paragraph("<b>Ação de Exportação (Excel):</b> Botão para gerar um relatório analítico consolidado em formato Excel (.xlsx) contendo todos os dados tabulados da simulação física.", bullet_style),
    ]
    
    slide_table = Table([[col1_p4, col2_p4]], colWidths=[385, 385])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 10: PASSO 4 - RESULTADOS (VISUAL)
    # ==========================================
    add_full_image_slide("Passo 4: Resultados da Simulação - Interface Visual", "step4_results.png")
    
    # ==========================================
    # SLIDE 11: PASSO 5 - COMPARATIVO A/B (CONTEÚDO)
    # ==========================================
    add_slide_header("Passo 5: Comparativo A/B de Cenários - Especificação")
    
    col1_p5 = [
        Paragraph("Confronto Gráfico e de Parâmetros Físicos", section_title_style),
        Paragraph(
            "O dimensionamento correto exige testar diferentes lógicas e baterias. "
            "Este passo executa um comparativo multicritério sobre o histórico do simulador.",
            body_style
        ),
        Paragraph("<b>Multisseleção de Cenários:</b> Sobreposição em tempo real de múltiplas curvas de SOH (%), balanço de energia de carga/descarga (kWh), eficiência round-trip (RTE) e distribuição de ciclos Rainflow.", bullet_style),
        Paragraph("<b>Tabela Analítica de Confronto (Diff Table):</b> Matriz unificada de todas as variáveis de input e output físico-químicas, destacando em cor dourada/escura as linhas onde há divergência entre os cenários.", bullet_style),
    ]
    
    col2_p5 = [
        Paragraph("Diagnóstico de Engenharia por IA (Gemini)", section_title_style),
        Paragraph(
            "A interface integra uma chamada inteligente ao modelo de linguagem Gemini por meio do SDK oficial do Google GenAI. "
            "A IA processa os dados estruturados de confronto físico-químico e gera na tela um relatório especializado contemplando:",
            body_style
        ),
        Paragraph("<b>• Parecer Comparativo Técnico:</b> Qual bateria e lógica sofreram menor estresse térmico Arrhenius e mecânico, fundamentando os fatores limitantes físicos.", bullet_style),
        Paragraph("<b>• Análise de RTE & Eficiência:</b> Desempenho termodinâmico dos conversores.", bullet_style),
        Paragraph("<b>• Recomendação de Investimento:</b> Indicação consultiva baseada na saúde de longo prazo.", bullet_style),
    ]
    
    slide_table = Table([[col1_p5, col2_p5]], colWidths=[385, 385])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 12: PASSO 5 - COMPARATIVO A/B (VISUAL)
    # ==========================================
    add_full_image_slide("Passo 5: Comparativo A/B de Cenários - Interface Visual", "step5_comparison.png")
    
    # ==========================================
    # SLIDE 13: PASSO 6 - CONFIGURAÇÕES (CONTEÚDO)
    # ==========================================
    add_slide_header("Passo 6: Parâmetros de Engenharia & Validação - Especificação")
    
    col1_p6 = [
        Paragraph("Calibração Científica e Suite de Testes Físicos", section_title_style),
        Paragraph(
            "Voltada para engenheiros seniores e pesquisadores, esta tela calibra as lógicas matemáticas "
            "e valida a fidelidade transiente do core do simulador.",
            body_style
        ),
        Paragraph("<b>Calibração Científica:</b> Ajuste dos coeficientes empíricos cíclicos ($a, b, c, d$ da regressão de Stroe) e parâmetros de Arrhenius calendários (peso $k_T$, peso $k_{soc}$ e expoente temporal $t^n$). Coeficientes aplicados globalmente.", bullet_style),
        Paragraph("<b>Suite de Testes Físicos (Auditoria CI):</b> Execução automatizada de dados sintéticos para auditar os pilares de física do projeto:", bullet_style),
        Paragraph("<b>• TC1: Coulomb Swing:</b> Verifica se a conservação de energia e balanço de carga se mantém íntegros no integrador elétrico sob ciclo de 1C.", bullet_style),
        Paragraph("<b>• TC2: Partial Cycling:</b> Provoca microciclos de DOD rápido para testar a extração correta na pilha incremental de Rainflow.", bullet_style),
        Paragraph("<b>• TC3: Stroe Non-Linear:</b> Valida se a acumulação de dano segue o princípio não-linear geométrico sob lógicas dinâmicas de 12 meses.", bullet_style),
    ]
    
    col2_p6 = [
        Paragraph("Validação Transiente Cruzada (PLECS vs Python)", section_title_style),
        Paragraph(
            "Para garantir a máxima confiabilidade científica, o BESx compara ponto-a-ponto os resultados das curvas "
            "simplificadas contra o solver transiente de alta fidelidade do PLECS:",
            body_style
        ),
        Paragraph("<b>• Erros Médios Absolutos (MAE):</b> Exibição em tempo real do Erro Médio de SOC (%), Erro Médio de Tensão Terminal (V) e Erro Médio de Corrente (A) entre os motores.", bullet_style),
        Paragraph("<b>• Gráficos Elétricos Sobrepostos:</b> Plota três gráficos síncronos contendo as curvas de Tensão, Corrente e SOC ao longo do ensaio temporal para ambos os motores, comprovando a exatidão física.", bullet_style),
        Paragraph("<b>• Reprodutibilidade:</b> Botão dedicado a 'Atualizar Perfis de Teste' que regenera e recalibra bases sintéticas de dados para suite CI de física.", bullet_style),
    ]
    
    slide_table = Table([[col1_p6, col2_p6]], colWidths=[385, 385])
    slide_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(slide_table)
    story.append(PageBreak())
    
    # ==========================================
    # SLIDE 14: PASSO 6 - CONFIGURAÇÕES (VISUAL)
    # ==========================================
    add_full_image_slide("Passo 6: Parâmetros de Engenharia & Validação - Interface Visual", "step6_settings.png")
    
    # --- CONSTRUÇÃO DO DOCUMENTO ---
    try:
        doc.build(story, canvasmaker=PresentationCanvas)
        print(f"Sucesso: PDF gerado com sucesso em '{output_filename}'")
    except PermissionError:
        # Se o arquivo estiver aberto e bloqueado no Windows, tenta gerar um nome alternativo
        base_name, ext = os.path.splitext(output_filename)
        for i in range(1, 20):
            alt_filename = f"{base_name}_{i}{ext}"
            try:
                doc.filename = alt_filename
                doc.build(story, canvasmaker=PresentationCanvas)
                print(f"Sucesso: PDF gerado com sucesso em '{alt_filename}' (o arquivo original '{output_filename}' estava aberto/bloqueado)")
                break
            except PermissionError:
                continue
        else:
            raise PermissionError(f"Erro: Não foi possível salvar o PDF pois todos os nomes alternativos de '{output_filename}' estão bloqueados/abertos.")

if __name__ == "__main__":
    create_presentation_pdf()
