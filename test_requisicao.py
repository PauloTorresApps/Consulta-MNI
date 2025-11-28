#!/usr/bin/env python3
"""
Script para testar requisição SOAP e ver resposta bruta
"""

import os
from dotenv import load_dotenv
import requests
import urllib3

# Carregar variáveis de ambiente
load_dotenv()

wsdl_url = os.getenv('SOAP_WSDL_URL')
usuario = os.getenv('SOAP_USUARIO')
senha = os.getenv('SOAP_SENHA')
servidor_base = os.getenv('SOAP_SERVIDOR_BASE')
verify_ssl_str = os.getenv('SOAP_VERIFY_SSL', 'true').lower()
verify_ssl = verify_ssl_str not in ('false', '0', 'no', 'n', 'off')

if not verify_ssl:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 80)
print("TESTE DE REQUISIÇÃO SOAP - RESPOSTA BRUTA")
print("=" * 80)

# Montar XML SOAP manualmente
soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope 
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:v300="http://www.cnj.jus.br/mni/v300/" 
    xmlns:tip="http://www.cnj.jus.br/mni/v300/tipos-servico-intercomunicacao" 
    xmlns:int="http://www.cnj.jus.br/mni/v300/intercomunicacao">
   <soapenv:Header/>
   <soapenv:Body>
      <v300:requisicaoConsultarProcesso>
         <tip:consultante>
            <int:autenticacaoSimples>
               <int:usuario>{usuario}</int:usuario>
               <int:senha>{senha}</int:senha>
            </int:autenticacaoSimples>
         </tip:consultante>
         <tip:numeroProcesso>00058128320258272729</tip:numeroProcesso>
         <tip:incluirCabecalho>true</tip:incluirCabecalho>
         <tip:incluirPartes>false</tip:incluirPartes>
         <tip:incluirEnderecos>false</tip:incluirEnderecos>
         <tip:incluirMovimentos>true</tip:incluirMovimentos>
         <tip:incluirDocumentos>true</tip:incluirDocumentos>
      </v300:requisicaoConsultarProcesso>
   </soapenv:Body>
</soapenv:Envelope>"""

# URL do serviço
service_url = f"{servidor_base}/ws/controlador_ws.php?srv=intercomunicacao3.0"

print(f"\n📤 Enviando requisição para:")
print(f"   {service_url}")
print(f"\n📋 XML da Requisição (primeiros 500 chars):")
print(soap_envelope[:500])
print("\n" + "-" * 80)

# Fazer requisição HTTP direta
headers = {
    'Content-Type': 'text/xml; charset=utf-8',
    'SOAPAction': '',
}

try:
    response = requests.post(
        service_url,
        data=soap_envelope.encode('utf-8'),
        headers=headers,
        verify=verify_ssl,
        timeout=30
    )
    
    print(f"\n📥 Resposta recebida:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"   Content-Length: {len(response.content)} bytes")
    
    print(f"\n📄 Conteúdo da Resposta (primeiros 1000 caracteres):")
    print("-" * 80)
    
    try:
        content = response.content.decode('utf-8', errors='ignore')
        print(content[:1000])
        
        if content[:1000].lower().strip().startswith('<'):
            print("\n✅ Resposta parece ser XML")
        else:
            print("\n❌ Resposta NÃO é XML válido!")
            print("   Possível página de erro HTML ou texto puro")
            
    except Exception as e:
        print(f"❌ Erro ao decodificar: {e}")
        print(response.content[:1000])
    
    print("\n" + "-" * 80)
    
    # Salvar resposta completa
    with open('resposta_soap.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\n💾 Resposta completa salva em: resposta_soap.txt")
    
except requests.exceptions.SSLError as e:
    print(f"\n❌ Erro SSL: {e}")
    print("   Configure SOAP_VERIFY_SSL=false no .env para desenvolvimento")
    
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Erro de Conexão: {e}")
    print("   Verifique se a URL está correta e o servidor está acessível")
    
except Exception as e:
    print(f"\n❌ Erro: {type(e).__name__}: {e}")

print("\n" + "=" * 80)