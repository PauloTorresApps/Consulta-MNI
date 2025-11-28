// Função para fechar alertas automaticamente após 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Formatação de número do processo
function formatarNumeroProcesso(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Limitar a 20 dígitos
    if (value.length > 20) {
        value = value.substr(0, 20);
    }
    
    input.value = value;
}

// Validação de formulário
function validarFormulario(form) {
    const numeroProcesso = form.querySelector('#numero_processo');
    
    if (numeroProcesso) {
        const numero = numeroProcesso.value.replace(/\D/g, '');
        
        if (numero.length !== 20) {
            alert('O número do processo deve ter exatamente 20 dígitos!');
            numeroProcesso.focus();
            return false;
        }
    }
    
    return true;
}

// Adicionar listener para todos os formulários
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!validarFormulario(form)) {
                e.preventDefault();
            }
        });
    });
});

// Loading spinner durante requisições
function mostrarLoading() {
    const loading = document.createElement('div');
    loading.id = 'loading-overlay';
    loading.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Consultando processo...</p>
        </div>
    `;
    
    // Adicionar estilos
    const style = document.createElement('style');
    style.textContent = `
        #loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .loading-spinner {
            text-align: center;
            color: white;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(loading);
}

function esconderLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.remove();
    }
}

// Adicionar loading aos formulários
document.addEventListener('DOMContentLoaded', function() {
    const consultaForms = document.querySelectorAll('form[action*="consultar"]');
    
    consultaForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (validarFormulario(form)) {
                mostrarLoading();
            }
        });
    });
});

// Função para fazer scroll suave
function scrollSuave(elemento) {
    elemento.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Copiar texto para área de transferência
function copiarTexto(texto) {
    return navigator.clipboard.writeText(texto).then(function() {
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
        return sucesso;
    });
}

// Mostrar notificação toast
function mostrarToast(mensagem, tipo = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensagem;
    
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            padding: 1rem 1.5rem;
            background-color: #1e293b;
            color: white;
            border-radius: 0.375rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        }
        
        .toast-success {
            background-color: #10b981;
        }
        
        .toast-error {
            background-color: #ef4444;
        }
        
        .toast-warning {
            background-color: #f59e0b;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    
    if (!document.querySelector('style[data-toast]')) {
        style.setAttribute('data-toast', 'true');
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}

// Prevenir múltiplos submits
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        let submitted = false;
        
        form.addEventListener('submit', function(e) {
            if (submitted) {
                e.preventDefault();
                return false;
            }
            
            const submitButtons = form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach(function(btn) {
                btn.disabled = true;
                btn.style.opacity = '0.6';
            });
            
            submitted = true;
        });
    });
});

// Console easter egg
console.log('%c⚖️ Sistema de Consulta SOAP - MNI', 'font-size: 20px; font-weight: bold; color: #2563eb;');
console.log('%cDesenvolvido com Python + Flask', 'font-size: 14px; color: #64748b;');
console.log('%c\nPara mais informações, visite /sobre', 'font-size: 12px; color: #10b981;');
