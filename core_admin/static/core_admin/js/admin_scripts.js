// ===== PONTI Admin - JavaScript Functions =====

document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
});

function initializeAdmin() {
    // Initialize sidebar state
    handleSidebarState();
    
    // Initialize accordions
    initializeAccordions();
    
    // Initialize theme
    initializeTheme();
    
    // Initialize auto-dismiss messages
    initializeMessages();
    
    // Initialize form enhancements
    initializeForms();
    
    // Initialize tooltips
    initializeTooltips();
}

// ===== SIDEBAR FUNCTIONS =====

function toggleSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const main = document.querySelector('.admin-main');
    
    if (window.innerWidth <= 1024) {
        // Mobile behavior
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
    } else {
        // Desktop behavior - could implement collapse functionality
        console.log('Desktop sidebar toggle - feature can be implemented');
    }
}

function handleSidebarState() {
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        const sidebar = document.getElementById('adminSidebar');
        const toggleButton = document.querySelector('.sidebar-toggle');
        
        if (window.innerWidth <= 1024 && 
            sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !toggleButton.contains(e.target)) {
            toggleSidebar();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const sidebar = document.getElementById('adminSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (window.innerWidth > 1024) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

// ===== ACCORDION FUNCTIONS =====

function toggleAccordion(headerElement) {
    const content = headerElement.nextElementSibling;
    const icon = headerElement.querySelector('.nav-accordion-icon');
    
    // Toggle active class on header
    headerElement.classList.toggle('active');
    
    // Toggle content visibility
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        content.style.maxHeight = '0';
    } else {
        content.classList.add('active');
        content.style.maxHeight = content.scrollHeight + 'px';
    }
    
    // Store accordion state in localStorage
    const accordionId = headerElement.textContent.trim();
    const isOpen = headerElement.classList.contains('active');
    localStorage.setItem(`accordion-${accordionId}`, isOpen);
}

function initializeAccordions() {
    // Restore accordion states from localStorage
    const accordionHeaders = document.querySelectorAll('.nav-accordion-header');
    accordionHeaders.forEach(header => {
        const accordionId = header.textContent.trim();
        const savedState = localStorage.getItem(`accordion-${accordionId}`);
        
        if (savedState === 'true') {
            const content = header.nextElementSibling;
            header.classList.add('active');
            content.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    });
}

// ===== THEME FUNCTIONS =====

function initializeTheme() {
    const savedTheme = localStorage.getItem('ponti-admin-theme') || 'light';
    setTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ponti-admin-theme', theme);
    
    // Update theme toggle icon
    const themeIcon = document.querySelector('.header-btn i.fa-moon, .header-btn i.fa-sun');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// ===== MESSAGE FUNCTIONS =====

function initializeMessages() {
    // Auto-dismiss messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            dismissMessage(message);
        }, 5000);
    });
}

function dismissMessage(messageElement) {
    if (messageElement) {
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            messageElement.remove();
        }, 300);
    }
}

function showMessage(type, text) {
    const container = document.querySelector('.messages-container') || createMessageContainer();
    
    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.innerHTML = `
        <div class="message-content">
            <i class="fas fa-${getMessageIcon(type)}"></i>
            <span>${text}</span>
            <button type="button" class="message-close" onclick="dismissMessage(this.parentElement.parentElement)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    container.appendChild(message);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        dismissMessage(message);
    }, 5000);
}

function createMessageContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    
    const content = document.querySelector('.admin-content');
    content.insertBefore(container, content.firstChild);
    
    return container;
}

function getMessageIcon(type) {
    const icons = {
        success: 'check-circle',
        warning: 'exclamation-triangle',
        error: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ===== FORM ENHANCEMENTS =====

function initializeForms() {
    // Add loading states to submit buttons
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                addLoadingState(submitBtn);
            }
        });
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        autoResizeTextarea(textarea);
        textarea.addEventListener('input', () => autoResizeTextarea(textarea));
    });
    
    // File input enhancements
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        enhanceFileInput(input);
    });
}

function addLoadingState(button) {
    const originalText = button.textContent;
    const originalHTML = button.innerHTML;
    
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
    
    // Remove loading state after 10 seconds (fallback)
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalHTML;
    }, 10000);
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 100) + 'px';
}

function enhanceFileInput(input) {
    const wrapper = document.createElement('div');
    wrapper.className = 'file-input-wrapper';
    
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    
    const label = document.createElement('label');
    label.className = 'file-input-label';
    label.innerHTML = '<i class="fas fa-upload"></i> Escolher arquivo';
    label.setAttribute('for', input.id);
    
    wrapper.appendChild(label);
    
    input.addEventListener('change', function() {
        const fileName = input.files[0]?.name || 'Nenhum arquivo selecionado';
        label.innerHTML = `<i class="fas fa-file"></i> ${fileName}`;
    });
}

// ===== TOOLTIP FUNCTIONS =====

function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(element => {
        createTooltip(element);
    });
}

function createTooltip(element) {
    let tooltip;
    
    element.addEventListener('mouseenter', function() {
        tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = element.getAttribute('title');
        document.body.appendChild(tooltip);
        
        // Remove title to prevent default tooltip
        element.removeAttribute('title');
        element.setAttribute('data-tooltip', tooltip.textContent);
        
        // Position tooltip
        positionTooltip(element, tooltip);
    });
    
    element.addEventListener('mouseleave', function() {
        if (tooltip) {
            tooltip.remove();
            tooltip = null;
        }
        
        // Restore title
        element.setAttribute('title', element.getAttribute('data-tooltip'));
    });
}

function positionTooltip(element, tooltip) {
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let top = rect.top - tooltipRect.height - 8;
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    
    // Adjust if tooltip goes off screen
    if (top < 0) {
        top = rect.bottom + 8;
        tooltip.classList.add('tooltip-bottom');
    }
    
    if (left < 0) {
        left = 8;
    } else if (left + tooltipRect.width > window.innerWidth) {
        left = window.innerWidth - tooltipRect.width - 8;
    }
    
    tooltip.style.top = top + window.scrollY + 'px';
    tooltip.style.left = left + 'px';
}

// ===== UTILITY FUNCTIONS =====

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showMessage('success', 'Copiado para a área de transferência!');
    }).catch(() => {
        showMessage('error', 'Erro ao copiar para a área de transferência.');
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== AJAX HELPERS =====

function makeAjaxRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    const config = { ...defaults, ...options };
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Ajax request failed:', error);
            showMessage('error', 'Erro na requisição. Tente novamente.');
            throw error;
        });
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// ===== CHARTS AND GRAPHS =====

function createSimpleChart(canvasId, data, options = {}) {
    // Simple chart implementation without external libraries
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Simple bar chart implementation
    if (data.type === 'bar') {
        drawBarChart(ctx, data, width, height, options);
    }
}

function drawBarChart(ctx, data, width, height, options) {
    const padding = 40;
    const chartWidth = width - (padding * 2);
    const chartHeight = height - (padding * 2);
    const barWidth = chartWidth / data.labels.length;
    const maxValue = Math.max(...data.values);
    
    // Draw bars
    data.values.forEach((value, index) => {
        const barHeight = (value / maxValue) * chartHeight;
        const x = padding + (index * barWidth) + (barWidth * 0.1);
        const y = height - padding - barHeight;
        const w = barWidth * 0.8;
        
        // Draw bar
        ctx.fillStyle = options.color || '#3b82f6';
        ctx.fillRect(x, y, w, barHeight);
        
        // Draw label
        ctx.fillStyle = '#374151';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(data.labels[index], x + w/2, height - padding + 20);
        
        // Draw value
        ctx.fillText(value, x + w/2, y - 10);
    });
}

// ===== KEYBOARD SHORTCUTS =====

document.addEventListener('keydown', function(e) {
    // Ctrl+/ or Cmd+/ - Toggle sidebar
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        toggleSidebar();
    }
    
    // Ctrl+Shift+D or Cmd+Shift+D - Toggle dark mode
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Escape - Close modals/dropdowns
    if (e.key === 'Escape') {
        // Close sidebar on mobile
        if (window.innerWidth <= 1024) {
            const sidebar = document.getElementById('adminSidebar');
            if (sidebar.classList.contains('open')) {
                toggleSidebar();
            }
        }
    }
});

// ===== PERFORMANCE MONITORING =====

function trackPageLoad() {
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Página carregada em ${loadTime}ms`);
        
        // Could send to analytics service
        if (loadTime > 3000) {
            console.warn('Página carregou lentamente');
        }
    });
}

// Initialize performance monitoring
trackPageLoad();

// ===== EXPORT FUNCTIONS FOR EXTERNAL USE =====

window.PontiAdmin = {
    toggleSidebar,
    toggleAccordion,
    toggleTheme,
    showMessage,
    dismissMessage,
    confirmAction,
    copyToClipboard,
    makeAjaxRequest,
    createSimpleChart
};