-- =============================
-- TABELAS DE DIMENSÃO
-- =============================

CREATE TABLE dim_cliente (
    id_cliente SERIAL PRIMARY KEY,
    codigo VARCHAR(30),
    razaosocial VARCHAR(255),
    id_sovis VARCHAR(100)  -- Alterado de int para varchar para evitar erro de estouro
);

CREATE TABLE dim_situacao (
    id_situacao SERIAL PRIMARY KEY,
    situacao VARCHAR(100)
);

CREATE TABLE dim_data (
    id_data SERIAL PRIMARY KEY,
    data_visita DATE
);

CREATE TABLE dim_vendedor (
    id_vendedor SERIAL PRIMARY KEY,
    vendedor VARCHAR(100)
);

-- =============================
-- TABELA FATO
-- =============================

CREATE TABLE fato_dsv (
    id_fato SERIAL PRIMARY KEY,
    id_cliente INT,
    id_situacao INT,
    id_data INT,
    id_vendedor INT,
    dsv VARCHAR(100)
);

-- =============================
-- CONSTRAINTS DE INTEGRIDADE
-- =============================

ALTER TABLE fato_dsv
    ADD CONSTRAINT fk_cliente FOREIGN KEY (id_cliente) REFERENCES dim_cliente(id_cliente);

ALTER TABLE fato_dsv
    ADD CONSTRAINT fk_situacao FOREIGN KEY (id_situacao) REFERENCES dim_situacao(id_situacao);

ALTER TABLE fato_dsv
    ADD CONSTRAINT fk_data FOREIGN KEY (id_data) REFERENCES dim_data(id_data);

ALTER TABLE fato_dsv
    ADD CONSTRAINT fk_vendedor FOREIGN KEY (id_vendedor) REFERENCES dim_vendedor(id_vendedor);

-- =============================
-- ÍNDICES PARA PERFORMANCE
-- =============================

CREATE INDEX idx_fato_cliente ON fato_dsv(id_cliente);
CREATE INDEX idx_fato_situacao ON fato_dsv(id_situacao);
CREATE INDEX idx_fato_data ON fato_dsv(id_data);
CREATE INDEX idx_fato_vendedor ON fato_dsv(id_vendedor);. documente esse script da melhor forma possível, tudo bem explicado! 