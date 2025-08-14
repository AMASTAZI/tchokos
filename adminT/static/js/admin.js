// static/admin/js/admin.js

document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Confirmation dialogs
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Êtes-vous sûr ?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // CSRF Token setup for AJAX requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    // Gestion du modal "Casser le prix"
    const appliquerReductionBtn = document.getElementById('appliquerReduction');
    if (appliquerReductionBtn) {
        appliquerReductionBtn.addEventListener('click', function() {
            const produitId = document.getElementById('produitId').value;
            const pourcentage = document.getElementById('pourcentageReduction').value;
            const nouveauPrix = document.getElementById('nouveauPrix').value;
            
            if (!pourcentage && !nouveauPrix) {
                alert('Veuillez entrer soit un pourcentage soit un nouveau prix');
                return;
            }
            
            const data = { produit_id: produitId };
            if (pourcentage) {
                data.pourcentage = parseInt(pourcentage);
            } else {
                data.nouveau_prix = parseFloat(nouveauPrix);
            }
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> Application...';
            this.disabled = true;
            
            fetch(`/admin/produits/casser-prix/${produitId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the price in the table
                    const row = document.querySelector(`tr[data-produit-id="${produitId}"]`);
                    if (row) {
                        const prixCell = row.querySelector('td:nth-child(4)');
                        prixCell.textContent = data.nouveau_prix.toLocaleString('fr-FR');
                        
                        const promotionCell = row.querySelector('td:nth-child(7)');
                        promotionCell.innerHTML = `<span class="badge bg-info"><i class="fas fa-percentage"></i> ${data.pourcentage}%</span>`;
                    }
                    
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('casserPrixModal'));
                    modal.hide();
                    
                    // Show success message
                    showAlert('success', 'Prix cassé avec succès !');
                } else {
                    showAlert('danger', 'Erreur lors de la modification du prix');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Une erreur est survenue');
            })
            .finally(() => {
                // Reset button state
                this.innerHTML = originalText;
                this.disabled = false;
            });
        });
    }
    
    // Changer le statut des commandes
    const statutSelect = document.querySelectorAll('.statut-select');
    statutSelect.forEach(select => {
        select.addEventListener('change', function() {
            const commandeId = this.getAttribute('data-commande-id');
            const nouveauStatut = this.value;
            
            const formData = new FormData();
            formData.append('statut', nouveauStatut);
            
            fetch(`/admin/commandes/statut/${commandeId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Statut mis à jour avec succès');
                    // Update the status badge
                    const badge = this.closest('tr').querySelector('.status-badge');
                    if (badge) {
                        badge.className = 'badge status-badge ' + getStatusBadgeClass(nouveauStatut);
                        badge.textContent = getStatusText(nouveauStatut);
                    }
                } else {
                    showAlert('danger', 'Erreur lors de la mise à jour');
                    // Reset select to original value
                    this.value = this.getAttribute('data-original-value');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Une erreur est survenue');
                this.value = this.getAttribute('data-original-value');
            });
        });
    });
    
    // Fonction pour afficher les alertes
    function showAlert(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the main content
        const mainContent = document.querySelector('.container-fluid');
        mainContent.insertBefore(alertContainer, mainContent.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
    
    // Helper functions for status
    function getStatusBadgeClass(status) {
        switch(status) {
            case 'en_attente': return 'bg-warning text-dark';
            case 'en_cours': return 'bg-info';
            case 'livre': return 'bg-success';
            case 'annule': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }
    
    function getStatusText(status) {
        switch(status) {
            case 'en_attente': return 'En attente';
            case 'en_cours': return 'En cours';
            case 'livre': return 'Livré';
            case 'annule': return 'Annulé';
            default: return status;
        }
    }
    
    // DataTable-like functionality for tables
    function initTableFeatures(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-column');
                const currentSort = this.getAttribute('data-sort') || 'asc';
                const newSort = currentSort === 'asc' ? 'desc' : 'asc';
                
                // Reset all headers
                headers.forEach(h => {
                    h.removeAttribute('data-sort');
                    h.querySelector('.sort-icon')?.remove();
                });
                
                // Set new sort
                this.setAttribute('data-sort', newSort);
                const icon = document.createElement('i');
                icon.className = `fas fa-sort-${newSort === 'asc' ? 'up' : 'down'} ms-2 sort-icon`;
                this.appendChild(icon);
                
                // Sort table
                sortTable(table, column, newSort === 'asc');
            });
        });
    }
    
    function sortTable(table, column, ascending) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.querySelector(`[data-value="${column}"]`)?.textContent || 
                        a.cells[parseInt(column)]?.textContent || '';
            const bVal = b.querySelector(`[data-value="${column}"]`)?.textContent || 
                        b.cells[parseInt(column)]?.textContent || '';
            
            if (ascending) {
                return aVal.localeCompare(bVal, 'fr', { numeric: true });
            } else {
                return bVal.localeCompare(aVal, 'fr', { numeric: true });
            }
        });
        
        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
    
    // Initialize table features for products table
    initTableFeatures('produitsTable');
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Image preview functionality
    const imageInputs = document.querySelectorAll('input[type="file"][data-preview]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            const previewId = this.getAttribute('data-preview');
            const preview = document.getElementById(previewId);
            
            if (file && preview) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Bulk actions
    const bulkCheckbox = document.getElementById('bulk-select-all');
    const itemCheckboxes = document.querySelectorAll('.bulk-select-item');
    const bulkActions = document.getElementById('bulk-actions');
    
    if (bulkCheckbox) {
        bulkCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            toggleBulkActions();
        });
    }
    
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', toggleBulkActions);
    });
    
    function toggleBulkActions() {
        const checkedItems = document.querySelectorAll('.bulk-select-item:checked');
        if (bulkActions) {
            bulkActions.style.display = checkedItems.length > 0 ? 'block' : 'none';
        }
        
        // Update bulk select all checkbox
        if (bulkCheckbox) {
            bulkCheckbox.indeterminate = checkedItems.length > 0 && checkedItems.length < itemCheckboxes.length;
            bulkCheckbox.checked = checkedItems.length === itemCheckboxes.length && itemCheckboxes.length > 0;
        }
    }
    
    // Statistics animation
    const statsNumbers = document.querySelectorAll('[data-animate-number]');
    statsNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent);
        const duration = 2000;
        const increment = finalValue / (duration / 16);
        let currentValue = 0;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                element.textContent = finalValue.toLocaleString('fr-FR');
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(currentValue).toLocaleString('fr-FR');
            }
        }, 16);
    });
    
    // Responsive sidebar for mobile
    function handleResponsiveSidebar() {
        if (window.innerWidth <= 768) {
            sidebar?.classList.add('collapsed');
            mainContent?.classList.add('expanded');
        } else {
            sidebar?.classList.remove('collapsed');
            mainContent?.classList.remove('expanded');
        }
    }
    
    window.addEventListener('resize', handleResponsiveSidebar);
    handleResponsiveSidebar();
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                modalInstance?.hide();
            }
        }
    });
    
    // Initialize tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});