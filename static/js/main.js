/**
 * CodevAI - Main JavaScript File
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Format code in pre blocks
    const codeBlocks = document.querySelectorAll('pre code');
    if (codeBlocks.length > 0) {
        formatCodeBlocks(codeBlocks);
    }

    // Add line numbers to code blocks
    addLineNumbersToCode();

    // Add copy button to code blocks
    addCopyButtonToCodeBlocks();
});

/**
 * Format code blocks with syntax highlighting (simple version)
 * In a production environment, you would use a library like highlight.js
 */
function formatCodeBlocks(codeBlocks) {
    codeBlocks.forEach(block => {
        // Simple syntax highlighting for keywords
        // This is a very basic implementation
        const keywords = [
            'function', 'return', 'if', 'else', 'for', 'while', 'class', 
            'try', 'catch', 'import', 'from', 'def', 'async', 'await',
            'var', 'let', 'const', 'new', 'this', 'super', 'extends',
            'package', 'public', 'private', 'protected', 'static'
        ];
        
        let html = block.innerHTML;
        
        // Highlight keywords
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'g');
            html = html.replace(regex, `<span class="text-primary">${keyword}</span>`);
        });
        
        // Highlight strings
        html = html.replace(/(["'])(.*?)\1/g, '<span class="text-success">$&</span>');
        
        // Highlight comments
        html = html.replace(/(\/\/.*|#.*)/g, '<span class="text-secondary">$&</span>');
        
        block.innerHTML = html;
    });
}

/**
 * Add line numbers to code blocks
 */
function addLineNumbersToCode() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const lines = block.innerHTML.split('\n');
        if (lines.length > 1) {
            let numberedLines = '';
            
            lines.forEach((line, i) => {
                numberedLines += `<span class="line-number">${i + 1}</span>${line}\n`;
            });
            
            // Create a line numbers container
            const lineNumbers = document.createElement('div');
            lineNumbers.className = 'line-numbers';
            
            // Update the block with line numbers
            block.innerHTML = numberedLines;
            block.parentNode.classList.add('with-line-numbers');
        }
    });
}

/**
 * Add copy button to code blocks
 */
function addCopyButtonToCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre');
    
    codeBlocks.forEach(block => {
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button btn btn-sm btn-outline-light';
        copyButton.textContent = 'Copy';
        
        // Position the button
        block.style.position = 'relative';
        copyButton.style.position = 'absolute';
        copyButton.style.top = '0.5rem';
        copyButton.style.right = '0.5rem';
        
        // Add click event
        copyButton.addEventListener('click', () => {
            const code = block.querySelector('code') ? 
                          block.querySelector('code').innerText :
                          block.innerText;
            
            navigator.clipboard.writeText(code).then(() => {
                copyButton.textContent = 'Copied!';
                
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                }, 2000);
            });
        });
        
        block.appendChild(copyButton);
    });
}
