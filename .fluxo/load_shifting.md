# Estratégia: Load Shifting (Arbitragem de Tempo)

Foca em carregar a bateria em horários baratos (fora de ponta) e descarregar em horários caros (ponta).

```mermaid
flowchart TD
    LS_In[Janelas de Tempo: Carga vs Descarga] --> LS_Time{Hora Atual em?}
    
    LS_Time -->|Janela de Carga| LS_Check{Há folga na<br/>demanda?}
    LS_Check -->|Sim| LS_Cha[Carga:<br/>P_bat = Limite - Carga_W]
    LS_Check -->|Não| LS_Idle[P_bat = 0]
    
    LS_Time -->|Janela de Descarga| LS_Dis[Descarga Total:<br/>P_bat = -Carga_W]
    
    LS_Time -->|Outros Horários| LS_Idle
    
    LS_Cha --> LS_Out[Setpoint Gerado]
    LS_Dis --> LS_Out
    LS_Idle --> LS_Out
```

### Regras de Cálculo:
1. **Janela de Carga:** $P_{bat} = \max(0, Limite - P_{load})$
2. **Janela de Descarga:** $P_{bat} = -P_{load}$ (Cobre toda a carga se possível)
3. **Fora das Janelas:** $P_{bat} = 0$
