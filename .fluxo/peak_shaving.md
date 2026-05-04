# Estratégia: Peak Shaving (Corte de Pico)

Esta estratégia visa manter a demanda da rede dentro de um limite contratado, utilizando a bateria para "achatar" os picos.

```mermaid
flowchart TD
    PS_In[Dados: Carga_W, Limite_kW, Margem] --> PS_1[Cálculo do Limite Efetivo:<br/>L_eff = Limite_kW - Margem]
    PS_1 --> PS_2[Comparação Vetorizada:<br/>Delta = L_eff - Carga_W]
    
    PS_2 --> PS_Cond{Delta < 0?}
    PS_Cond -->|Sim: Pico Detectado| PS_Dis[Descarga:<br/>Bateria fornece o excesso]
    PS_Cond -->|Não: Folga| PS_Cha[Carga:<br/>Bateria carrega até o limite]
    
    PS_Dis --> PS_Out[Potencia_Bateria_W = Delta]
    PS_Cha --> PS_Out
```

### Regras de Cálculo:
1. **Definição do Alvo:** $L_{eff} = L_{limit} - Margem$
2. **Diferença:** $\Delta P = L_{eff} - P_{load}$
3. **Ação:**
   - Se $\Delta P < 0$: Descarga.
   - Se $\Delta P > 0$: Carga.
