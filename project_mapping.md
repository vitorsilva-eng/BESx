# BESx Project Mapping

| File Path / Tree | Function | Description | Usage |
| :--- | :--- | :--- | :--- |
| **get_oauth_token.py** | | | |
| └── main | `main()` | N/A | Internal, src\besx\application\ems\ems_manager.py, src\besx\entrypoints\cli\menu.py, tests\test_battery_simulator.py, tests\test_data_handler.py, tests\test_degradation_model.py |
| **src/besx/application/ems/ems_engine.py** | | | |
| └── __init__ | `__init__()` | Inicializa o gerador de perfis do EMS de forma agnóstica à bateria. | src\besx\application\ems\ems_manager.py, src\besx\application\simulation.py, src\besx\infrastructure\files\file_manager.py |
| └── gerar_perfil_load_shifting | `gerar_perfil_load_shifting()` | Aplica a estratégia de Load Shifting (Arbitragem de Tempo de Uso) de forma vetorizada. | src\besx\application\ems\ems_manager.py |
| └── gerar_perfil_peak_shaving | `gerar_perfil_peak_shaving()` | Aplica a estratégia de Peak Shaving (Corte de Pico) de forma vetorizada, | src\besx\application\ems\ems_manager.py |
| **src/besx/application/ems/ems_manager.py** | | | |
| └── execute | `execute()` | Executes the specific EMS strategy. | Internal |
| └── execute | `execute()` | N/A | Internal |
| └── execute | `execute()` | N/A | Internal |
| └── __init__ | `__init__()` | N/A | src\besx\application\ems\ems_engine.py, src\besx\application\simulation.py, src\besx\infrastructure\files\file_manager.py |
| └── validate_and_prepare_input | `validate_and_prepare_input()` | Validates the input DataFrame following strict rules (REQ-04 to REQ-08). | Internal |
| └── run | `run()` | Validates data, executes strategies sequentially, and calculates heuristic metrics. | src\besx\application\simulation.py, src\besx\entrypoints\cli\main.py, src\besx\infrastructure\ui\streamlit\pages\step_rules.py, src\besx\infrastructure\ui\streamlit\pages\step_simulation.py |
| └── get_status | `get_status()` | N/A | Internal |
| **src/besx/application/simulation.py** | | | |
| └── __init__ | `__init__()` | N/A | src\besx\application\ems\ems_engine.py, src\besx\application\ems\ems_manager.py, src\besx\infrastructure\files\file_manager.py |
| └── _carregar_checkpoint | `_carregar_checkpoint()` | Tenta carregar o estado anterior da simulação a partir de um arquivo checkpoint.json. | Internal |
| └── _salvar_checkpoint | `_salvar_checkpoint()` | Salva o estado atual da simulação em um arquivo checkpoint.json para permitir retomada. | Internal |
| └── run | `run()` | Inicia ou retoma a execução completa do pipeline de simulação. | src\besx\application\ems\ems_manager.py, src\besx\entrypoints\cli\main.py, src\besx\infrastructure\ui\streamlit\pages\step_rules.py, src\besx\infrastructure\ui\streamlit\pages\step_simulation.py |
| └── _processar_mes | `_processar_mes()` | Processa um mês individual de simulação: cálculos elétricos, degradação e agregação. | Internal |
| └── _finalizar_simulacao | `_finalizar_simulacao()` | Consolida os resultados, exporta relatórios e gera os gráficos finais da simulação. | Internal |
| **src/besx/domain/models/battery_simulator.py** | | | |
| └── _interpolar_ocv | `_interpolar_ocv()` | Interpola a tensão OCV do banco para um dado SOC (fração 0-1). | Internal |
| └── simular_soc_mes | `simular_soc_mes()` | Simula o perfil de SOC e Tensão de um mês usando integração de Coulomb e Modelo Rint. | src\besx\infrastructure\plecs\plecs_connector.py, tests\test_battery_simulator.py |
| └── old_simular_soc_mes | `old_simular_soc_mes()` | Simula o perfil de SOC de um mês usando integração de Coulomb. |  |
| └── picos_e_vales | `picos_e_vales()` | Extrai picos e vales de uma Série de SOC. | src\besx\application\simulation.py, src\besx\domain\models\degradation_model.py, tests\test_data_handler.py, tests\test_engine_validation.py |
| └── ciclos_idle | `ciclos_idle()` | Encontra períodos 'idle' (SOC constante) em um perfil de SOC. | src\besx\application\simulation.py, tests\test_data_handler.py |
| **src/besx/domain/models/degradation_model.py** | | | |
| └── acumular_dano | `acumular_dano()` | Acumula o dano de acordo com a exponencial. | tests\test_degradation_model.py |
| └── calcular_dano_referencia_serrao | `calcular_dano_referencia_serrao()` | Calcula o dano nominal de referência conforme Serrão et al. | Internal |
| └── calcular_fator_severidade | `calcular_fator_severidade()` | Calcula o Fator de Severidade (Is) comparando o dano real com o nominal. | src\besx\infrastructure\ui\streamlit\pages\step_comparison.py, src\besx\infrastructure\ui\streamlit\utils\render_utils.py |
| └── calcular_rul | `calcular_rul()` | Projeta o Remaining Useful Life (RUL) em anos. | src\besx\infrastructure\ui\streamlit\pages\step_comparison.py, src\besx\infrastructure\ui\streamlit\utils\render_utils.py |
| └── dano_ciclo | `dano_ciclo()` | Calcula o dano total de cada ciclo do mês e acumula de forma quadrática. | src\besx\application\simulation.py, tests\test_degradation_model.py, tests\test_engine_validation.py |
| └── dano_calendar | `dano_calendar()` | Calcula o dano total por calendário (%) para o mês. | src\besx\application\simulation.py, tests\test_degradation_model.py, tests\test_engine_validation.py |
| └── calcular_estatisticas_operacionais | `calcular_estatisticas_operacionais()` | Analisa o comportamento do mês: Ciclos (Rainflow), C-Rates e Energia Utilizada. | src\besx\application\simulation.py, tests\test_degradation_model.py |
| **src/besx/entrypoints/cli/main.py** | | | |
| └── parse_args | `parse_args()` | Configura e analisa os argumentos de linha de comando. | Internal |
| **src/besx/entrypoints/cli/menu.py** | | | |
| └── exibir_menu_inicial | `exibir_menu_inicial()` | Exibe o menu interativo em loop até o usuário confirmar. | src\besx\entrypoints\cli\main.py |
| └── _imprimir_cabecalho | `_imprimir_cabecalho()` | Imprime o cabeçalho do menu interativo no console. | Internal |
| └── _selecionar_perfil_bateria | `_selecionar_perfil_bateria()` | Pergunta qual perfil de bateria usar e retorna a chave escolhida. | Internal |
| └── _selecionar_backend | `_selecionar_backend()` | Pergunta qual backend de simulação usar e retorna a constante. | Internal |
| └── _confirmar_selecao | `_confirmar_selecao()` | Exibe o resumo e pede confirmação. Retorna True se confirmado. | Internal |
| **src/besx/entrypoints/dashboard/streamlit_app.py** | | | |
| └── change_step | `change_step()` | N/A | Internal |
| **src/besx/infrastructure/files/file_manager.py** | | | |
| └── __init__ | `__init__()` | Gerencia a estrutura de pastas e arquivos da simulação. | src\besx\application\ems\ems_engine.py, src\besx\application\ems\ems_manager.py, src\besx\application\simulation.py |
| └── _create_structure | `_create_structure()` | Cria as pastas necessárias. | Internal |
| └── get_debug_path | `get_debug_path()` | Retorna o caminho completo para um arquivo de debug. | src\besx\application\simulation.py |
| └── get_plot_path | `get_plot_path()` | Retorna o caminho completo para um arquivo de plot. | src\besx\application\simulation.py |
| └── get_data_path | `get_data_path()` | Retorna o caminho completo para um arquivo de dados (ex: .mat intermediário). | src\besx\application\simulation.py, src\besx\infrastructure\reports\validation_report.py |
| └── save_report | `save_report()` | Salva o relatório final da simulação. | src\besx\infrastructure\reports\report.py |
| **src/besx/infrastructure/llm/gemini_analyzer.py** | | | |
| └── analisar_comparacao_bess | `analisar_comparacao_bess()` | Envia os dados de comparação das simulações para a API do Gemini e | src\besx\infrastructure\ui\streamlit\pages\step_comparison.py |
| **src/besx/infrastructure/loaders/conversor.py** | | | |
| └── expandir_curva_carga | `expandir_curva_carga()` | Lê uma curva de carga, detecta a resolução e expande para N anos. |  |
| └── converter_csv_para_pkl | `converter_csv_para_pkl()` | Converte um arquivo CSV específico para o formato Pickle (.pkl) otimizado. | src\besx\infrastructure\loaders\data_handler.py |
| **src/besx/infrastructure/loaders/data_handler.py** | | | |
| └── data_handle | `data_handle()` | Função principal do módulo: orquestra o carregamento e fatiamento dos dados. | src\besx\application\simulation.py |
| └── selecionar_arquivo_database | `selecionar_arquivo_database()` | Exibe os dados na pasta do banco de dados e solicita ao usuário que selecione um. | Internal |
| └── identificar_tipo_arquivo | `identificar_tipo_arquivo()` | Analisa a extensão, converte se necessário e RETORNA o nome do arquivo .mat final. | Internal |
| └── carregar_dados_mat | `carregar_dados_mat()` | (Função interna) Carrega um arquivo (.mat ou .pkl) e o converte para um DataFrame. | Internal |
| └── analisar_integridade_dados | `analisar_integridade_dados()` | Analisa os dados assumindo que a primeira coluna é Tempo (em minutos) | Internal |
| └── ajustar_duracao_dados | `ajustar_duracao_dados()` | Expande ou corta os dados. | Internal |
| └── fatiar_dados_mensais | `fatiar_dados_mensais()` | Divide o DataFrame em uma lista de DataFrames mensais. | Internal, tests\test_data_handler.py |
| **src/besx/infrastructure/logging/logger.py** | | | |
| └── setup_logger | `setup_logger()` | Configura o logger principal com saída colorida no console. | Internal |
| **src/besx/infrastructure/plecs/plecs_connector.py** | | | |
| └── run_monthly_simulation | `run_monthly_simulation()` | Simula um mês de operação da bateria e retorna o perfil de SOC. | Internal, src\besx\application\simulation.py, tests\test_engine_validation.py |
| └── extrair_soc_final | `extrair_soc_final()` | Extrai o SOC final da simulação mensal como fração 0–1. | src\besx\application\simulation.py |
| └── close_plecs_server | `close_plecs_server()` | Tenta fechar o servidor PLECS (no-op se backend Python estiver em uso). | Internal, src\besx\application\simulation.py |
| └── _run_python | `_run_python()` | Delega ao simulador Python de integração de Coulomb. | Internal |
| └── _run_plecs | `_run_plecs()` | Executa a simulação via XML-RPC no PLECS. | Internal |
| └── _to_native_types | `_to_native_types()` | Converte tipos NumPy para tipos Python nativos (compatibilidade XMLRPC). | Internal |
| └── _montar_model_vars_bateria | `_montar_model_vars_bateria()` | Constrói o dicionário ModelVars para o PLECS. | Internal |
| **src/besx/infrastructure/reports/report.py** | | | |
| └── gerar_relatorio_txt | `gerar_relatorio_txt()` | Gera um relatório de texto detalhado com metadados, configuração  | src\besx\application\simulation.py |
| **src/besx/infrastructure/reports/validation_report.py** | | | |
| └── gerar_relatorio_validacao | `gerar_relatorio_validacao()` | Gera um relatório completo de validação em Excel com múltiplas sheets. | src\besx\application\simulation.py |
| └── criar_sheet_configuracao | `criar_sheet_configuracao()` | Cria a sheet com todos os parâmetros de configuração. | Internal |
| └── criar_sheet_resumo_mensal | `criar_sheet_resumo_mensal()` | Cria a sheet com resumo mensal (similar ao resultados_completos.xlsx). | Internal |
| └── criar_sheets_calculos_detalhados | `criar_sheets_calculos_detalhados()` | Cria sheets detalhadas para cada mês (Ciclo e Calendário). | Internal |
| └── formatar_workbook | `formatar_workbook()` | Aplica formatação profissional ao workbook: | Internal |
| └── exportar_debug_degradacao | `exportar_debug_degradacao()` | Exporta dados intermediários do modelo de degradação para validação externa (Excel). | src\besx\application\simulation.py |
| └── export_xlsx | `export_xlsx()` | Exporta uma lista de DataFrames para um arquivo Excel com múltiplas abas. | src\besx\application\simulation.py, tests\test_engine_validation.py |
| **src/besx/infrastructure/ui/streamlit/pages/step_battery.py** | | | |
| └── render_step_battery | `render_step_battery()` | Passo 2: Configuração Física da Bateria e Limites Operacionais. | src\besx\entrypoints\dashboard\streamlit_app.py |
| **src/besx/infrastructure/ui/streamlit/pages/step_comparison.py** | | | |
| └── render_step_comparison | `render_step_comparison()` | Passo 5: Comparativo A/B de Simulações. | src\besx\entrypoints\dashboard\streamlit_app.py |
| └── render_diff_table | `render_diff_table()` | N/A | Internal |
| └── style_diff | `style_diff()` | N/A | Internal |
| **src/besx/infrastructure/ui/streamlit/pages/step_results.py** | | | |
| └── render_step_results | `render_step_results()` | Passo 4: Visualização de Resultados e Histórico. | src\besx\entrypoints\dashboard\streamlit_app.py |
| └── render_dashboard | `render_dashboard()` | Renderiza o dashboard completo para um DataFrame de resultados. | Internal |
| **src/besx/infrastructure/ui/streamlit/pages/step_rules.py** | | | |
| └── render_step_rules | `render_step_rules()` | Passo 1: Definição das Regras do Local e Estratégia EMS. | src\besx\entrypoints\dashboard\streamlit_app.py |
| └── save_ems_profile | `save_ems_profile()` | N/A | Internal |
| **src/besx/infrastructure/ui/streamlit/pages/step_settings.py** | | | |
| └── render_step_settings | `render_step_settings()` | Passo 6: Parâmetros de Engenharia e Validação de Motores. | src\besx\entrypoints\dashboard\streamlit_app.py |
| **src/besx/infrastructure/ui/streamlit/pages/step_simulation.py** | | | |
| └── render_step_simulation | `render_step_simulation()` | Passo 3: Configuração do Motor e Execução da Simulação. | src\besx\entrypoints\dashboard\streamlit_app.py |
| └── live_callback | `live_callback()` | N/A | Internal |
| **src/besx/infrastructure/ui/streamlit/utils/render_utils.py** | | | |
| └── get_status_color | `get_status_color()` | Retorna a cor neon baseada no valor (SOH ou similar). | Internal |
| └── render_glass_battery | `render_glass_battery()` | Renderiza uma bateria estilo Glassmorphism (Vidro/Neon). | src\besx\infrastructure\ui\streamlit\pages\step_simulation.py |
| └── render_ev_battery | `render_ev_battery()` | Renderiza uma bateria estilo EV Dashboard (Segmentada). | Internal |
| └── format_sim_name | `format_sim_name()` | Formata o nome da simulação para exibição. | src\besx\infrastructure\ui\streamlit\pages\step_comparison.py, src\besx\infrastructure\ui\streamlit\pages\step_results.py |
| └── render_metrics_row | `render_metrics_row()` | N/A | src\besx\infrastructure\ui\streamlit\pages\step_results.py |
| └── render_view_overview | `render_view_overview()` | N/A | src\besx\infrastructure\ui\streamlit\pages\step_results.py |
| └── render_view_degradation | `render_view_degradation()` | N/A | src\besx\infrastructure\ui\streamlit\pages\step_results.py |
| └── render_view_operational | `render_view_operational()` | N/A | src\besx\infrastructure\ui\streamlit\pages\step_results.py |
| **src/besx/infrastructure/visualization/plotly_plots.py** | | | |
| └── plot_ems_dispatch_comparison | `plot_ems_dispatch_comparison()` | Plots a comparison between Original Load, Adjusted Load, and Battery Power. | src\besx\infrastructure\ui\streamlit\pages\step_rules.py |
| └── plot_energy_balance | `plot_energy_balance()` | Plots the accumulated energy balance (kWh). | src\besx\infrastructure\ui\streamlit\pages\step_rules.py |
| **src/besx/infrastructure/visualization/plots.py** | | | |
| └── imprimir_histograma | `imprimir_histograma()` | Imprime um histograma de contagem de ciclos agrupados por DOD (Range) |  |
| └── plotar_capacidade_mensal | `plotar_capacidade_mensal()` | Gera um gráfico da capacidade restante da bateria ao final de cada mês. | src\besx\application\simulation.py |
| └── plotar_composicao_degradacao | `plotar_composicao_degradacao()` | Gera um gráfico de área empilhada mostrando a contribuição | src\besx\application\simulation.py |
| **tests/mission_profile_generator.py** | | | |
| └── generate_profiles | `generate_profiles()` | N/A | Internal |
| └── add_segment | `add_segment()` | N/A | Internal |
| **tests/test_battery_simulator.py** | | | |
| └── _df_mes_constante | `_df_mes_constante()` | Cria um DataFrame de potência constante em Watts. | Internal |
| └── test_saida_tem_colunas_corretas | `test_saida_tem_colunas_corretas()` | A saída deve tel exatamente as colunas 'Tempo' e 'SOC'. |  |
| └── test_saida_tem_mesmo_numero_de_linhas | `test_saida_tem_mesmo_numero_de_linhas()` | O número de linhas da saída deve ser igual ao da entrada. |  |
| └── test_tempo_em_segundos | `test_tempo_em_segundos()` | Coluna Tempo deve estar em segundos (primeiro valor = 0 s). |  |
| └── test_soc_em_percentual | `test_soc_em_percentual()` | SOC deve estar em % (0–100), não em fração (0–1). |  |
| └── test_soc_inicial_correto | `test_soc_inicial_correto()` | O primeiro valor de SOC deve corresponder ao soc_inicial fornecido. |  |
| └── test_potencia_zero_soc_constante | `test_potencia_zero_soc_constante()` | Com potência zero, o SOC deve permanecer constante ao longo do tempo. |  |
| └── test_carga_aumenta_soc | `test_carga_aumenta_soc()` | Potência positiva (carga) deve aumentar o SOC. |  |
| └── test_descarga_diminui_soc | `test_descarga_diminui_soc()` | Potência negativa (descarga) deve diminuir o SOC. |  |
| └── test_soc_nao_ultrapassa_socmax | `test_soc_nao_ultrapassa_socmax()` | SOC nunca deve ultrapassar soc_max (90%). |  |
| └── test_soc_nao_cai_abaixo_socmin | `test_soc_nao_cai_abaixo_socmin()` | SOC nunca deve cair abaixo de soc_min (10%). |  |
| └── test_potencia_limitada_por_p_bess | `test_potencia_limitada_por_p_bess()` | Potência muito alta deve ser clipada ao valor de P_bess. |  |
| └── test_soh_reduzido_aumenta_variacao_soc | `test_soh_reduzido_aumenta_variacao_soc()` | Com SOH reduzido a capacidade efetiva diminui, |  |
| └── test_conservacao_energetica_carga_simples | `test_conservacao_energetica_carga_simples()` | Verifica que a variação de SOC é próxima ao valor calculado analiticamente. |  |
| **tests/test_data_handler.py** | | | |
| └── setUp | `setUp()` | N/A | tests\test_degradation_model.py |
| └── tearDown | `tearDown()` | N/A |  |
| └── test_ciclos_idle_basic | `test_ciclos_idle_basic()` | Test basic idle detection with constant blocks. |  |
| └── test_ciclos_idle_no_idle | `test_ciclos_idle_no_idle()` | Test profile with no idle periods (changing every step). |  |
| └── test_ciclos_idle_full_idle | `test_ciclos_idle_full_idle()` | Test profile that is entirely idle. |  |
| └── test_ciclos_idle_float_precision | `test_ciclos_idle_float_precision()` | Test idle detection with floating point numbers. |  |
| └── test_picos_e_vales | `test_picos_e_vales()` | Test peak and valley detection. |  |
| └── test_fatiar_dados_mensais | `test_fatiar_dados_mensais()` | Test slicing dataframe into monthly chunks. |  |
| **tests/test_degradation_model.py** | | | |
| └── setUp | `setUp()` | N/A | tests\test_data_handler.py |
| └── test_dano_ciclo | `test_dano_ciclo()` | Test cycle damage calculation. |  |
| └── test_dano_calendar | `test_dano_calendar()` | Test calendar damage calculation. |  |
| └── test_acumular_dano | `test_acumular_dano()` | Test damage accumulation. |  |
| **tests/test_engine_validation.py** | | | |
| └── rodar_validacao | `rodar_validacao()` | N/A | Internal, src\besx\infrastructure\ui\streamlit\pages\step_settings.py |
