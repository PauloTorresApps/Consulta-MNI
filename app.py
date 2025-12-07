import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from dotenv import load_dotenv
from soap_service import SOAPService
import json
from datetime import datetime


# Configurar logging para o app
logging.basicConfig(level=logging.INFO) # <--- ADICIONAR ESTA LINHA
logger = logging.getLogger(__name__)    # <--- ADICIONAR ESTA L

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurar serviço SOAP
WSDL_URL = os.getenv('SOAP_WSDL_URL')
USUARIO = os.getenv('SOAP_USUARIO')
SENHA = os.getenv('SOAP_SENHA')
SERVIDOR_BASE = os.getenv('SOAP_SERVIDOR_BASE')
# Corrigir lógica: se SOAP_VERIFY_SSL=false, então verify_ssl deve ser False
VERIFY_SSL_STR = os.getenv('SOAP_VERIFY_SSL', 'true').lower()
VERIFY_SSL = VERIFY_SSL_STR not in ('false', '0', 'no', 'n', 'off')


def get_soap_service():
    """Retorna instância do serviço SOAP"""
    if not all([WSDL_URL, USUARIO, SENHA]):
        raise ValueError("Configurações SOAP não encontradas. Configure as variáveis de ambiente.")
    return SOAPService(WSDL_URL, USUARIO, SENHA, verify_ssl=VERIFY_SSL, servidor_base=SERVIDOR_BASE)


@app.route('/')
def index():
    """Página inicial com formulário de consulta"""
    return render_template('index.html')


@app.route('/consultar', methods=['POST'])
def consultar():
    """Endpoint para consultar processo"""
    try:
        # Obter dados do formulário
        numero_processo = request.form.get('numero_processo', '').strip()
        data_inicial = request.form.get('data_inicial', '').strip()
        data_final = request.form.get('data_final', '').strip()
        
        # Opções booleanas
        incluir_cabecalho = request.form.get('incluir_cabecalho') == 'on'
        incluir_partes = request.form.get('incluir_partes') == 'on'
        incluir_enderecos = request.form.get('incluir_enderecos') == 'on'
        incluir_movimentos = request.form.get('incluir_movimentos') == 'on'
        incluir_documentos = request.form.get('incluir_documentos') == 'on'
        
        # Validar número do processo
        if not numero_processo:
            flash('Número do processo é obrigatório', 'error')
            return redirect(url_for('index'))
        
        # Remover caracteres especiais do número do processo
        numero_processo = ''.join(filter(str.isdigit, numero_processo))
        
        if len(numero_processo) != 20:
            flash('Número do processo deve ter 20 dígitos', 'error')
            return redirect(url_for('index'))
        
        # Criar serviço e consultar
        soap_service = get_soap_service()
        
        resultado = soap_service.consultar_processo(
            numero_processo=numero_processo,
            data_inicial=data_inicial if data_inicial else None,
            data_final=data_final if data_final else None,
            incluir_cabecalho=incluir_cabecalho,
            incluir_partes=incluir_partes,
            incluir_enderecos=incluir_enderecos,
            incluir_movimentos=incluir_movimentos,
            incluir_documentos=incluir_documentos
        )
        
        return render_template('resultado.html', 
                             resultado=resultado,
                             numero_processo=numero_processo,
                             data_consulta=datetime.now())
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao consultar processo: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/consultar', methods=['POST'])
def api_consultar():
    """API endpoint para consultar processo (retorna JSON)"""
    try:
        # Obter dados do JSON
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        numero_processo = data.get('numero_processo', '').strip()
        
        if not numero_processo:
            return jsonify({'error': 'Número do processo é obrigatório'}), 400
        
        # Remover caracteres especiais
        numero_processo = ''.join(filter(str.isdigit, numero_processo))
        
        if len(numero_processo) != 20:
            return jsonify({'error': 'Número do processo deve ter 20 dígitos'}), 400
        
        # Criar serviço e consultar
        soap_service = get_soap_service()
        
        resultado = soap_service.consultar_processo(
            numero_processo=numero_processo,
            data_inicial=data.get('data_inicial'),
            data_final=data.get('data_final'),
            incluir_cabecalho=data.get('incluir_cabecalho', True),
            incluir_partes=data.get('incluir_partes', False),
            incluir_enderecos=data.get('incluir_enderecos', False),
            incluir_movimentos=data.get('incluir_movimentos', True),
            incluir_documentos=data.get('incluir_documentos', True)
        )
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao consultar processo: {str(e)}'}), 500


@app.route('/debug/xml', methods=['POST'])
def debug_xml():
    """Endpoint para visualizar XMLs de requisição e resposta"""
    try:
        numero_processo = request.form.get('numero_processo', '').strip()
        
        if not numero_processo:
            flash('Número do processo é obrigatório', 'error')
            return redirect(url_for('index'))
        
        numero_processo = ''.join(filter(str.isdigit, numero_processo))
        
        if len(numero_processo) != 20:
            flash('Número do processo deve ter 20 dígitos', 'error')
            return redirect(url_for('index'))
        
        soap_service = get_soap_service()
        
        xml_data = soap_service.consultar_processo_raw_xml(
            numero_processo=numero_processo,
            incluir_cabecalho=True,
            incluir_partes=False,
            incluir_enderecos=False,
            incluir_movimentos=True,
            incluir_documentos=True
        )
        
        return render_template('debug_xml.html', 
                             xml_data=xml_data,
                             numero_processo=numero_processo)
        
    except Exception as e:
        flash(f'Erro ao obter XML: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/sobre')
def sobre():
    """Página sobre o sistema"""
    return render_template('sobre.html')


@app.route('/download-documento', methods=['POST'])
def download_documento():
    
    logger.info(f"Iniciando download de documento################################################################")
    """Endpoint para baixar documento do processo"""
    try:
        # Obter dados do POST
        numero_processo = request.form.get('numero_processo', '').strip()
        id_documento = request.form.get('id_documento', '').strip()
        id_movimento = request.form.get('id_movimento', '').strip()
        descricao_movimento = request.form.get('descricao_movimento', '').strip()
        
        if not numero_processo or not id_documento:
            flash('Número do processo e ID do documento são obrigatórios', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Remover caracteres especiais do número do processo
        numero_processo = ''.join(filter(str.isdigit, numero_processo))
        
        # Log de informações
        logger.info(f"Download documento: Processo={numero_processo}, Doc={id_documento}, Mov={id_movimento}")
        
        # Criar serviço e consultar documento
        soap_service = get_soap_service()
        
        resultado = soap_service.consultar_documentos_processo(
            numero_processo=numero_processo,
            ids_documentos=id_documento
        )
        
        if not resultado.get('sucesso'):
            flash(f'Erro ao baixar documento: {resultado.get("erro", "Erro desconhecido")}', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Obter primeiro documento
        documentos = resultado.get('documentos', [])
        if not documentos:
            flash('Nenhum documento encontrado', 'error')
            return redirect(request.referrer or url_for('index'))
        
        documento = documentos[0]
        
        # Preparar resposta com arquivo
        conteudo = documento.get('conteudo')
        if not conteudo:
            flash('Documento sem conteúdo', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Determinar nome do arquivo e tipo MIME
        mimetype = documento.get('mimetype', 'application/octet-stream')
        extensao = {
            'application/pdf': 'pdf',
            'text/html': 'html',
            'text/plain': 'txt',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'image/jpeg': 'jpg',
            'image/png': 'png',
        }.get(mimetype, 'bin')
        
        # Criar nome do arquivo com informações do movimento se disponível
        if descricao_movimento and id_movimento:
            # Sanitizar descrição para usar no nome do arquivo
            descricao_safe = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in descricao_movimento)
            descricao_safe = descricao_safe[:50]  # Limitar tamanho
            filename = f'mov_{id_movimento}_{descricao_safe}.{extensao}'
        else:
            filename = f'documento_{id_documento}.{extensao}'
        
        # Retornar arquivo para download
        from flask import send_file
        from io import BytesIO
        
        return send_file(
            BytesIO(conteudo),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erro ao baixar documento: {str(e)}")
        flash(f'Erro ao baixar documento: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))


@app.route('/api/download-documento', methods=['POST'])
def api_download_documento():
    """API endpoint para baixar documento (retorna base64)"""
    try:
        # Obter dados do JSON
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        numero_processo = data.get('numero_processo', '').strip()
        id_documento = data.get('id_documento', '').strip()
        
        if not numero_processo or not id_documento:
            return jsonify({'error': 'Número do processo e ID do documento são obrigatórios'}), 400
        
        # Remover caracteres especiais
        numero_processo = ''.join(filter(str.isdigit, numero_processo))
        
        # Criar serviço e consultar documento
        soap_service = get_soap_service()
        
        resultado = soap_service.consultar_documentos_processo(
            numero_processo=numero_processo,
            ids_documentos=id_documento
        )
        
        if not resultado.get('sucesso'):
            return jsonify({
                'error': resultado.get('erro', 'Erro desconhecido'),
                'success': False
            }), 500
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar documento: {str(e)}'}), 500


@app.errorhandler(404)
def page_not_found(e):
    """Tratamento de erro 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Tratamento de erro 500"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)