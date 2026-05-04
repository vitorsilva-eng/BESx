---
phase: 7
plan: 1
wave: 1
depends_on: []
files_modified: ["src/besx/application/ems/ems_manager.py"]
autonomous: true

must_haves:
  truths:
    - "EMSManager aceita combinações de P, Q, S e FP."
    - "EMSManager infere todas as quatro variáveis elétricas e as padroniza em colunas explícitas (Carga_W, Carga_VAr, Carga_VA, Carga_FP)."
    - "A configuração de EMSManager agora aceita `s_inversor_va`."
  artifacts:
    - "src/besx/application/ems/ems_manager.py modificado"
---

# Plan 7.1: Validação e Inferência do Triângulo de Potências

<objective>
Expandir o validador de entrada do EMS para processar potência reativa, aparente e fator de potência, inferindo dados ausentes com base em combinações mínimas. Adicionar o limite de capacidade do inversor (S).

Purpose: Garantir que a estratégia de Correção de Fator de Potência tenha todas as métricas necessárias (Load_W, Load_VAr) para calcular o setpoint reativo, sem sobrecarregar o usuário com exigências de dados super-específicos.
Output: `validate_and_prepare_input` aprimorado e `EMSManager` pronto para gerenciar VArs.
</objective>

<context>
Load for context:
- .gsd/phases/7/RESEARCH.md
- src/besx/application/ems/ems_manager.py
</context>

<tasks>

<task type="auto">
  <name>Adicionar suporte a `s_inversor_va` no construtor</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    Modifique `EMSManager.__init__` para aceitar um argumento adicional opcional `s_inversor_va: float = None`.
    Salve-o em `self.s_inversor_va`. Se não fornecido, pode assumir `self.p_bess_max_w` (o que implica Fator de Potência do Inversor = 1.0 como fallback).
    AVOID: Quebrar inicializações existentes. Use `s_inversor_va=None` para compatibilidade.
  </action>
  <verify>grep "s_inversor_va" src/besx/application/ems/ems_manager.py</verify>
  <done>Construtor do EMSManager inicializa a propriedade s_inversor_va</done>
</task>

<task type="auto">
  <name>Implementar inferência do triângulo de potência</name>
  <files>src/besx/application/ems/ems_manager.py</files>
  <action>
    Atualize `validate_and_prepare_input`. Após garantir `Carga_W`, procure por `Carga_FP` (Fator de Potência), `Carga_VAr` (Reativa) ou `Carga_VA` (Aparente).
    Use Numpy (`import numpy as np`) para vetorizar as seguintes condições de inferência, preenchendo as colunas:
    - Se tem W e FP: VA = W / FP, VAr = W * np.tan(np.arccos(FP))
    - Se tem W e VAr: VA = np.sqrt(W**2 + VAr**2), FP = W / VA
    - Se tem W e VA: VAr = np.sqrt(np.clip(VA**2 - W**2, 0, None)), FP = W / VA
    - Se tem apenas W: assuma VAr=0, VA=W, FP=1.0 (Fallback seguro)
    AVOID: `pd.Series.apply` ou loops `for`. Utilize puramente equações Numpy/Pandas diretamente nas colunas para manter a performance O(1).
  </action>
  <verify>python -c "import src.besx.application.ems.ems_manager"</verify>
  <done>validate_and_prepare_input retorna um DataFrame contendo as 4 colunas padronizadas de potência independente do input mínimo fornecido.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Construtor do EMSManager não quebra contratos antigos.
- [ ] Inferência cobre Q e FP de forma vetorizada sem erros de divisão por zero.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
