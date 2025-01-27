SISTEMA DE GESTÃO DE REQUERIMENTOS
==================================

Este é um sistema de gerenciamento de solicitações desenvolvido para o Instituto de Geociências da UNICAMP. Ele permite a administração centralizada das solicitações de auxílio financeiro de pós-graduandos, oferecendo recursos como:

- Visualização e gerenciamento de solicitações.
- Envio automatizado de e-mails.
- Estatísticas e gráficos para análise de dados financeiros.
- Configurações avançadas para gestão de usuários e notificações.
- Diferentes níveis de acesso baseados em cargos.

FUNCIONALIDADES PRINCIPAIS
--------------------------

1. LOGIN SEGURO
   - Autenticação por nome de usuário e senha.
   - Diferentes níveis de acesso (visualização, gerenciamento, administração).

2. GERENCIAMENTO DE SOLICITAÇÕES
   - Listagem, filtragem e pesquisa de solicitações.
   - Detalhamento de informações por abas (dados pessoais, acadêmicos e financeiros).
   - Atualização de status com registro histórico.

3. ENVIO DE E-MAILS AUTOMATIZADO
   - Notificações configuráveis para mudanças de status, solicitações de documentos e aprovações.

4. ANÁLISE E RELATÓRIOS
   - Estatísticas detalhadas com gráficos de barras, linhas e pizza.
   - Filtros customizáveis para visualizações específicas.

PASSO A PASSO PARA INSTALAÇÃO
-----------------------------

1. PRÉ-REQUISITOS:
   Certifique-se de que os seguintes itens estão instalados no seu sistema:
   - Python 3.8 ou superior.
   - Gerenciador de pacotes `pip`.
   - Conta de e-mail compatível com SMTP (ex.: Gmail).

2. CLONE O REPOSITÓRIO:
   Execute o seguinte comando no terminal:

git clone https://github.com/Akio60/Financas-IG-2 cd gestao-requerimentos

3. INSTALE AS DEPENDÊNCIAS:
Instale os pacotes necessários executando:

pip install -r requirements.txt

4. CONFIGURE AS CREDENCIAIS:
- Crie um arquivo `credentials.json` com as credenciais do Google Sheets.
- Defina a variável de ambiente para autenticação de e-mail:
  ```
  export EMAIL_PASSWORD="sua-senha-de-aplicativo"
  ```

5. CONFIGURAÇÃO INICIAL:
Certifique-se de configurar os arquivos auxiliares:
- `users_db.json`: Base de dados de usuários.
- `notification_cargos.json`: Mapeamento de cargos e notificações.

6. EXECUTE A APLICAÇÃO:
Inicie a aplicação com:

python main.py


OBSERVAÇÕES
-----------

1. Personalização de templates de e-mail:
- Os modelos de e-mail podem ser editados no arquivo `email_templates.json`.

2. Requisitos do ambiente:
- Garantir conectividade com o Google Sheets configurado no arquivo `constants.py`.

3. Suporte:
- Em caso de dúvidas, entre em contato com os desenvolvedores:
  - Vitor Isawa: vitorakioisawa@gmail.com
  - Leonardo Macedo: l239207@dac.unicamp.br

LICENÇA
-------

Este projeto é distribuído sob a licença MIT.
