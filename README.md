# Sistema de Consulta SOAP - MNI

Sistema web desenvolvido em Python para consultar processos judiciais através do MNI (Modelo Nacional de Interoperabilidade) utilizando requisições SOAP/WSDL, com visualização organizada de movimentos e download de documentos vinculados.

## 🚀 Tecnologias

- **Python 3.8+**
- **Flask 3.0.0** - Framework web
- **Zeep 4.2.1** - Cliente SOAP/WSDL
- **LXML 5.1.0** - Processamento XML
- **HTML5/CSS3/JavaScript** - Frontend responsivo

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Credenciais válidas para acesso ao serviço MNI

## 🔧 Instalação

### 1. Clone ou baixe os arquivos:
```bash
git clone <seu-repositorio>
cd sistema-soap-mni
```

### 2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

### 5. Edite o arquivo `.env`:
```env
SOAP_WSDL_URL=https://eproc-1g-to.dev.br/ws/intercomunicacao3.0/wsdl/servico-intercomunicacao-3.0.0.wsdl
SOAP_USUARIO=seu_usuario
SOAP_SENHA=sua_senha_hash
SOAP_SERVIDOR_BASE=https://eproc-1g-to.dev.br
SOAP_VERIFY_SSL=false
FLASK_SECRET_KEY=uma-chave-secreta-aleatoria
FLASK_DEBUG=True
```

## 🎯 Uso

### Iniciar o servidor

```bash
python app.py
```

Acesse: `http://localhost:5000`

### Interface Web

1. **Consultar Processo**
   - Acesse a página inicial
   - Insira o número do processo (20 dígitos)
   - Configure opções de consulta
   - Clique em "Consultar Processo"

2. **Visualizar Movimentos e Documentos**
   - Movimentos são exibidos em cards organizados
   - Apenas movimentos com documentos vinculados são mostrados
   - Cada documento exibe:
     - Rótulo (descrição amigável)
     - ID do documento
     - Botão "Enviar para Análise"

3. **Download de Documentos**
   - Clique em "Enviar para Análise" no documento desejado
   - O arquivo será baixado automaticamente
   - Nome do arquivo inclui contexto do movimento

## ✨ Funcionalidades Principais

### 📌 Visualização de Movimentos
- ✅ Exibe apenas movimentos com documentos vinculados
- ✅ Informações detalhadas de cada movimento
- ✅ Data e hora formatadas
- ✅ Descrição do movimento local
- ✅ Tipo de movimento

### 📄 Gestão de Documentos
- ✅ Lista documentos vinculados por movimento
- ✅ Exibe rótulo amigável (campo `outroParametro.rotulo`)
- ✅ Fallback para campo `descricao`
- ✅ Download com nome contextualizado
- ✅ Suporte a múltiplos formatos (PDF, HTML, DOC, etc)

### 🔍 Consulta de Processos
- ✅ Busca por número CNJ (20 dígitos)
- ✅ Filtros por data (inicial/final)
- ✅ Opções configuráveis:
  - Incluir cabeçalho
  - Incluir partes
  - Incluir endereços
  - Incluir movimentos
  - Incluir documentos

### 🎨 Interface Minimalista
- ✅ Design limpo e profissional
- ✅ Link "Voltar" no navbar
- ✅ Sem elementos desnecessários
- ✅ Foco no conteúdo essencial
- ✅ Responsivo para mobile

### 🔧 Funcionalidades Técnicas
- ✅ API REST para integração
- ✅ Descoberta dinâmica de operações SOAP
- ✅ Correção automática de WSDL e XSD
- ✅ Suporte a SSL auto-assinado
- ✅ Logs detalhados
- ✅ Tratamento de erros robusto

## 📡 API REST

### Consultar Processo

**Endpoint:** `POST /api/consultar`

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/consultar \
  -H "Content-Type: application/json" \
  -d '{
    "numero_processo": "00058128320258272729",
    "incluir_movimentos": true,
    "incluir_documentos": true
  }'
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "processo": {
      "movimento": [...],
      "documento": [...]
    }
  }
}
```

### Download de Documento

**Endpoint:** `POST /api/download-documento`

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/download-documento \
  -H "Content-Type: application/json" \
  -d '{
    "numero_processo": "00058128320258272729",
    "id_documento": "771761320987264735528069530499"
  }'
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "documentos": [{
      "idDocumento": "771761...",
      "mimetype": "application/pdf",
      "conteudo_base64": "JVBERi0xLjQK..."
    }]
  }
}
```

## 📊 Estrutura de Dados

### Movimentos com Documentos Vinculados

```json
{
  "processo": {
    "movimento": [
      {
        "idMovimento": "12345",
        "dataHora": "2024-11-27T14:30:00",
        "movimentoLocal": {
          "descricao": "Petição Inicial apresentada"
        },
        "tipoMovimento": "PETIÇÃO",
        "idDocumentoVinculado": [
          "771761320987264735528069530499",
          "771761320987264735528069530500"
        ]
      }
    ],
    "documento": [
      {
        "idDocumento": "771761320987264735528069530499",
        "descricao": "Documento oficial",
        "mimetype": "application/pdf",
        "outroParametro": [
          {
            "nome": "rotulo",
            "valor": "CNPJ - Comprovante de Inscrição"
          },
          {
            "nome": "tamanho",
            "valor": "89188"
          }
        ]
      }
    ]
  }
}
```

### Campo outroParametro

O sistema busca a descrição do documento no campo `rotulo` dentro do array `outroParametro`:

**Prioridade:**
1. `outroParametro[nome='rotulo'].valor` ⭐
2. `descricao` (Fallback)
3. "Documento" (Padrão)

## 📁 Estrutura do Projeto

```
sistema-soap-mni/
├── app.py                     # Aplicação Flask principal
├── soap_service.py            # Serviço SOAP (Zeep)
├── requirements.txt           # Dependências Python
├── .env.example              # Exemplo de configuração
├── .env                      # Configuração (não versionado)
├── .gitignore               # Arquivos ignorados
├── templates/               # Templates Jinja2
│   ├── base.html           # Template base
│   ├── index.html          # Página inicial
│   ├── resultado.html      # Resultados da consulta
│   ├── debug_xml.html      # Debug SOAP
│   ├── sobre.html          # Sobre o sistema
│   ├── 404.html           # Página não encontrada
│   └── 500.html           # Erro interno
└── static/                 # Arquivos estáticos
    ├── css/
    │   └── style.css       # Estilos CSS
    └── js/
        └── script.js       # JavaScript

docs/ (arquivos de documentação)
├── SOLUCAO_SSL.md              # Solução de problemas SSL
├── CORRECAO_SERVIDOR.md        # Correção de placeholders
├── DOWNLOAD_DOCUMENTOS.md      # Guia de download
├── ESTRUTURA_MOVIMENTOS.md     # Estrutura de dados
├── MELHORIAS_INTERFACE.md      # Melhorias de UX
├── OUTRO_PARAMETRO.md          # Campo outroParametro
└── MELHORIAS_LAYOUT.md         # Layout minimalista
```

## 🔒 Segurança

- ✅ Credenciais em variáveis de ambiente (`.env`)
- ✅ Validação de entrada (número processo com 20 dígitos)
- ✅ Sanitização de dados
- ✅ Logs de auditoria
- ✅ Suporte a SSL/TLS
- ✅ `.gitignore` configurado (não versionada credenciais)

## 🐛 Problemas Resolvidos

### SSL Auto-Assinado
```env
SOAP_VERIFY_SSL=false
```
Permite conexão com servidores que usam certificados auto-assinados.

### Placeholder [servidor] no WSDL
```env
SOAP_SERVIDOR_BASE=https://eproc-1g-to.dev.br
```
Substitui automaticamente `[servidor]` por URL completa.

### Caminhos Relativos de XSD
O sistema converte automaticamente caminhos relativos em URLs absolutas.

### Descoberta de Operações SOAP
Mapeia dinamicamente todas as operações disponíveis no WSDL.

## 🧪 Scripts de Teste

### Testar Configuração SSL
```bash
python test_ssl.py
```

### Listar Operações SOAP
```bash
python listar_operacoes.py
```

### Testar Requisição HTTP
```bash
python test_requisicao.py
```

## 📚 Exemplos de Integração

### Python
```python
import requests

# Consultar processo
response = requests.post('http://localhost:5000/api/consultar', json={
    'numero_processo': '00058128320258272729',
    'incluir_movimentos': True,
    'incluir_documentos': True
})

resultado = response.json()
if resultado['success']:
    processo = resultado['data']['processo']
    print(f"Movimentos: {len(processo['movimento'])}")
```

### JavaScript
```javascript
fetch('http://localhost:5000/api/consultar', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    numero_processo: '00058128320258272729',
    incluir_movimentos: true,
    incluir_documentos: true
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### PHP
```php
<?php
$ch = curl_init('http://localhost:5000/api/consultar');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'numero_processo' => '00058128320258272729',
    'incluir_movimentos' => true,
    'incluir_documentos' => true
]));

$response = curl_exec($ch);
$data = json_decode($response, true);
print_r($data);
?>
```

## 🚀 Deploy em Produção

### Usando Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Usando Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Variáveis de Ambiente (Produção)
```env
SOAP_VERIFY_SSL=true
FLASK_DEBUG=False
FLASK_SECRET_KEY=chave-forte-aleatoria-producao
```

## 📖 Documentação Adicional

- [MNI - CNJ](https://www.cnj.jus.br/tecnologia-da-informacao/modelo-nacional-de-interoperabilidade/)
- [Zeep Documentation](https://docs.python-zeep.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## ⚠️ Avisos Importantes

- ✅ Requer credenciais válidas do MNI
- ✅ Use apenas para fins autorizados
- ✅ Em produção, sempre use HTTPS
- ✅ Mantenha credenciais seguras
- ✅ Respeite limites de taxa de requisições

## 🎨 Interface

### Página Inicial
- Formulário de consulta limpo
- Validação em tempo real
- Opções configuráveis

### Página de Resultados
- Cards de movimentos organizados
- Documentos vinculados por movimento
- Botão "Enviar para Análise"
- JSON completo disponível
- Link "Voltar" no navbar

### Design Minimalista
- Sem elementos desnecessários
- Foco no conteúdo
- Responsivo
- Profissional

## 📄 Licença

Este projeto é fornecido como está, sem garantias.

## 👨‍💻 Desenvolvedor

Sistema desenvolvido em Python + Flask para consultas SOAP ao MNI, com foco em usabilidade e organização de documentos judiciais.

---

**Nota:** Este sistema é uma ferramenta auxiliar e não substitui o acesso oficial aos sistemas do Poder Judiciário.