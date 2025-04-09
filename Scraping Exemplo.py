
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text
import psycopg2

# ========== CONFIGURAÇÃO ==========
DB_HOST = 'localhost'  # Coloque o host do banco
DB_PORT = '5432'       # Coloque a porta do banco
DB_NAME = 'nome_do_banco'  # Coloque o nome do seu banco
DB_USER = 'usuario'    # Coloque seu usuário do banco
DB_PASS = 'senha'      # Coloque sua senha do banco

CAMINHO_CLIENTES = r"caminho\para\arquivo_base.xlsx"  # Caminho local para inserção de base

# ========== WEB SCRAPING ==========
def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def login_sistema(driver):
    driver.get("https://site-do-sistema.com.br/login")  # Insira aqui o site para extração
    wait = WebDriverWait(driver, 15) # Tempo de espera para não crashar o site

    campo_email = wait.until(EC.element_to_be_clickable((By.XPATH, 'xpath_do_email')))
    campo_email.click()
    driver.switch_to.active_element.send_keys("seu_email@exemplo.com")  # Coloque seu email

    campo_senha = wait.until(EC.element_to_be_clickable((By.XPATH, 'xpath_da_senha')))
    campo_senha.click()
    driver.switch_to.active_element.send_keys("sua_senha_segura")  # Coloque sua senha

    botao_login = wait.until(EC.element_to_be_clickable((By.XPATH, 'xpath_do_botao_login')))
    botao_login.click()
    time.sleep(5)

def acessar_aba_cliente(driver):
    wait = WebDriverWait(driver, 15)
    aba_clientes = wait.until(EC.element_to_be_clickable((By.XPATH, 'xpath_aba_clientes')))
    aba_clientes.click()
    time.sleep(1)
    subaba_cliente = wait.until(EC.element_to_be_clickable((By.XPATH, 'xpath_subaba_clientes')))
    subaba_cliente.click()
    time.sleep(5)

def extrair_dados_pagina(driver):
    wait = WebDriverWait(driver, 15)
    dados = []

    wait.until(EC.presence_of_element_located((By.XPATH, 'xpath_linhas_da_tabela')))
    linhas = driver.find_elements(By.XPATH, 'xpath_linhas_da_tabela')

    for linha in linhas:
        # Loop de extração de colunas da web
        try:
            codigo = linha.find_element(By.XPATH, './td[2]').text.strip() or "Sem Informação"
            id_externo = linha.find_element(By.XPATH, './td[3]').text.strip() or "Sem Informação"
            razao = linha.find_element(By.XPATH, './td[5]').text.strip() or "Sem Informação"
            dsv = linha.find_element(By.XPATH, './td[6]').text.strip() or "Sem Informação"
            ultima = linha.find_element(By.XPATH, './td[7]').text.strip() or "01/01/1900"
            situacao = linha.find_element(By.XPATH, './td[8]').text.strip() or "Sem Informação"

            dsv = "Sem Informação" if dsv.lower() == "nunca vendido" else dsv
            ultima = "1900-01-01" if ultima.lower() == "nunca visitado" else ultima

            # Dicionário de dados
            dados.append({
                "codigo": codigo,
                "id_externo": id_externo,
                "razao_social": razao,
                "dsv": dsv,
                "ultima_visita": ultima,
                "situacao": situacao
            })
        except Exception as e:
            print("Erro ao extrair linha:", e)
    return dados

# Função para passar para a próxima páxina
def clicar_proxima_pagina(driver):
    try:
        botao_proxima = driver.find_element(By.XPATH, 'xpath_botao_proxima_pagina')
        if "disabled" in botao_proxima.get_attribute("class"):
            return False
        botao_proxima.click()
        time.sleep(2)
        return True
    except:
        return False

# ========== EXECUÇÃO ==========
driver = iniciar_driver()
login_sistema(driver)
acessar_aba_cliente(driver)

todos_os_dados = []
pagina = 1
limite_paginas = 503

while pagina <= limite_paginas:
    print(f"Extraindo página {pagina}...")
    dados_pagina = extrair_dados_pagina(driver)
    if not dados_pagina:
        break
    todos_os_dados.extend(dados_pagina)
    if not clicar_proxima_pagina(driver):
        break
    pagina += 1

driver.quit()
df_final = pd.DataFrame(todos_os_dados)
df_final.fillna("Sem Informação", inplace=True)
df_final["ultima_visita"] = df_final["ultima_visita"].replace("", "01/01/1900")

# Cruzamento com base de clientes
df_clientes = pd.read_excel(CAMINHO_CLIENTES, skiprows=5, dtype={"Código do cliente": str})
df_clientes["Código do cliente"] = df_clientes["Código do cliente"].str.strip()
df_final["codigo_ajustado"] = df_final["codigo"].str[:-4]
df_final = pd.merge(
    df_final,
    df_clientes[["Código do cliente", "VENDOR"]],
    how="left",
    left_on="codigo_ajustado",
    right_on="Código do cliente"
)
df_final.rename(columns={"VENDOR": "vendedor"}, inplace=True)
df_final.drop(columns=["codigo_ajustado", "Código do cliente"], inplace=True, errors="ignore")
df_final.fillna("Sem Informação", inplace=True)

# ========== CARGA NO DW ==========
conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

# Truncamento e constraints
with engine.begin() as conn:
    print("🧹 Limpando DW...")
    conn.execute(text("ALTER TABLE fato_dsv DROP CONSTRAINT IF EXISTS fk_cliente"))
    conn.execute(text("ALTER TABLE fato_dsv DROP CONSTRAINT IF EXISTS fk_situacao"))
    conn.execute(text("ALTER TABLE fato_dsv DROP CONSTRAINT IF EXISTS fk_data"))
    conn.execute(text("ALTER TABLE fato_dsv DROP CONSTRAINT IF EXISTS fk_vendedor"))
    conn.execute(text("TRUNCATE TABLE fato_dsv RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dim_cliente RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dim_situacao RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dim_data RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dim_vendedor RESTART IDENTITY CASCADE"))
    conn.execute(text("""
        ALTER TABLE fato_dsv ADD CONSTRAINT fk_cliente FOREIGN KEY (id_cliente) REFERENCES dim_cliente(id_cliente);
        ALTER TABLE fato_dsv ADD CONSTRAINT fk_situacao FOREIGN KEY (id_situacao) REFERENCES dim_situacao(id_situacao);
        ALTER TABLE fato_dsv ADD CONSTRAINT fk_data FOREIGN KEY (id_data) REFERENCES dim_data(id_data);
        ALTER TABLE fato_dsv ADD CONSTRAINT fk_vendedor FOREIGN KEY (id_vendedor) REFERENCES dim_vendedor(id_vendedor);
    """))

# Carga nas dimensões
df_final[["codigo", "razao_social", "id_externo"]].rename(columns={"razao_social": "razaosocial"}).drop_duplicates().to_sql("dim_cliente", engine, if_exists="append", index=False)
df_final[["situacao"]].drop_duplicates().to_sql("dim_situacao", engine, if_exists="append", index=False)
df_final[["ultima_visita"]].rename(columns={"ultima_visita": "data_visita"}).drop_duplicates().to_sql("dim_data", engine, if_exists="append", index=False)
df_final[["vendedor"]].drop_duplicates().to_sql("dim_vendedor", engine, if_exists="append", index=False)

# ========== CARGA DA FATO ==========
with psycopg2.connect(
    host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
) as conn:
    cur = conn.cursor()
    total = 0

    for _, row in df_final.iterrows():
        try:
            cur.execute("SELECT id_cliente FROM dim_cliente WHERE codigo = %s LIMIT 1", (row["codigo"],))
            id_cliente = cur.fetchone()
            if not id_cliente:
                continue

            cur.execute("SELECT id_situacao FROM dim_situacao WHERE situacao = %s LIMIT 1", (row["situacao"],))
            id_situacao = cur.fetchone()
            if not id_situacao:
                continue

            cur.execute("SELECT id_data FROM dim_data WHERE data_visita = %s::date LIMIT 1", (row["ultima_visita"],))
            id_data = cur.fetchone()
            if not id_data:
                continue

            cur.execute("SELECT id_vendedor FROM dim_vendedor WHERE vendedor = %s LIMIT 1", (row["vendedor"],))
            id_vendedor = cur.fetchone()
            if not id_vendedor:
                continue

            cur.execute("""
                INSERT INTO fato_dsv (
                    id_cliente, id_situacao, id_data, id_vendedor, dsv
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                id_cliente[0], id_situacao[0], id_data[0], id_vendedor[0], row["dsv"]
            ))
            total += 1
        except Exception as e:
            print("Erro na linha:", e)

    conn.commit()
    cur.close()

print(f"✅ Carga finalizada com sucesso! Registros inseridos na fato: {total}")
