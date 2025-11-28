import os
import tempfile
import re
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from lxml import etree
import logging
import urllib3

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SOAPService:
    """Serviço para realizar consultas SOAP ao MNI (Modelo Nacional de Interoperabilidade)"""
    
    def __init__(self, wsdl_url, usuario, senha, verify_ssl=True, servidor_base=None):
        """
        Inicializa o serviço SOAP
        
        Args:
            wsdl_url: URL do WSDL
            usuario: Usuário para autenticação
            senha: Senha para autenticação
            verify_ssl: Verificar certificado SSL (padrão: True)
            servidor_base: URL base do servidor (ex: https://eproc-1g-to.dev.br)
        """
        self.wsdl_url = wsdl_url
        self.usuario = usuario
        self.senha = senha
        self.verify_ssl = verify_ssl
        self.servidor_base = servidor_base
        
        # Desabilitar warnings de SSL se verify_ssl for False
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("⚠️ AVISO: Verificação SSL desabilitada! Use apenas em ambiente de desenvolvimento.")
        
        # Configurar sessão HTTP com timeout
        session = Session()
        session.verify = verify_ssl  # Verificar certificado SSL
        
        # Se servidor_base foi fornecido, baixar e corrigir WSDL
        if servidor_base:
            wsdl_url = self._preparar_wsdl(wsdl_url, servidor_base, session)
        
        # Configurar transport e settings do Zeep
        transport = Transport(session=session, timeout=30)
        settings = Settings(strict=False, xml_huge_tree=True, raw_response=False)
        
        # Criar plugin para capturar requisições/respostas
        from zeep.plugins import HistoryPlugin
        history = HistoryPlugin()
        
        # Criar cliente SOAP
        try:
            self.client = Client(wsdl_url, transport=transport, settings=settings, plugins=[history])
            self.history = history
            logger.info(f"Cliente SOAP inicializado com sucesso: {wsdl_url}")
            
            # Descobrir operações disponíveis
            self._descobrir_operacoes()
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente SOAP: {str(e)}")
            raise
    
    def _preparar_wsdl(self, wsdl_url, servidor_base, session):
        """
        Baixa o WSDL e corrige as URLs com [servidor] e paths relativos
        
        Args:
            wsdl_url: URL do WSDL original
            servidor_base: URL base do servidor
            session: Sessão HTTP
            
        Returns:
            str: Caminho para o WSDL corrigido
        """
        import tempfile
        import re
        from urllib.parse import urljoin, urlparse
        
        logger.info(f"Baixando e corrigindo WSDL de: {wsdl_url}")
        
        # Baixar WSDL
        response = session.get(wsdl_url, timeout=30)
        response.raise_for_status()
        
        wsdl_content = response.text
        
        # Garantir que servidor_base não termine com /
        servidor = servidor_base.rstrip('/')
        
        # Substituir [servidor] no conteúdo
        wsdl_corrigido = wsdl_content.replace('[servidor]', servidor + '/')
        
        # Remover barras duplas (exceto em protocolo://)
        wsdl_corrigido = re.sub(r'(?<!:)//+', '/', wsdl_corrigido)
        
        # Corrigir imports/includes de XSD com caminhos relativos
        # Procurar por schemaLocation="/xsd/..." e converter para URL absoluta
        base_url = wsdl_url.rsplit('/', 1)[0] + '/'  # URL base do WSDL
        
        def substituir_schema_location(match):
            schema_path = match.group(1)
            if schema_path.startswith('/'):
                # Caminho absoluto no servidor
                schema_url = servidor + schema_path
            elif not schema_path.startswith('http'):
                # Caminho relativo
                schema_url = urljoin(base_url, schema_path)
            else:
                # Já é URL completa
                schema_url = schema_path
            
            logger.info(f"XSD encontrado: {schema_path} -> {schema_url}")
            return f'schemaLocation="{schema_url}"'
        
        # Substituir schemaLocation
        wsdl_corrigido = re.sub(
            r'schemaLocation="([^"]+)"',
            substituir_schema_location,
            wsdl_corrigido
        )
        
        # Substituir import location também
        def substituir_import_location(match):
            import_path = match.group(1)
            if import_path.startswith('/'):
                import_url = servidor + import_path
            elif not import_path.startswith('http'):
                import_url = urljoin(base_url, import_path)
            else:
                import_url = import_path
            
            logger.info(f"Import encontrado: {import_path} -> {import_url}")
            return f'location="{import_url}"'
        
        wsdl_corrigido = re.sub(
            r'location="([^"]+)"',
            substituir_import_location,
            wsdl_corrigido
        )
        
        # Salvar WSDL corrigido em arquivo temporário
        fd, temp_path = tempfile.mkstemp(suffix='.wsdl', text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(wsdl_corrigido)
        
        logger.info(f"WSDL corrigido salvo em: {temp_path}")
        logger.info(f"Substituições feitas: [servidor] -> {servidor}/")
        
        return temp_path
    
    
    def _descobrir_operacoes(self):
        """Descobre as operações disponíveis no WSDL"""
        self.operacoes = {}
        
        for service in self.client.wsdl.services.values():
            for port in service.ports.values():
                for operation_name in port.binding._operations.keys():
                    self.operacoes[operation_name.lower()] = operation_name
        
        logger.info(f"Operações disponíveis: {list(self.operacoes.keys())}")
    
    def _get_operation_name(self, nome_base):
        """
        Encontra o nome correto da operação, tentando variações
        
        Args:
            nome_base: Nome base da operação (ex: 'consultarprocesso')
            
        Returns:
            str: Nome correto da operação
        """
        # Tentar nome exato (case insensitive)
        nome_lower = nome_base.lower()
        if nome_lower in self.operacoes:
            return self.operacoes[nome_lower]
        
        # Tentar com 'requisicao' no início
        nome_com_req = f'requisicao{nome_base}'.lower()
        if nome_com_req in self.operacoes:
            return self.operacoes[nome_com_req]
        
        # Tentar encontrar por correspondência parcial
        for op_key, op_name in self.operacoes.items():
            if nome_base.lower() in op_key:
                logger.info(f"Encontrada operação por correspondência: {op_name}")
                return op_name
        
        # Se não encontrar, retornar o primeiro que parece ser de consulta
        for op_key, op_name in self.operacoes.items():
            if 'consultar' in op_key or 'processo' in op_key:
                logger.warning(f"Usando operação alternativa: {op_name}")
                return op_name
        
        # Último recurso: retornar a primeira operação
        if self.operacoes:
            primeiro = list(self.operacoes.values())[0]
            logger.warning(f"Usando primeira operação disponível: {primeiro}")
            return primeiro
        
        raise ValueError(f"Nenhuma operação encontrada no WSDL")
    
    def consultar_processo(self, numero_processo, data_inicial=None, data_final=None,
                          incluir_cabecalho=True, incluir_partes=False,
                          incluir_enderecos=False, incluir_movimentos=True,
                          incluir_documentos=True, parametros=None):
        """
        Consulta informações de um processo judicial
        
        Args:
            numero_processo: Número do processo (20 dígitos sem formatação)
            data_inicial: Data inicial para filtro (opcional)
            data_final: Data final para filtro (opcional)
            incluir_cabecalho: Incluir cabeçalho do processo
            incluir_partes: Incluir partes do processo
            incluir_enderecos: Incluir endereços das partes
            incluir_movimentos: Incluir movimentações
            incluir_documentos: Incluir documentos
            parametros: Lista de dicionários com parâmetros adicionais
            
        Returns:
            dict: Resposta do serviço SOAP
        """
        try:
            # Preparar estrutura de autenticação
            autenticacao = {
                'autenticacaoSimples': {
                    'usuario': self.usuario,
                    'senha': self.senha
                }
            }
            
            # Preparar consultante
            consultante = autenticacao
            
            # Preparar parâmetros da requisição
            requisicao = {
                'consultante': consultante,
                'numeroProcesso': numero_processo,
                'incluirCabecalho': incluir_cabecalho,
                'incluirPartes': incluir_partes,
                'incluirEnderecos': incluir_enderecos,
                'incluirMovimentos': incluir_movimentos,
                'incluirDocumentos': incluir_documentos
            }
            
            # Adicionar datas se fornecidas
            if data_inicial:
                requisicao['dataInicial'] = data_inicial
            if data_final:
                requisicao['dataFinal'] = data_final
            
            # Adicionar parâmetros extras se fornecidos
            if parametros:
                requisicao['parametros'] = parametros
            
            # Log da requisição
            logger.info(f"Consultando processo: {numero_processo}")
            
            # Descobrir nome correto da operação
            operation_name = self._get_operation_name('consultarprocesso')
            logger.info(f"Usando operação: {operation_name}")
            
            # Realizar chamada SOAP
            service_method = getattr(self.client.service, operation_name)
            response = service_method(**requisicao)
            
            logger.info("Consulta realizada com sucesso")
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"Erro ao consultar processo: {str(e)}")
            
            # Tentar capturar resposta bruta para debug
            if hasattr(self, 'history') and self.history.last_received:
                try:
                    response_content = self.history.last_received['http_headers'].get('content', b'')
                    if not response_content and 'envelope' in self.history.last_received:
                        response_content = etree.tostring(self.history.last_received['envelope'], encoding='unicode')
                    
                    logger.error(f"Resposta recebida (primeiros 500 caracteres):")
                    logger.error(response_content[:500] if isinstance(response_content, str) else response_content.decode('utf-8', errors='ignore')[:500])
                except:
                    pass
            
            raise
    
    def consultar_documentos_processo(self, numero_processo, ids_documentos, parametros=None):
        """
        Consulta e baixa documentos de um processo judicial
        
        Args:
            numero_processo: Número do processo (20 dígitos sem formatação)
            ids_documentos: Lista de IDs dos documentos ou ID único (string)
            parametros: Lista de dicionários com parâmetros adicionais
            
        Returns:
            dict: Resposta contendo os documentos com seus conteúdos
        """
        try:
            # Preparar estrutura de autenticação
            autenticacao = {
                'autenticacaoSimples': {
                    'usuario': self.usuario,
                    'senha': self.senha
                }
            }
            
            # Garantir que ids_documentos seja uma lista
            if isinstance(ids_documentos, str):
                ids_documentos = [ids_documentos]
            
            # Preparar parâmetros da requisição
            requisicao = {
                'consultante': autenticacao,
                'numeroProcesso': numero_processo,
                'idDocumento': ids_documentos
            }
            
            # Adicionar parâmetros extras se fornecidos
            if parametros:
                requisicao['parametros'] = parametros
            
            # Log da requisição
            logger.info(f"Consultando documentos do processo: {numero_processo}")
            logger.info(f"IDs dos documentos: {ids_documentos}")
            
            # Descobrir nome correto da operação
            operation_name = self._get_operation_name('consultardocumentosprocesso')
            logger.info(f"Usando operação: {operation_name}")
            
            # Realizar chamada SOAP
            service_method = getattr(self.client.service, operation_name)
            response = service_method(**requisicao)
            
            logger.info("Documentos consultados com sucesso")
            
            # Processar resposta e extrair documentos
            return self._parse_documentos_response(response)
            
        except Exception as e:
            logger.error(f"Erro ao consultar documentos: {str(e)}")
            raise
    
    def _parse_documentos_response(self, response):
        """
        Processa a resposta de consulta de documentos e extrai anexos
        
        Args:
            response: Resposta do Zeep
            
        Returns:
            dict: Documentos processados com conteúdo extraído
        """
        from zeep.helpers import serialize_object
        
        try:
            # Serializar resposta
            resultado = serialize_object(response)
            
            # Extrair documentos
            documentos = []
            
            if 'documentos' in resultado:
                docs = resultado['documentos']
                
                # Se for um único documento, transformar em lista
                if isinstance(docs, dict):
                    docs = [docs]
                
                for doc in docs:
                    documento_info = {
                        'idDocumento': doc.get('idDocumento'),
                        'mimetype': doc.get('mimetype'),
                        'encoding': doc.get('encoding'),
                        'hash': doc.get('hash'),
                        'conteudo': None,
                        'conteudo_base64': None
                    }
                    
                    # Extrair conteúdo
                    if 'conteudo' in doc:
                        conteudo = doc['conteudo']
                        
                        # O conteúdo pode vir como bytes ou string base64
                        if isinstance(conteudo, bytes):
                            import base64
                            documento_info['conteudo'] = conteudo
                            documento_info['conteudo_base64'] = base64.b64encode(conteudo).decode('utf-8')
                        elif isinstance(conteudo, str):
                            documento_info['conteudo_base64'] = conteudo
                            try:
                                import base64
                                documento_info['conteudo'] = base64.b64decode(conteudo)
                            except:
                                documento_info['conteudo'] = conteudo.encode('utf-8')
                    
                    documentos.append(documento_info)
            
            return {
                'sucesso': True,
                'recibo': resultado.get('recibo'),
                'documentos': documentos
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta de documentos: {str(e)}")
            return {
                'sucesso': False,
                'erro': str(e),
                'resposta_bruta': serialize_object(response)
            }
    
    def _parse_response(self, response):
        """
        Converte a resposta SOAP em um dicionário Python
        
        Args:
            response: Resposta do Zeep
            
        Returns:
            dict: Resposta parseada
        """
        try:
            # Zeep já retorna objetos Python, mas vamos garantir serialização
            from zeep.helpers import serialize_object
            return serialize_object(response)
        except Exception as e:
            logger.warning(f"Erro ao serializar resposta: {str(e)}")
            return {'raw_response': str(response)}
    
    def consultar_processo_raw_xml(self, numero_processo, data_inicial=None, data_final=None,
                                   incluir_cabecalho=True, incluir_partes=False,
                                   incluir_enderecos=False, incluir_movimentos=True,
                                   incluir_documentos=True):
        """
        Retorna o XML bruto da requisição e resposta (útil para debug)
        
        Returns:
            dict: Contém 'request_xml' e 'response_xml'
        """
        from zeep.plugins import HistoryPlugin
        
        history = HistoryPlugin()
        
        # Criar novo cliente com plugin de histórico
        session = Session()
        session.verify = self.verify_ssl
        transport = Transport(session=session, timeout=30)
        settings = Settings(strict=False, xml_huge_tree=True)
        
        client = Client(self.wsdl_url, transport=transport, 
                       settings=settings, plugins=[history])
        
        # Preparar e executar requisição
        autenticacao = {
            'autenticacaoSimples': {
                'usuario': self.usuario,
                'senha': self.senha
            }
        }
        
        requisicao = {
            'consultante': autenticacao,
            'numeroProcesso': numero_processo,
            'incluirCabecalho': incluir_cabecalho,
            'incluirPartes': incluir_partes,
            'incluirEnderecos': incluir_enderecos,
            'incluirMovimentos': incluir_movimentos,
            'incluirDocumentos': incluir_documentos
        }
        
        if data_inicial:
            requisicao['dataInicial'] = data_inicial
        if data_final:
            requisicao['dataFinal'] = data_final
        
        try:
            # Descobrir operações do cliente temporário
            temp_operacoes = {}
            for service in client.wsdl.services.values():
                for port in service.ports.values():
                    for operation_name in port.binding._operations.keys():
                        temp_operacoes[operation_name.lower()] = operation_name
            
            # Encontrar operação correta
            operation_name = None
            for op_key, op_name in temp_operacoes.items():
                if 'consultar' in op_key and 'processo' in op_key:
                    operation_name = op_name
                    break
            
            if not operation_name:
                operation_name = list(temp_operacoes.values())[0]
            
            logger.info(f"Usando operação: {operation_name}")
            
            # Executar
            service_method = getattr(client.service, operation_name)
            service_method(**requisicao)
            
            # Capturar XMLs
            return {
                'request_xml': etree.tostring(history.last_sent['envelope'], 
                                             encoding='unicode', pretty_print=True),
                'response_xml': etree.tostring(history.last_received['envelope'], 
                                              encoding='unicode', pretty_print=True)
            }
        except Exception as e:
            logger.error(f"Erro ao obter XML: {str(e)}")
            if history.last_sent:
                return {
                    'request_xml': etree.tostring(history.last_sent['envelope'], 
                                                 encoding='unicode', pretty_print=True),
                    'error': str(e)
                }
            raise