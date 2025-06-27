class QueryConsole {
    constructor() {
        // Derive backend API URL from current browser URL
        const currentUrl = window.location.origin;
        const baseUrl = currentUrl.replace('queryui-', 'duckdb-');
        this.hiveApiUrl = baseUrl + '/hive-folders';
        this.queryApiUrl = baseUrl + '/query';
        this.initializeElements();
        this.bindEvents();
        this.loadHiveTree();
    }

    initializeElements() {
        this.hiveTreeContainer = document.getElementById('hive-tree');
        this.sqlEditor = document.getElementById('sql-editor');
        this.runQueryBtn = document.getElementById('run-query');
        this.clearQueryBtn = document.getElementById('clear-query');
        this.refreshTreeBtn = document.getElementById('refresh-tree');
        this.resultsContainer = document.getElementById('results-container');
        this.queryStatus = document.getElementById('query-status');
        this.selectedFolderDiv = document.getElementById('selected-folder');
        this.selectedPathSpan = document.getElementById('selected-path');
        this.clearSelectionBtn = document.getElementById('clear-selection');
        this.resizer = document.getElementById('resizer');
        this.selectedPath = '';
    }

    bindEvents() {
        this.runQueryBtn.addEventListener('click', () => this.executeQuery());
        this.clearQueryBtn.addEventListener('click', () => this.clearQuery());
        this.refreshTreeBtn.addEventListener('click', () => this.loadHiveTree());
        this.clearSelectionBtn.addEventListener('click', () => this.clearSelection());
        
        // Enable Ctrl+Enter to run query
        this.sqlEditor.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.executeQuery();
            }
        });

        // Resizer functionality
        this.setupResizer();
    }

    async loadHiveTree(parent = '') {
        try {
            if (parent === '') {
                this.hiveTreeContainer.innerHTML = '<div class="loading">Loading...</div>';
            }
            
            const url = parent ? `${this.hiveApiUrl}?parent=${encodeURIComponent(parent)}` : this.hiveApiUrl;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (parent === '') {
                // Root level - replace entire tree
                this.renderHiveTree(data.folders, this.hiveTreeContainer, 0);
            }
        } catch (error) {
            console.error('Error loading hive tree:', error);
            if (parent === '') {
                this.hiveTreeContainer.innerHTML = `
                    <div class="error-message">
                        Failed to load hive tree: ${error.message}
                    </div>
                `;
            }
        }
    }

    renderHiveTree(folders, container, level = 0, parentPath = '') {
        if (level === 0) {
            container.innerHTML = '';
        }

        if (!folders || folders.length === 0) {
            if (level === 0) {
                container.innerHTML = '<div class="no-results">No hive folders found</div>';
            }
            return;
        }

        folders.forEach(folderName => {
            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'tree-node folder';
            nodeDiv.style.paddingLeft = `${level * 16 + 8}px`;
            
            const fullPath = parentPath ? `${parentPath}/${folderName}` : folderName;
            
            // Create expand/collapse button
            const expandBtn = document.createElement('span');
            expandBtn.className = 'expand-btn';
            expandBtn.textContent = '▶';
            expandBtn.style.marginRight = '4px';
            expandBtn.style.cursor = 'pointer';
            expandBtn.style.fontSize = '10px';
            
            const labelSpan = document.createElement('span');
            // Clean up hive partition names (e.g., "hostname=host_0" -> "host_0")
            const displayName = folderName.includes('=') ? folderName.split('=')[1] : folderName;
            labelSpan.textContent = displayName;
            labelSpan.style.cursor = 'pointer';
            
            nodeDiv.appendChild(expandBtn);
            nodeDiv.appendChild(labelSpan);
            
            // Container for children
            const childrenDiv = document.createElement('div');
            childrenDiv.className = 'tree-children';
            childrenDiv.style.display = 'none';
            
            let expanded = false;
            let childrenLoaded = false;
            
            expandBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                
                if (!expanded) {
                    if (!childrenLoaded) {
                        childrenDiv.innerHTML = '<div class="loading" style="padding: 4px 20px; font-size: 12px;">Loading...</div>';
                        childrenDiv.style.display = 'block';
                        await this.loadChildren(fullPath, childrenDiv, level + 1);
                        childrenLoaded = true;
                    } else {
                        childrenDiv.style.display = 'block';
                    }
                    expandBtn.textContent = '▼';
                    expanded = true;
                } else {
                    childrenDiv.style.display = 'none';
                    expandBtn.textContent = '▶';
                    expanded = false;
                }
            });
            
            labelSpan.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectFolder(fullPath);
            });

            container.appendChild(nodeDiv);
            container.appendChild(childrenDiv);
        });
    }

    async loadChildren(parentPath, container, level) {
        try {
            const url = `${this.hiveApiUrl}?parent=${encodeURIComponent(parentPath)}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            container.innerHTML = '';
            
            if (data.folders && data.folders.length > 0) {
                this.renderHiveTree(data.folders, container, level, parentPath);
            } else {
                container.innerHTML = '<div style="padding: 4px 20px; font-size: 12px; color: #666;">No subfolders</div>';
            }
        } catch (error) {
            console.error('Error loading children:', error);
            container.innerHTML = '<div style="padding: 4px 20px; font-size: 12px; color: #d93025;">Error loading</div>';
        }
    }

    insertTableName(tableName, level) {
        // Build full path for deeper levels
        const currentValue = this.sqlEditor.value;
        const cursorPos = this.sqlEditor.selectionStart;
        
        // Insert table name at cursor position
        const beforeCursor = currentValue.substring(0, cursorPos);
        const afterCursor = currentValue.substring(cursorPos);
        
        this.sqlEditor.value = beforeCursor + tableName + afterCursor;
        this.sqlEditor.focus();
        
        // Position cursor after inserted text
        const newCursorPos = cursorPos + tableName.length;
        this.sqlEditor.setSelectionRange(newCursorPos, newCursorPos);
    }

    async executeQuery() {
        let query = this.sqlEditor.value.trim();
        
        if (!query) {
            this.showStatus('Please enter a query', 'error');
            return;
        }

        // Replace :selected: with the read_parquet statement
        if (query.includes(':selected:') && this.selectedPath) {
            const s3Path = `s3://quix-test-bucket/events6/${this.selectedPath}/*.parquet`;
            const readParquetStatement = `read_parquet('${s3Path}')`;
            query = query.replace(/:selected:/g, readParquetStatement);
        }

        this.runQueryBtn.disabled = true;
        this.runQueryBtn.textContent = 'Running...';
        this.showStatus('Executing query...', '');

        try {
            const response = await fetch(this.queryApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain',
                },
                body: query
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const result = await response.text();
            this.displayResults(result);
            this.showStatus('Query completed successfully', 'success');

        } catch (error) {
            console.error('Query error:', error);
            this.displayError(error.message);
            this.showStatus('Query failed', 'error');
        } finally {
            this.runQueryBtn.disabled = false;
            this.runQueryBtn.textContent = 'Run Query';
        }
    }

    displayResults(result) {
        // Check if result looks like a pandas DataFrame string representation
        if (result.includes('|') && result.includes('\n')) {
            this.displayDataFrameTable(result);
        } else {
            // Display as preformatted text
            this.resultsContainer.innerHTML = `
                <div class="results-pre">${this.escapeHtml(result)}</div>
            `;
        }
    }

    displayDataFrameTable(result) {
        const lines = result.trim().split('\n');
        
        if (lines.length < 2) {
            this.resultsContainer.innerHTML = `<div class="results-pre">${this.escapeHtml(result)}</div>`;
            return;
        }

        // Find header line (usually contains column names)
        let headerIndex = -1;
        let separatorIndex = -1;
        
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('|') && !lines[i].match(/^[\s\-\|]+$/)) {
                headerIndex = i;
                break;
            }
        }

        if (headerIndex === -1) {
            this.resultsContainer.innerHTML = `<div class="results-pre">${this.escapeHtml(result)}</div>`;
            return;
        }

        // Find separator line
        for (let i = headerIndex + 1; i < lines.length; i++) {
            if (lines[i].match(/^[\s\-\|]+$/)) {
                separatorIndex = i;
                break;
            }
        }

        const headerLine = lines[headerIndex];
        const headers = headerLine.split('|').map(h => h.trim()).filter(h => h !== '');

        const table = document.createElement('table');
        table.className = 'results-table';

        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create body
        const tbody = document.createElement('tbody');
        const startIndex = separatorIndex > -1 ? separatorIndex + 1 : headerIndex + 1;
        
        for (let i = startIndex; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line && line.includes('|')) {
                const cells = line.split('|').map(c => c.trim()).filter(c => c !== '');
                if (cells.length === headers.length) {
                    const row = document.createElement('tr');
                    cells.forEach(cell => {
                        const td = document.createElement('td');
                        td.textContent = cell;
                        row.appendChild(td);
                    });
                    tbody.appendChild(row);
                }
            }
        }

        table.appendChild(tbody);
        this.resultsContainer.innerHTML = '';
        this.resultsContainer.appendChild(table);
    }

    displayError(error) {
        this.resultsContainer.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${this.escapeHtml(error)}
            </div>
        `;
    }

    selectFolder(folderPath) {
        this.selectedPath = folderPath;
        this.selectedPathSpan.textContent = `${folderPath}/*`;
        this.selectedFolderDiv.style.display = 'flex';
        console.log('Selected folder:', folderPath);
    }

    clearSelection() {
        this.selectedPath = '';
        this.selectedFolderDiv.style.display = 'none';
    }

    clearQuery() {
        this.sqlEditor.value = '';
        this.sqlEditor.focus();
    }

    showStatus(message, type = '') {
        this.queryStatus.textContent = message;
        this.queryStatus.className = `status ${type}`;
    }

    setupResizer() {
        let isResizing = false;
        
        this.resizer.addEventListener('mousedown', () => {
            isResizing = true;
            document.body.style.cursor = 'row-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const container = document.querySelector('.main-content');
            const containerRect = container.getBoundingClientRect();
            const querySection = document.querySelector('.query-section');
            
            const mouseY = e.clientY - containerRect.top;
            
            // Calculate new height for query section (minimum 150px, maximum container height - 200px for results)
            const minQueryHeight = 150;
            const maxQueryHeight = containerRect.height - 200 - 4; // Reserve 200px for results + 4px for resizer
            
            let newQueryHeight = Math.max(minQueryHeight, Math.min(mouseY - 16, maxQueryHeight)); // 16px for padding
            
            querySection.style.flexBasis = `${newQueryHeight}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the console when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new QueryConsole();
});