# Sistema de Consulta SOAP - MNI

Sistema web desenvolvido em Python para realizar consultas a processos judiciais através do MNI (Modelo Nacional de Interoperabilidade) utilizando requisições SOAP/WSDL.

## 🚀 Tecnologias

- **Python 3.8+**
- **Flask** - Framework web
- **Zeep** - Cliente SOAP/WSDL
- **LXML** - Processamento XML
- **HTML5/CSS3/JavaScript** - Frontend

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Credenciais válidas para acesso ao serviço MNI

## 🔧 Instalação

1. Clone o repositório ou baixe os arquivos:
```bash
git clone <seu-repositorio>
cd sistema-soap-mni
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

5. Edite o arquivo `.env` com suas credenciais:
```
SOAP_WSDL_URL=https://seu-endpoint.com/servico?wsdl
SOAP_USUARIO=seu_usuario
SOAP_SENHA=sua_senha_hash
FLASK_SECRET_KEY=uma-chave-secreta-aleatoria
FLASK_DEBUG=True
```

## 🎯 Uso

### Iniciar o servidor

```bash
python app.py
```

O sistema estará disponível em: `http://localhost:5000`

### Interface Web

1. Acesse `http://localhost:5000`
2. Insira o número do processo (20 dígitos)
3. Configure as opções de consulta desejadas
4. Clique em "Consultar Processo"

### API REST

O sistema também disponibiliza uma API REST para integração:

**Endpoint:** `POST /api/consultar`

**Content-Type:** `application/json`

**Exemplo de requisição:**
```json
{
  "numero_processo": "00058128320258272729",
  "data_inicial": "2024-01-01",
  "data_final": "2024-12-31",
  "incluir_cabecalho": true,
  "incluir_partes": false,
  "incluir_enderecos": false,
  "incluir_movimentos": true,
  "incluir_documentos": true
}
```

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:5000/api/consultar \
  -H "Content-Type: application/json" \
  -d '{
    "numero_processo": "00058128320258272729",
    "incluir_cabecalho": true,
    "incluir_movimentos": true
  }'
```

**Exemplo com Python:**
```python
import requests

url = "http://localhost:5000/api/consultar"
data = {
    "numero_processo": "00058128320258272729",
    "incluir_cabecalho": True,
    "incluir_movimentos": True
}

response = requests.post(url, json=data)
resultado = response.json()

if resultado.get('success'):
    print("Consulta realizada com sucesso!")
    print(resultado['data'])
else:
    print(f"Erro: {resultado.get('error')}")
```

**Exemplo com JavaScript:**
```javascript
fetch('http://localhost:5000/api/consultar', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    numero_processo: '00058128320258272729',
    incluir_cabecalho: true,
    incluir_movimentos: true
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Dados do processo:', data.data);
  } else {
    console.error('Erro:', data.error);
  }
});
```

**Exemplo com PHP:**
```php
<?php
$url = 'http://localhost:5000/api/consultar';
$data = [
    'numero_processo' => '00058128320258272729',
    'incluir_cabecalho' => true,
    'incluir_movimentos' => true
];

$options = [
    'http' => [
        'header'  => "Content-Type: application/json\r\n",
        'method'  => 'POST',
        'content' => json_encode($data)
    ]
];

$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);
$response = json_decode($result, true);

if ($response['success']) {
    echo "Consulta realizada com sucesso!\n";
    print_r($response['data']);
} else {
    echo "Erro: " . $response['error'] . "\n";
}
?>
```

## 📁 Estrutura do Projeto

```
sistema-soap-mni/
├── app.py                  # Aplicação Flask principal
├── soap_service.py         # Serviço SOAP
├── requirements.txt        # Dependências
├── .env.example           # Exemplo de configuração
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── resultado.html
│   ├── debug_xml.html
│   ├── sobre.html
│   ├── 404.html
│   └── 500.html
└── static/                # Arquivos estáticos
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## ✨ Funcionalidades

- ✅ Consulta de processos por número CNJ
- ✅ Filtros por data inicial e final
- ✅ Opções configuráveis de inclusão de dados
- ✅ Visualização formatada dos resultados
- ✅ Exportação em JSON
- ✅ Modo debug com visualização de XMLs SOAP
- ✅ API REST para integração
- ✅ Interface responsiva
- ✅ Validação de dados
- ✅ Tratamento de erros

## 🔒 Segurança

- Credenciais em variáveis de ambiente
- Validação de entrada de dados
- Sanitização de XMLs
- Logs de auditoria
- HTTPS recomendado em produção

## 🐛 Debug

Para visualizar os XMLs de requisição e resposta SOAP:

1. Acesse a seção "Modo Debug" na página inicial
2. Insira o número do processo
3. Clique em "Ver XML Debug"

Ou use a função diretamente no código:

```python
from soap_service import SOAPService

service = SOAPService(wsdl_url, usuario, senha)
xml_data = service.consultar_processo_raw_xml(numero_processo)

print("Request XML:", xml_data['request_xml'])
print("Response XML:", xml_data['response_xml'])
```

## 📝 Estrutura SOAP

A requisição SOAP segue o padrão MNI v3.0.0:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                  xmlns:v300="http://www.cnj.jus.br/mni/v300/" 
                  xmlns:tip="http://www.cnj.jus.br/mni/v300/tipos-servico-intercomunicacao" 
                  xmlns:int="http://www.cnj.jus.br/mni/v300/intercomunicacao">
   <soapenv:Header/>
   <soapenv:Body>
      <v300:requisicaoConsultarProcesso>
         <tip:consultante>
            <int:autenticacaoSimples>
               <int:usuario>SEU_USUARIO</int:usuario>
               <int:senha>SUA_SENHA</int:senha>
            </int:autenticacaoSimples>
         </tip:consultante>
         <tip:numeroProcesso>00058128320258272729</tip:numeroProcesso>
         <tip:incluirCabecalho>true</tip:incluirCabecalho>
         <tip:incluirMovimentos>true</tip:incluirMovimentos>
      </v300:requisicaoConsultarProcesso>
   </soapenv:Body>
</soapenv:Envelope>
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

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Variáveis de Ambiente em Produção

```bash
SOAP_WSDL_URL=https://producao.com/servico?wsdl
SOAP_USUARIO=usuario_producao
SOAP_SENHA=senha_hash_producao
FLASK_SECRET_KEY=chave-secreta-forte-aleatoria
FLASK_DEBUG=False
FLASK_PORT=8000
```

## 🧪 Testes

Para testar a aplicação:

```bash
# Testar servidor
python app.py

# Testar API
curl -X POST http://localhost:5000/api/consultar \
  -H "Content-Type: application/json" \
  -d '{"numero_processo": "00058128320258272729"}'
```

## 📚 Documentação Adicional

- [Documentação MNI - CNJ](https://www.cnj.jus.br/tecnologia-da-informacao/modelo-nacional-de-interoperabilidade/)
- [Documentação Zeep](https://docs.python-zeep.org/)
- [Documentação Flask](https://flask.palletsprojects.com/)

## ⚠️ Avisos

- Este sistema requer credenciais válidas para acessar o serviço MNI
- Use apenas para fins autorizados e legítimos
- Em produção, sempre use HTTPS
- Mantenha suas credenciais seguras e nunca as compartilhe

## 📄 Licença

Este projeto é fornecido como está, sem garantias.

## 👨‍💻 Desenvolvedor

Desenvolvido com Python + Flask para facilitar consultas SOAP ao MNI.

---

**Nota:** Este sistema é uma ferramenta de consulta e não substitui o acesso oficial aos sistemas do Poder Judiciário.
