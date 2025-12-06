/**
 * Sistema de Consulta SOAP - MNI
 * JavaScript principal com suporte ao AdminLTE 4
 */

// Inicialização quando o documento estiver pronto
$(document).ready(function() {
    // Auto-dismiss alerts após 5 segundos
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
    
    // Formatação de número do processo em tempo real
    $('#numero_processo, #debug_numero_processo').on('input', function() {
        let value = $(this).val().replace(/\D/g, '');
        
        // Limitar a 20 dígitos
        if (value.length > 20) {
            value = value.substr(0, 20);
        }
        
        $(this).val(value);
    });
    
    // Prevenir múltiplos submits
    $('form').on('submit', function() {
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        
        if ($form.data('submitted') === true) {
            return false;
        }
        
        $form.data('submitted', true);
        $submitBtn.prop('disabled', true).css('opacity', '0.6');
        
        // Re-habilitar após 5 segundos (caso de erro)
        setTimeout(function() {
            $form.data('submitted', false);
            $submitBtn.prop('disabled', false).css('opacity', '1');
        }, 5000);
    });
});

// Função para validar formulário de consulta
function validarFormularioConsulta(form) {
    const numeroProcesso = $(form).find('#numero_processo').val().replace(/\D/g, '');
    
    if (!numeroProcesso) {
        mostrarAlerta('Erro', 'Informe o número do processo', 'error');
        return false;
    }
    
    if (numeroProcesso.length !== 20) {
        mostrarAlerta('Erro', 'O número do processo deve ter exatamente 20 dígitos', 'error');
        return false;
    }
    
    return true;
}

// Função para mostrar alertas usando SweetAlert2
function mostrarAlerta(titulo, texto, icone = 'info') {
    Swal.fire({
        icon: icone,
        title: titulo,
        text: texto,
        confirmButtonColor: '#007bff'
    });
}

// Função para mostrar toast de sucesso
function mostrarToast(mensagem, tipo = 'success') {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });
    
    Toast.fire({
        icon: tipo,
        title: mensagem
    });
}

// Função para copiar texto para área de transferência
function copiarTexto(texto) {
    return navigator.clipboard.writeText(texto).then(function() {
        mostrarToast('Copiado para área de transferência!', 'success');
        return true;
    }).catch(function() {
        // Fallback para navegadores antigos
        const textarea = document.createElement('textarea');
        textarea.value = texto;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        const sucesso = document.execCommand('copy');
        document.body.removeChild(textarea);
        
        if (sucesso) {
            mostrarToast('Copiado para área de transferência!', 'success');
        }
        
        return sucesso;
    });
}

// Função para scroll suave
function scrollSuave(elemento) {
    if (typeof elemento === 'string') {
        elemento = document.querySelector(elemento);
    }
    
    if (elemento) {
        elemento.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Função para mostrar loading overlay
function mostrarLoading(mensagem = 'Carregando...') {
    Swal.fire({
        title: mensagem,
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

// Função para esconder loading
function esconderLoading() {
    Swal.close();
}

// Função para formatar número do processo (adicionar máscara)
function formatarNumeroProcesso(numero) {
    // Remove tudo que não é dígito
    numero = numero.replace(/\D/g, '');
    
    // Formata: NNNNNNN-DD.AAAA.J.TR.OOOO
    if (numero.length === 20) {
        return numero.replace(
            /(\d{7})(\d{2})(\d{4})(\d{1})(\d{2})(\d{4})/,
            '$1-$2.$3.$4.$5.$6'
        );
    }
    
    return numero;
}

// Função para validar data
function validarData(data) {
    if (!data) return true;
    
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(data)) return false;
    
    const dataObj = new Date(data);
    return dataObj instanceof Date && !isNaN(dataObj);
}

// Função para exportar dados como JSON
function exportarJSON(dados, nomeArquivo = 'dados.json') {
    const json = JSON.stringify(dados, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = nomeArquivo;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    mostrarToast('Arquivo JSON exportado com sucesso!', 'success');
}

// Função para imprimir página
function imprimirPagina() {
    window.print();
}

// Debugging helper
function debugLog(mensagem, dados) {
    if (console && console.log) {
        console.log(`[Debug] ${mensagem}`, dados || '');
    }
}

// Console easter egg
console.log('%c⚖️ Sistema de Consulta SOAP - MNI', 'font-size: 20px; font-weight: bold; color: #007bff;');
console.log('%c🚀 Desenvolvido com Python + Flask + AdminLTE 4', 'font-size: 14px; color: #6c757d;');
console.log('%c📚 Para mais informações, visite /sobre', 'font-size: 12px; color: #28a745;');
console.log('%c💡 Dica: Use o modo Debug XML para visualizar as requisições SOAP', 'font-size: 11px; color: #17a2b8;');