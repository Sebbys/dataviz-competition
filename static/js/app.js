// Enhanced JavaScript for Pacific Economy Dashboard
class DashboardApp {
    constructor() {
        this.init();
    }

    init() {
        this.initializeElements();
        this.bindEvents();
        this.initializeTooltips();
        this.loadSavedSelections();
    }

    initializeElements() {
        this.categorySelect = document.getElementById('category-select');
        this.indicatorSelect = document.getElementById('indicator-select');
        this.form = document.getElementById('visualization-form');
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabPanes = document.querySelectorAll('.tab-pane');
        this.loadingOverlay = this.createLoadingOverlay();
    }

    bindEvents() {
        // Category change handler
        this.categorySelect?.addEventListener('change', (e) => {
            this.handleCategoryChange(e.target.value);
        });

        // Form submission handler
        this.form?.addEventListener('submit', (e) => {
            this.handleFormSubmission(e);
        });

        // Tab navigation
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                this.switchTab(targetTab);
                this.saveTabSelection(targetTab);
            });
        });

        // Keyboard navigation for tabs
        document.addEventListener('keydown', (e) => {
            if (e.key >= '1' && e.key <= '3' && e.ctrlKey) {
                e.preventDefault();
                const tabIndex = parseInt(e.key) - 1;
                const tabs = ['statistical', 'geographical', 'time'];
                if (tabs[tabIndex]) {
                    this.switchTab(tabs[tabIndex]);
                }
            }
        });

        // Auto-save form data
        [this.categorySelect, this.indicatorSelect].forEach(element => {
            element?.addEventListener('change', () => {
                this.saveFormSelections();
            });
        });
    }

    handleCategoryChange(selectedCategory) {
        this.populateIndicators(selectedCategory);
        this.indicatorSelect.value = '';
        this.removeErrorMessages();
        
        // Auto-switch to appropriate tab
        const categoryTabMap = {
            'economy': 'statistical',
            'work': 'statistical',
            'trade_resources': 'geographical',
            'social_growth': 'time'
        };
        
        if (categoryTabMap[selectedCategory]) {
            this.switchTab(categoryTabMap[selectedCategory]);
        }
    }

    populateIndicators(selectedCategory) {
        if (!window.categoriesData || !this.indicatorSelect) return;
        
        this.indicatorSelect.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Choose an indicator...';
        defaultOption.disabled = true;
        defaultOption.selected = true;
        this.indicatorSelect.appendChild(defaultOption);
        
        const indicators = window.categoriesData[selectedCategory]?.indicators || {};
        
        Object.entries(indicators).forEach(([code, name]) => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name;
            this.indicatorSelect.appendChild(option);
        });
        
        // Trigger change event for validation
        this.indicatorSelect.dispatchEvent(new Event('change'));
    }

    handleFormSubmission(e) {
        if (!this.validateForm()) {
            e.preventDefault();
            return false;
        }

        this.showLoadingState();
        this.saveFormSelections();
        
        // Auto-scroll to results after a delay
        setTimeout(() => {
            this.scrollToResults();
        }, 1000);
    }

    validateForm() {
        const category = this.categorySelect?.value;
        const indicator = this.indicatorSelect?.value;
        
        this.removeErrorMessages();
        
        if (!category || !indicator) {
            this.showError('Please select both a category and an indicator.');
            return false;
        }
        
        return true;
    }

    showError(message) {
        this.removeErrorMessages();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-shake';
        errorDiv.innerHTML = `
            <div class="flex items-center">
                <i data-lucide="alert-circle" class="w-5 h-5 text-red-600 mr-2"></i>
                <p class="text-red-800 font-medium">${message}</p>
                <button class="ml-auto text-red-600 hover:text-red-800" onclick="this.parentElement.parentElement.remove()">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        
        this.form.appendChild(errorDiv);
        lucide.createIcons();
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv?.remove();
        }, 5000);
    }

    removeErrorMessages() {
        const errors = document.querySelectorAll('.error-message');
        errors.forEach(error => error.remove());
    }

    switchTab(targetTab) {
        this.tabButtons.forEach(btn => btn.classList.remove('active'));
        this.tabPanes.forEach(pane => pane.classList.remove('active'));

        const targetButton = document.querySelector(`[data-tab="${targetTab}"]`);
        const targetPane = document.getElementById(targetTab);

        if (targetButton && targetPane) {
            targetButton.classList.add('active');
            targetPane.classList.add('active');
            
            // Trigger a custom event for analytics or other purposes
            window.dispatchEvent(new CustomEvent('tabChanged', { 
                detail: { tab: targetTab } 
            }));
        }
    }

    showLoadingState() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i data-lucide="loader-2" class="inline w-5 h-5 mr-2 animate-spin"></i>Generating Visualizations...';
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75');
        }
        
        document.body.appendChild(this.loadingOverlay);
    }

    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="bg-white p-8 rounded-lg shadow-xl">
                <div class="flex items-center">
                    <div class="spinner mr-4"></div>
                    <div>
                        <h3 class="text-lg font-semibold">Generating Visualizations</h3>
                        <p class="text-gray-600">Please wait while we process your data...</p>
                    </div>
                </div>
            </div>
        `;
        return overlay;
    }

    scrollToResults() {
        const tabContainer = document.querySelector('.tab-container');
        if (tabContainer) {
            tabContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }

    saveFormSelections() {
        if (typeof Storage !== "undefined") {
            localStorage.setItem('selectedCategory', this.categorySelect?.value || '');
            localStorage.setItem('selectedIndicator', this.indicatorSelect?.value || '');
        }
    }

    saveTabSelection(tab) {
        if (typeof Storage !== "undefined") {
            localStorage.setItem('activeTab', tab);
        }
    }

    loadSavedSelections() {
        if (typeof Storage !== "undefined") {
            const savedCategory = localStorage.getItem('selectedCategory');
            const savedIndicator = localStorage.getItem('selectedIndicator');
            const savedTab = localStorage.getItem('activeTab');

            if (savedCategory && this.categorySelect) {
                this.categorySelect.value = savedCategory;
                this.populateIndicators(savedCategory);
            }

            if (savedIndicator && this.indicatorSelect) {
                // Wait a bit for indicators to populate
                setTimeout(() => {
                    this.indicatorSelect.value = savedIndicator;
                }, 100);
            }

            if (savedTab) {
                this.switchTab(savedTab);
            }
        }
    }

    initializeTooltips() {
        // Add tooltips to various elements
        const tooltipElements = [
            { selector: '[data-tooltip]', attr: 'data-tooltip' },
            { selector: '.form-select', text: 'Use keyboard arrows to navigate options' },
            { selector: '.tab-button', text: 'Use Ctrl+1,2,3 for quick navigation' }
        ];

        tooltipElements.forEach(({ selector, attr, text }) => {
            document.querySelectorAll(selector).forEach(element => {
                const tooltipText = attr ? element.getAttribute(attr) : text;
                if (tooltipText) {
                    element.title = tooltipText;
                }
            });
        });
    }
}

// Utility functions
const utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    formatNumber(num) {
        if (typeof num !== 'number') return num;
        return new Intl.NumberFormat().format(num);
    },

    copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!');
        }
    },

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        } text-white`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardApp = new DashboardApp();
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Add some CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .animate-shake {
            animation: shake 0.5s ease-in-out;
        }
        
        .animate-spin {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .transition-all {
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('Dashboard Error:', e.error);
    utils.showToast('An unexpected error occurred. Please refresh the page.', 'error');
});

// Export for external use
window.DashboardUtils = utils;
