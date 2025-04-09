
# 🧠 Projeto de Carga de Dados Automatizada 

Este projeto realiza um processo **completo de ETL (Extração, Transformação e Carga)** a partir de um sistema web, utilizando automação com Selenium e integração com PostgreSQL para alimentar um Data Warehouse com modelo dimensional.

## 📌 Visão Geral

O pipeline automatiza a coleta de informações sobre visitas comerciais, vendas (DSV) e situação dos clientes. Ele é composto por:

- **Web Scraping** com Selenium
- **Tratamento e cruzamento** com Pandas + Excel de apoio
- **Carga em banco de dados PostgreSQL** (dimensões e fato)
- Pronto para visualização no Power BI

---

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Selenium (WebDriver)
- Pandas
- SQLAlchemy
- psycopg2
- PostgreSQL

---

## 📂 Estrutura do Projeto

```
📦 projeto-sovis-etl/
├── pipeline_sovis.py              # Script principal com todo o processo
├── pipeline_sovis_generico.py     # Versão anonimizada para publicação
├── Documentacao_Pipeline_SOVIS.docx  # Documentação completa do projeto
├── Clientes (mês X ano).xlsx      # Base de apoio para enriquecer os dados
```

---

## ⚙️ Funcionalidades

- 🔐 **Login automatizado** no sistema
- 🌐 **Navegação dinâmica** entre páginas
- 📑 **Extração estruturada** dos seguintes dados:
  - Código do cliente
  - ID externo (sistema)
  - Razão social
  - DSV
  - Última visita
  - Situação do cliente
- 🔗 **Cruzamento com Excel** para identificar o vendedor responsável
- 🧹 **Limpeza e carga no DW**, com:
  - Truncamento das tabelas
  - Recriação de constraints
  - Carga nas dimensões (sem duplicatas)
  - Inserção controlada na fato

---

## 🧪 Pré-requisitos

- Python instalado
- PostgreSQL em execução
- Google Chrome + ChromeDriver compatível
- Variáveis como e-mail, senha e XPaths precisam ser ajustadas no script

---

## 🚀 Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/projeto-sovis-etl.git
cd projeto-sovis-etl
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o script principal:
```bash
python pipeline_sovis.py
```

---

## 📊 Resultado Esperado

Ao final da execução, os dados estarão disponíveis nas tabelas:

- `dim_cliente`
- `dim_situacao`
- `dim_data`
- `dim_vendedor`
- `fato_dsv`

Esses dados poderão ser consumidos por ferramentas como Power BI para análise de performance comercial.

---

## 📌 Observações

> O script contém trechos com dados sensíveis (login e XPaths específicos). Para publicação, utilize a versão `pipeline_sovis_generico.py`.

---

## 👨‍💻 Autor

Desenvolvido por **Lucca Carnaúba Peixoto Rosário**  
Tecnologias: Python, Selenium, Pandas, SQL, PostgreSQL  
Contato: [seu-email@exemplo.com](mailto:seu-email@exemplo.com)
