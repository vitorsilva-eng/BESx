# Estratégia: Power Factor Correction (Correção de FP)

Despacha potência reativa ($VAr$) para atingir um fator de potência alvo, respeitando o limite do inversor ($S_{max}$).

```mermaid
flowchart TD
    PFC_In[P_carga, Q_carga, FP_alvo, S_max] --> PFC_1[Calcular Ângulo Alvo:<br/>phi = arccos|FP_alvo|]
    PFC_1 --> PFC_2[Calcular Reativo Alvo:<br/>Q_alvo = P_carga * tan_phi]
    PFC_2 --> PFC_3[Diferença Necessária:<br/>Q_req = Q_alvo - Q_carga]
    PFC_3 --> PFC_Lim{Excede S_max?}
    PFC_Lim -->|Sim| PFC_Clip[Clip: Q_bat = S_max]
    PFC_Lim -->|Não| PFC_Set[Q_bat = Q_req]
```

### Regras de Cálculo:
1. **Target Angle:** $\phi = \arccos(|PF_{target}|)$
2. **Target Reactive:** $Q_{target} = P_{load} \cdot \tan(\phi)$
3. **Dispatch:** $Q_{bat} = \text{clip}(Q_{target} - Q_{load}, -S_{max}, S_{max})$
