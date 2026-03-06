# TO DO

## TO DO CODE

    [X] Verificar o nível de corrente que passa nas células
    [X] Comparar a simulação no plecs com a simulação em python
    [ ] Implementar a bateria de Rodrigo para fazer um Benchmarking
    [ ] Implementar uma Curva OCVxSOC para carga e outra para descarga
    [ ] Atualizar para receber os dados da curva de carga e decidir se carrega ou descarrega
    [ ] Modelo térmico da temperatura:
        - [X] Setar uma temperatura diferentes para o dano de ciclo ou de calendário
        - [ ] Usar um modelo de temperatura do Daniel
        - [ ] Usar um modelo artigo de rodrigo
        - [ ] Tentar obter uma curva com os dados do local?
    [] Testar pediar a IA para gerar o python do arquivo plecs
    [ ] Implementar o cálculo do RUL (Remaining Useful Life / Vida Útil Remanescente)
    [ ] Implementar um ganho de resistência para a bateria?

## TO_DO_DASH

    [X] Mostrar Histograma de DOD (espectro de uso gerado pelo algoritmo Rainflow) 
    [X] Mostrar SOC Médio em Repouso.
    [X] Mostrar RUL (Remaining Useful Life / Vida Útil Remanescente)
    [X] Tratar erro na exibição do Soc medio repouso
    [X] Adaptar o visual para funcionar bem no modo light
    [X] Implementar o Fator de Severidade conforme _ref\serrao.pdf estabelecendo T_ref = 25°C, SOC_ref = 50%, DOD_ref = 10%
    [ ] Revisar os itens na comparação do plecs com o python
    [ ] Revisar dados operacionais do histórico
    [ ] Adicionar número de ciclos no dash de comparação
    

## Sugestões de Melhoria (Code Cleanliness & Efficiency)

    [x] Adicionar Type Hints (anotações de tipo) em todas as funções.
    [x] Implementar Docstrings (padrão Google/NumPy) para documentação.
    [x] Usar `dataclasses`, `Pydantic` ou `NamedTuple` para estruturar resultados (ao invés de dicts soltos).
    [x] Implementar Checkpointing: Salvar estado intermediário para retomar simulação em caso de falha.
    [x] Modularizar: Separar CLI (interface) da lógica de simulação (Core).
    [x] Tratar while ture e inputs (argparse)
