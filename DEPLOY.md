# Guia de Deploy - BESx (Streamlit Community Cloud)

Este guia orienta como colocar o simulador BESx online utilizando a Opção A (Streamlit Community Cloud).

## Passo 1: Preparar o Repositório no GitHub
1. Crie um repositório novo no seu GitHub (pode ser privado).
2. Suba todos os arquivos desta pasta para o repositório.
   - Certifique-se de que a pasta `src` e o arquivo `requirements.txt` estão na raiz do repositório.
   - O arquivo `.streamlit/config.toml` também deve ser enviado.

## Passo 2: Conectar ao Streamlit Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io).
2. Conecte sua conta do GitHub.
3. Clique em **"New app"**.
4. Selecione o repositório do BESx.
5. Em **"Main file path"**, coloque:
   `src/besx/entrypoints/dashboard/streamlit_app.py`
6. Clique em **"Deploy!"**.

## Passo 3: Configurar o PYTHONPATH (Importante!)
Se o Streamlit reclamar que não encontra o módulo `besx`, você precisará adicionar uma variável de ambiente no painel do Streamlit Cloud:
1. Vá em **Settings** -> **Secrets**.
2. Adicione:
   ```toml
   PYTHONPATH = "src"
   ```

## Passo 4: Secrets (Opcional)
Se você utiliza chaves de API, coloque-as também na seção **Secrets** do painel do Streamlit Cloud para que fiquem protegidas.

---

## Adendo: Atualizando um Repositório GitHub Existente

Como você já tem o projeto no GitHub, mas o código mudou bastante e não há um "remote" configurado localmente no momento, siga estes passos no seu terminal (CMD/PowerShell) dentro da pasta do BESx para atualizar seu código na web:

1. **Vincule a pasta local ao seu repositório online:**
   Substitua `URL_DO_SEU_REPO` pelo link do seu repositório (ex: `https://github.com/seu-usuario/besx.git`)
   ```bash
    git remote add origin https://github.com/vitorsilva-eng/BESx.git
   ```

2. **Adicione as novidades e crie um "pacote" (commit):**
   *(Este comando vai rastrear todos os arquivos novos e modificados, como o requirements.txt e o config.toml)*
   ```bash
   git add .
   git commit -m "feat: atualizando arquitetura e preparando para deploy"
   ```

3. **Envie (Push) para a nuvem:**
   Se o seu branch principal for `main`:
   ```bash
   git push -u origin main
   ```
   *(Nota: Caso o histórico esteja conflitando muito e você tiver certeza de que a versão local é a correta, você pode forçar o envio com `git push -u origin main --force`. Cuidado, isso sobrescreve o que está online).*

*Desenvolvido pela Equipe BESx*
