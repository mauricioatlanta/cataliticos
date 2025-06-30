// Dashboard interactivo - Funciones adicionales
class DashboardController {
    constructor() {
        this.initializeRealTimeUpdates();
        this.initializeNotifications();
        this.initializePerformanceMetrics();
    }

    // Actualización en tiempo real
    initializeRealTimeUpdates() {
        setInterval(() => {
            this.updateMetrics();
        }, 30000); // Actualizar cada 30 segundos
    }

    // Sistema de notificaciones
    initializeNotifications() {
        this.checkLowStock();
        this.checkHighValueTransactions();
    }

    // Métricas de rendimiento
    initializePerformanceMetrics() {
        this.calculateConversionRate();
        this.calculateAverageTransactionValue();
    }

    updateMetrics() {
        fetch('/api/dashboard-metrics/')
            .then(response => response.json())
            .then(data => {
                this.updateCounters(data);
                this.showNotification('📊 Datos actualizados', 'success');
            })
            .catch(error => {
                console.error('Error updating metrics:', error);
            });
    }

    updateCounters(data) {
        const counters = document.querySelectorAll('.metric-value');
        counters.forEach((counter, index) => {
            this.animateCounter(counter, data.values[index]);
        });
    }

    animateCounter(element, targetValue) {
        const startValue = parseInt(element.textContent.replace(/[^\d]/g, ''));
        const duration = 1000;
        const startTime = Date.now();

        const updateCounter = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            
            element.textContent = this.formatNumber(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        requestAnimationFrame(updateCounter);
    }

    formatNumber(num) {
        return new Intl.NumberFormat('es-CL').format(num);
    }

    checkLowStock() {
        // Lógica para verificar stock bajo
        const lowStockItems = this.getLowStockItems();
        if (lowStockItems.length > 0) {
            this.showNotification(`⚠️ ${lowStockItems.length} items con stock bajo`, 'warning');
        }
    }

    checkHighValueTransactions() {
        // Verificar transacciones de alto valor
        const highValueThreshold = 100000;
        // Lógica de verificación...
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 1050;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }

    // Exportar datos
    exportDashboardData() {
        const data = this.collectDashboardData();
        const blob = new Blob([JSON.stringify(data, null, 2)], 
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard-data-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Inicializar el dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardController();
    
    // Agregar controles adicionales
    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn btn-outline-light position-fixed';
    exportBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1040;';
    exportBtn.innerHTML = '📊 Exportar';
    exportBtn.onclick = () => dashboard.exportDashboardData();
    document.body.appendChild(exportBtn);
});

// Configuración de temas
const themeController = {
    themes: {
        ocean: {
            primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            accent: '#FFD700'
        },
        sunset: {
            primary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            accent: '#FFE066'
        },
        forest: {
            primary: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            accent: '#7FFF00'
        }
    },
    
    applyTheme(themeName) {
        const theme = this.themes[themeName];
        if (theme) {
            document.querySelector('.dashboard-container').style.background = theme.primary;
            this.showNotification(`🎨 Tema "${themeName}" aplicado`, 'success');
        }
    }
};
