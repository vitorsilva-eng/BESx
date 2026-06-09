import numpy as np

acum_ciclo_atual = 13.042374097288988
acum_cal_atual = 4.122831031568966
dano_ciclo_medio = 0.8414594071579499
dano_cal_medio = 0.051300427523862734
exp_cal = 1.25

def projetar_perda(meses_futuros):
    fut_ciclo = np.sqrt(acum_ciclo_atual**2 + meses_futuros * (dano_ciclo_medio**2))
    fut_cal = (acum_cal_atual**exp_cal + meses_futuros * (dano_cal_medio**exp_cal))**(1/exp_cal)
    return fut_ciclo + fut_cal

for m in [0, 12, 24, 36, 48, 60, 72, 73, 74, 84, 96, 120]:
    perda = projetar_perda(m)
    print(f"Meses futuros: {m:3d} | Perda Projetada: {perda:.4f}% | SOH Projetado: {100-perda:.4f}%")
