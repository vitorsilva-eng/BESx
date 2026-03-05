---
description: Substitui dicionários de configuração por modelos de validação estrita do Pydantic.
---

# Refatorar para Pydantic

Analise os dicionários de configuração e resultados presentes no código atual.
Refatore-os para utilizar modelos de validação do Pydantic (BaseModel).
Aplique tipagem estrita para todos os parâmetros (ex: garantindo que capacidade seja float, quantidade de células seja int).
Garanta que a refatoração não quebre o restante da lógica de simulação do BESx e atualize as chamadas dos objetos.
