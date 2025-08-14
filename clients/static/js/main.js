/**
 * TOKOS - Main JavaScript File
 * Fonctionnalités principales du site e-commerce
 */

// Configuration globale
const TOKOS = {
    config: {
        animationSpeed: 300,
        autoSlideInterval: 5000,
        cartUpdateDelay: 500,
        searchDelay: 300
    },
    
    // État global de l'application
    state: {
        cartCount: 0,
        isLoading: false,
        currentPage: 'home'
    }
};

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🛒 Tokos E-commerce initialized');
    
    // Initialiser les modules
    CartModule.init();
    UIModule.init();
    NavigationModule.init();
    ModalModule.init();
    FormModule.init();
    
    // Détecter la page courante
    detectCurrentPage();
    
    // Initialiser les animations
    initAnimations();
    
    // Mettre à jour le compteur du panier
    updateCartCount();
    
    // Afficher la pop-up promotionnelle (avec délai)
    setTimeout(showPromoPopup, 3000);
});

// ==========================================================================
// CART MODULE
// ==========================================================================

const CartModule = {
    init() {
        this.bindEvents();
        this.loadCartFromStorage();
    },
    
    bindEvents() {
        // Boutons d'ajout au panier
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart-btn')) {
                this.handleAddToCart(e);
            }
        });
        
        // Mise à jour des quantités
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('qty-input')) {
                this.handleQuantityChange(e);
            }
        });
        
        // Suppression d'articles
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-item')) {
                this.handleRemoveItem(e);
            }
        });
    },
    
    handleAddToCart(event) {
        event.preventDefault();
        
        const button = event.target.closest('.add-to-cart-btn') || event.target;
        const form = button.closest('form');
        
        if (!form) return;
        
        // Animation du bouton
        this.animateButton(button, 'success');
        
        // Simulation d'ajout (en attendant la soumission du form)
        setTimeout(() => {
            this.updateCartCount(1);
            this.showAddedToCartNotification();
        }, 300);
    },
    
    handleQuantityChange(event) {
        const input = event.target;
        const itemId = input.dataset.itemId;
        const newQuantity = parseInt(input.value);
        
        if (newQuantity < 1) {
            input.value = 1;
            return;
        }
        
        // Debounce la mise à jour
        clearTimeout(input.updateTimeout);
        input.updateTimeout = setTimeout(() => {
            this.updateQuantity(itemId, newQuantity);
        }, TOKOS.config.cartUpdateDelay);
    },
    
    handleRemoveItem(event) {
        event.preventDefault();
        
        const button = event.target.closest('.remove-item');
        const itemId = button.dataset.itemId;
        
        // Confirmation
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) {
            return;
        }
        
        this.removeItem(itemId);
    },
    
    updateQuantity(itemId, quantity) {
        // Cette fonction sera appelée par les vues Django
        console.log(`Updating item ${itemId} to quantity ${quantity}`);
        
        // Animation de chargement
        const input = document.querySelector(`[data-item-id="${itemId}"]`);
        if (input) {
            input.disabled = true;
            setTimeout(() => input.disabled = false, 1000);
        }
    },
    
    removeItem(itemId) {
        const cartItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('.cart-item');
        
        if (cartItem) {
            // Animation de suppression
            cartItem.style.transform = 'translateX(-100%)';
            cartItem.style.opacity = '0';
            
            setTimeout(() => {
                cartItem.remove();
                this.updateCartCount(-1);
                this.updateCartTotals();
            }, TOKOS.config.animationSpeed);
        }
    },
    
    updateCartCount(change = 0) {
        TOKOS.state.cartCount += change;
        const cartBadge = document.getElementById('cart-count');
        
        if (cartBadge) {
            cartBadge.textContent = TOKOS.state.cartCount;
            
            // Animation du badge
            cartBadge.style.transform = 'scale(1.3)';
            setTimeout(() => {
                cartBadge.style.transform = 'scale(1)';
            }, 200);
        }
    },
    
    updateCartTotals() {
        // Recalculer les totaux du panier
        let subtotal = 0;
        const items = document.querySelectorAll('.cart-item');
        
        items.forEach(item => {
            const price = parseFloat(item.dataset.price || 0);
            const quantity = parseInt(item.querySelector('.qty-input').value || 0);
            subtotal += price * quantity;
        });
        
        // Mettre à jour l'affichage
        const subtotalElement = document.getElementById('subtotal');
        const totalElement = document.getElementById('total');
        const shipping = subtotal >= 25000 ? 0 : 2500;
        
        if (subtotalElement) {
            subtotalElement.textContent = `${subtotal.toLocaleString()} FCFA`;
        }
        
        if (totalElement) {
            totalElement.textContent = `${(subtotal + shipping).toLocaleString()} FCFA`;
        }
    },
    
    animateButton(button, type = 'success') {
        const originalContent = button.innerHTML;
        const originalClass = button.className;
        
        // Animation de succès
        if (type === 'success') {
            button.innerHTML = '<i class="fas fa-check me-1"></i>Ajouté !';
            button.className = button.className.replace(/btn-\w+/, 'btn-success');
            
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.className = originalClass;
            }, 2000);
        }
    },
    
    showAddedToCartNotification() {
        // Toast notification
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle me-2"></i>Produit ajouté au panier !
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    },
    
    loadCartFromStorage() {
        // Charger l'état du panier depuis le localStorage (si nécessaire)
        const savedCartCount = localStorage.getItem('tokos_cart_count');
        if (savedCartCount) {
            TOKOS.state.cartCount = parseInt(savedCartCount);
            this.updateCartCount(0); // Juste pour mettre à jour l'affichage
        }
    },
    
    saveCartToStorage() {
        localStorage.setItem('tokos_cart_count', TOKOS.state.cartCount);
    }
};

// ==========================================================================
// UI MODULE
// ==========================================================================

const UIModule = {
    init() {
        this.initScrollEffects();
        this.initImageLazyLoading();
        this.initTooltips();
        this.initSearchFunctionality();
        this.initThemeToggle();
    },
    
    initScrollEffects() {
        let lastScrollTop = 0;
        const navbar = document.querySelector('.navbar');
        
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Navbar hide/show on scroll
            if (navbar) {
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    navbar.style.transform = 'translateY(0)';
                }
            }
            
            lastScrollTop = scrollTop;
            
            // Parallax effect for hero section
            const heroSection = document.querySelector('.hero-section');
            if (heroSection && scrollTop < heroSection.offsetHeight) {
                heroSection.style.transform = `translateY(${scrollTop * 0.5}px)`;
            }
        });
    },
    
    initImageLazyLoading() {
        // Lazy loading pour les images
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    },
    
    initTooltips() {
        // Initialiser les tooltips Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    initSearchFunctionality() {
        const searchInput = document.querySelector('input[name="search"]');
        if (!searchInput) return;
        
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, TOKOS.config.searchDelay);
        });
    },
    
    performSearch(query) {
        if (query.length < 3) return;
        
        // Animation de chargement
        const searchIcon = document.querySelector('.search-icon');
        if (searchIcon) {
            searchIcon.className = 'fas fa-spinner fa-spin';
            setTimeout(() => {
                searchIcon.className = 'fas fa-search';
            }, 1000);
        }
        
        console.log(`Recherche: ${query}`);
    },
    
    initThemeToggle() {
        // Toggle dark mode (optionnel)
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                document.body.classList.toggle('dark-mode');
                localStorage.setItem('tokos_theme', 
                    document.body.classList.contains('dark-mode') ? 'dark' : 'light'
                );
            });
        }
        
        // Appliquer le thème sauvegardé
        const savedTheme = localStorage.getItem('tokos_theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        }
    }
};

// ==========================================================================
// NAVIGATION MODULE
// ==========================================================================

const NavigationModule = {
    init() {
        this.initMobileMenu();
        this.initActiveLinks();
        this.initSmoothScrolling();
    },
    
    initMobileMenu() {
        const mobileToggle = document.querySelector('.navbar-toggler');
        const mobileMenu = document.querySelector('.navbar-collapse');
        
        if (mobileToggle && mobileMenu) {
            // Fermer le menu mobile lors du clic sur un lien
            mobileMenu.addEventListener('click', (e) => {
                if (e.target.classList.contains('nav-link')) {
                    const collapse = new bootstrap.Collapse(mobileMenu);
                    collapse.hide();
                }
            });
        }
    },
    
    initActiveLinks() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    },
    
    initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
};

// ==========================================================================
// MODAL MODULE
// ==========================================================================

const ModalModule = {
    init() {
        this.bindModalEvents();
    },
    
    bindModalEvents() {
        // Événements pour les modales
        document.addEventListener('show.bs.modal', (e) => {
            console.log('Modal opening:', e.target.id);
        });
        
        document.addEventListener('hidden.bs.modal', (e) => {
            console.log('Modal closed:', e.target.id);
            // Nettoyer les formulaires
            const forms = e.target.querySelectorAll('form');
            forms.forEach(form => form.reset());
        });
    }
};

// ==========================================================================
// FORM MODULE
// ==========================================================================

const FormModule = {
    init() {
        this.initFormValidation();
        this.initFormSubmission();
    },
    
    initFormValidation() {
        const forms = document.querySelectorAll('form[novalidate]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },
    
    initFormSubmission() {
        // Gérer les soumissions AJAX
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('ajax-form')) {
                e.preventDefault();
                this.submitFormAjax(form);
            }
        });
    },
    
    submitFormAjax(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // État de chargement
        if (submitBtn) {
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Chargement...';
            
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 2000);
        }
        
        console.log('Form submitted via AJAX');
    }
};

// ==========================================================================
// UTILITY FUNCTIONS
// ==========================================================================

function detectCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('/produits/')) TOKOS.state.currentPage = 'products';
    else if (path.includes('/promotions/')) TOKOS.state.currentPage = 'promotions';
    else if (path.includes('/panier/')) TOKOS.state.currentPage = 'cart';
    else if (path.includes('/mon-compte/')) TOKOS.state.currentPage = 'account';
    else TOKOS.state.currentPage = 'home';
    
    document.body.classList.add(`page-${TOKOS.state.currentPage}`);
}

function initAnimations() {
    // Animation d'entrée pour les cartes
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.product-card, .category-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });
}

function updateCartCount() {
    // Récupérer le nombre d'articles dans le panier depuis le serveur
    // Cette fonction sera appelée au chargement de la page
    const cartItems = document.querySelectorAll('.cart-item').length;
    TOKOS.state.cartCount = cartItems;
    
    const cartBadge = document.getElementById('cart-count');
    if (cartBadge) {
        cartBadge.textContent = cartItems;
    }
}
