# Integração de Energia (Balanço de SOC)

Após todas as estratégias, o EMS calcula como isso afetou o nível de energia da bateria.

```mermaid
flowchart TD
    Int_1[P_bat_W em t] --> Int_2[Intervalo de Tempo: dt_h]
    Int_2 --> Int_3[Energia do Intervalo:<br/>dE = P_bat_W * dt_h / 1000]
    Int_3 --> Int_4[Acumulação:<br/>E_total_t = E_total_t-1 + dE]
```

### Notas:
- **Carga Ajustada:** $P_{adj} = P_{load} + P_{bat}$
- **Balanço:** Energia Acumulada reflete a integração da potência ao longo do tempo.
