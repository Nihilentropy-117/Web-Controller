// API Base URL
const API_BASE = '/api';

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Load all modules
async function loadModules() {
    const container = document.getElementById('modules-container');

    try {
        const response = await fetch(`${API_BASE}/modules`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to load modules');
        }

        if (data.modules.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <h2 class="empty-state-title">No Modules Found</h2>
                    <p class="empty-state-description">
                        Add Python modules to the <code>modules/</code> directory to get started.
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        data.modules.forEach(module => {
            const moduleCard = createModuleCard(module);
            container.appendChild(moduleCard);
        });

    } catch (error) {
        console.error('Error loading modules:', error);
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h2 class="empty-state-title">Error Loading Modules</h2>
                <p class="empty-state-description">${error.message}</p>
            </div>
        `;
        showToast('Failed to load modules', 'error');
    }
}

// Create module card HTML
function createModuleCard(module) {
    const card = document.createElement('div');
    card.className = 'module-card';
    card.style.setProperty('--module-color', module.color);

    // Build status section (excluding fields and actions which are handled separately)
    let statusItems = {};
    if (module.status && typeof module.status === 'object') {
        statusItems = Object.entries(module.status).filter(([key]) =>
            key !== 'fields' && key !== 'actions'
        );
    }

    const statusHTML = statusItems.length > 0
        ? `
            <div class="module-status">
                <div class="status-grid">
                    ${statusItems.map(([key, value]) => {
                        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        let displayValue = value;

                        // Handle different value types
                        if (typeof value === 'boolean') {
                            displayValue = `<span class="status-badge ${value ? 'success' : 'danger'}">${value ? 'Yes' : 'No'}</span>`;
                        } else if (key.toLowerCase().includes('status')) {
                            const statusClass = value.toLowerCase() === 'running' || value.toLowerCase() === 'active' ? 'success' :
                                              value.toLowerCase() === 'stopped' || value.toLowerCase() === 'inactive' ? 'danger' : 'warning';
                            displayValue = `<span class="status-badge ${statusClass}">${value}</span>`;
                        }

                        return `
                            <div class="status-item">
                                <span class="status-label">${formattedKey}</span>
                                <span class="status-value">${displayValue}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `
        : '';

    // Build form fields section
    const fields = module.status && module.status.fields ? module.status.fields : [];
    const fieldsHTML = fields.length > 0
        ? `
            <div class="module-fields">
                ${fields.map(field => `
                    <div class="field-group">
                        <label class="field-label" for="${module.id}-${field.id}">${field.label}</label>
                        <input
                            type="${field.type || 'text'}"
                            id="${module.id}-${field.id}"
                            class="field-input"
                            placeholder="${field.placeholder || ''}"
                            value="${field.value || ''}"
                            data-field-id="${field.id}"
                        />
                    </div>
                `).join('')}
            </div>
        `
        : '';

    // Build actions section (prefer module.actions, fallback to module.status.actions)
    const actions = module.actions && module.actions.length > 0
        ? module.actions
        : (module.status && module.status.actions ? module.status.actions : []);

    const actionsHTML = actions.length > 0
        ? `
            <div class="module-actions">
                ${actions.map(action => `
                    <button
                        class="action-btn ${action.variant || 'primary'}"
                        onclick="executeAction('${module.id}', '${action.id}')"
                    >
                        ${action.label}
                    </button>
                `).join('')}
            </div>
        `
        : '';

    card.innerHTML = `
        <div class="module-header">
            <div class="module-icon">${module.icon}</div>
            <div class="module-info">
                <h2 class="module-name">${module.name}</h2>
                <p class="module-description">${module.description}</p>
            </div>
        </div>
        ${statusHTML}
        ${fieldsHTML}
        ${actionsHTML}
        <div class="module-results" id="results-${module.id}" style="display: none;">
            <div class="results-header">
                <span class="results-title">Result</span>
                <button class="results-close" onclick="clearResults('${module.id}')">✕</button>
            </div>
            <pre class="results-output"></pre>
        </div>
    `;

    return card;
}

// Execute module action
async function executeAction(moduleId, actionId) {
    // Disable all buttons temporarily
    const buttons = document.querySelectorAll('.action-btn');
    buttons.forEach(btn => btn.disabled = true);

    try {
        // Collect field values from the module card
        const params = {};
        const moduleCard = document.querySelector(`[id*="${moduleId}"]`)?.closest('.module-card') ||
                          Array.from(document.querySelectorAll('.module-card')).find(card => {
                              const inputs = card.querySelectorAll('.field-input');
                              return inputs.length > 0 && inputs[0].id.startsWith(moduleId);
                          });

        if (moduleCard) {
            const inputs = moduleCard.querySelectorAll('.field-input');
            inputs.forEach(input => {
                const fieldId = input.getAttribute('data-field-id');
                if (fieldId) {
                    params[fieldId] = input.value;
                }
            });
        }

        const response = await fetch(`${API_BASE}/modules/${moduleId}/action`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action_id: actionId,
                params: params
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || 'Action completed successfully', 'success');

            // Store the output to display after reload
            const outputToShow = data.data && data.data.output ? data.data.output : null;

            // Reload modules to show updated status
            await loadModules();

            // Display command output after reload if available
            if (outputToShow) {
                const resultsDiv = document.getElementById(`results-${moduleId}`);
                if (resultsDiv) {
                    const outputPre = resultsDiv.querySelector('.results-output');
                    outputPre.textContent = outputToShow;
                    resultsDiv.style.display = 'block';
                }
            }
        } else {
            showToast(data.error || 'Action failed', 'error');
        }

    } catch (error) {
        console.error('Error executing action:', error);
        showToast('Failed to execute action', 'error');
    } finally {
        buttons.forEach(btn => btn.disabled = false);
    }
}

// Clear results display for a module
function clearResults(moduleId) {
    const resultsDiv = document.getElementById(`results-${moduleId}`);
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
        const outputPre = resultsDiv.querySelector('.results-output');
        if (outputPre) {
            outputPre.textContent = '';
        }
    }
}

// Reload all modules
async function reloadModules() {
    const btn = document.querySelector('.reload-btn');
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/reload`);
        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            await loadModules();
        } else {
            showToast(data.error || 'Failed to reload modules', 'error');
        }

    } catch (error) {
        console.error('Error reloading modules:', error);
        showToast('Failed to reload modules', 'error');
    } finally {
        btn.disabled = false;
    }
}

// Auto-refresh status every 30 seconds
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(async () => {
        // Silently refresh module status without showing toast
        await loadModules();
    }, 30000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadModules();
    startAutoRefresh();
});

// Stop auto-refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});
