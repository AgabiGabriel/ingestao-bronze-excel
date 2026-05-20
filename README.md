---

## 🏗️ Arquitetura do Pipeline

* **Ambiente Compatível:** Notebooks Spark (Microsoft Fabric, Databricks, Synapse)
* **Linguagens:** Python, PySpark e Pandas
* **Formato de Entrada:** Arquivos compactados do Excel (`.xlsx`) armazenados no sistema de arquivos distribuído.
* **Formato de Saída:** Tabelas gerenciadas em formato Delta Lake no catálogo de dados.

---

## 🛠️ Detalhamento Técnico da Lógica

### 1. Descoberta Dinâmica de Arquivos
O script utiliza funções do ecossistema do sistema operacional para varrer a pasta de origem e mapear o conteúdo em tempo de execução. O filtro por extensão garante que outros formatos temporários ou corrompidos não causem falhas no loop de processamento.

### 2. Leitura Conservadora (`dtype=str`)
A leitura inicial das planilhas é forçada estritamente como formato texto (`string`). 
* **Abordagem de Segurança:** Planilhas Excel frequentemente contêm colunas com identificadores numéricos, chaves compostas ou códigos postais que começam com o dígito zero (`0`). Permitir que o interpretador infira os tipos automaticamente causaria a conversão desses campos para números inteiros ou flutuantes, resultando em perda definitiva de zeros à esquerda. A conversão posterior para os tipos corretos é delegada às camadas de refinamento (Silver/Gold).

### 3. Tratamento de Anomalias do Excel (Data Cleansing)
* **Remoção de Linhas Fantasmas:** Arquivos manipulados manualmente no Excel costumam arrastar linhas em branco salvas no fim da tabela devido a restos de formatação de bordas ou cores. O script remove linhas inteiramente nulas utilizando a lógica `dropna(how='all')`.
* **Substituição de Nulos (`NaN`):** Para evitar quebras de consistência na serialização para o Spark, valores nulos e ausentes são padronizados como strings vazias (`""`).
* **Normalização de Metadados:** Os cabeçalhos das colunas são explicitamente convertidos para texto estruturado, garantindo compatibilidade com o esquema rígido de nomes exigido pelo Spark.

### 4. Paralelização e Escrita Delta
O DataFrame otimizado em Pandas é convertido em um DataFrame nativo do Spark para distribuição de processamento. O nome da tabela final é padronizado de forma programática (letras minúsculas e remoção da extensão do arquivo), aplicando boas práticas de nomenclatura de tabelas em bancos de dados.

---

