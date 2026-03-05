import json
from google import genai
from besx.config import CONFIGURACAO
from besx.infrastructure.logging.logger import logger

def analisar_comparacao_bess(dados_simulacoes: list[dict], api_key: str = None) -> str:
    """
    Envia os dados de comparação das simulações para a API do Gemini e
    retorna um relatório analítico em formato Markdown.
    
    Args:
        dados_simulacoes: Lista de dicionários contendo os KPIs e configurações 
                          relevantes de cada simulação para comparação.
        api_key: Chave opcional da API do Gemini. Se None, usará do CONFIGURACAO.
        
    Returns:
        String com a análise formatada em Markdown, ou mensagem de erro.
    """
    key = api_key or CONFIGURACAO.llm.gemini_api_key
    
    if not key or key == "sua_chave_api_aqui":
        return "⚠️ **Erro:** A chave da API do Gemini não foi configurada corretamente. Adicione em `config.py` ou na variável de ambiente `GEMINI_API_KEY`."
    
    try:
        client = genai.Client(api_key=key)
        
        # Preparando os dados em JSON formatado para facilitar a leitura da IA
        dados_json = json.dumps(dados_simulacoes, indent=2, ensure_ascii=False)
        
        prompt = f"""# Persona e Contexto

Você é um Engenheiro de Confiabilidade de Baterias (BESS) e Especialista em Ciência de Dados.
Sua tarefa é analisar os resultados de simulações de degradação de baterias de íon-lítio gerados por um motor matemático baseado no Modelo Empírico de Stroe e no algoritmo de Rainflow Cycle Counting.

Você receberá um payload de dados contendo duas ou mais simulações (ex: Cenário A e Cenário B), incluindo métricas como SOH (State of Health), RUL (Remaining Useful Life), EFC (Equivalent Full Cycles), Throughput de Energia, Fator de Severidade Global (σ) e faixas de temperatura.

# Objetivos da Análise

Trabalhe neste problema passo a passo. Faça uma análise técnica, neutra e baseada estritamente nos dados fornecidos, dividida nas três seções a seguir:

## 1. Análise Comparativa Direta

- Compare as simulações fornecidas.
- Identifique qual cenário resulta em uma vida útil (RUL) maior e justifique com base no balanço entre a degradação cíclica (uso) e calendárica (repouso).
- Avalie o volume de energia processada (Throughput) versus o desgaste sofrido (SOH).

## 2. "Reality Check" (Estimativa de Proximidade com o Real)

Modelos empíricos possuem limitações no mundo real. Avalie a confiabilidade destas simulações e a proximidade com o desgaste real utilizando as seguintes regras de domínio:
- **Análise do Fator de Severidade (σ):** Se o Fator de Severidade de um cenário for muito alto (ex: > 1.5) ou muito variável, alerte o usuário de que a simulação pode estar subestimando o dano real. Modelos empíricos perdem precisão quando operam fora das condições nominais de calibração de laboratório.
- **Estresse Térmico e Químico:** Se a temperatura máxima de operação ultrapassar 35°C ou ficar abaixo de 10°C, aponte que fenômenos físicos não capturados pelo modelo de Stroe (como *Lithium Plating* em baixas temperaturas ou crescimento acelerado e anômalo da camada SEI pelo calor) podem fazer com que a bateria real morra mais rápido do que a simulação prevê.
- **Perfil do Rainflow:** Se o EFC for alcançado através de ciclos muito profundos (alto DOD), alerte que o estresse mecânico real nas partículas do eletrodo pode gerar microfissuras que aceleram a perda de material ativo de forma não linear, aproximando a simulação de uma margem de erro maior.

## 3. Limitações e Recomendações (PIML)

- Não generalize os resultados além do que os números mostram. Indique explicitamente que esta é uma simulação matemática.
- Recomende que, para uma operação real em campo, este modelo deve atuar em conjunto com uma arquitetura de aprendizado de máquina guiado pela física (Physics-Informed Machine Learning - PIML), onde os dados de telemetria reais calibram os resíduos do modelo físico ao longo do tempo.

# Restrições de Saída

- Retorne a resposta formatada em Markdown, utilizando tabelas ou bullet points para facilitar a leitura no dashboard.
- Mantenha um tom técnico, objetivo e cauteloso. Não afirme que a simulação é uma previsão infalível.

# Dados de Entrada

Os dados estão no formato JSON:
{dados_json}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        return response.text

    except Exception as e:
        logger.error(f"Erro ao chamar API do Gemini: {e}")
        return f"❌ **Erro na comunicação com a Inteligência Artificial:**\n{str(e)}"
