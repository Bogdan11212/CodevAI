/**
 * Основные функции JavaScript для CodevAI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Добавление кнопок копирования для блоков кода
    addCopyButtonToCodeBlocks();
    
    // Форматирование блоков кода
    formatCodeBlocks();
    
    // Добавление номеров строк к блокам кода
    addLineNumbersToCode();
});

/**
 * Форматирование блоков кода с подсветкой синтаксиса
 * В реальной среде используйте библиотеку вроде highlight.js
 */
function formatCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(function(block) {
        // Простая подсветка ключевых слов
        const keywords = ['function', 'return', 'if', 'else', 'for', 'while', 'let', 'const', 'var', 'import', 'export', 'class', 'def', 'from', 'import'];
        
        keywords.forEach(function(keyword) {
            const regex = new RegExp('\\b' + keyword + '\\b', 'g');
            block.innerHTML = block.innerHTML.replace(regex, '<span class="keyword">' + keyword + '</span>');
        });
        
        // Подсветка строк
        block.innerHTML = block.innerHTML.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, '<span class="string">$&</span>');
        
        // Подсветка комментариев
        block.innerHTML = block.innerHTML.replace(/(\/\/.*)/g, '<span class="comment">$1</span>');
        block.innerHTML = block.innerHTML.replace(/(#.*)/g, '<span class="comment">$1</span>');
    });
}

/**
 * Добавление номеров строк к блокам кода
 */
function addLineNumbersToCode() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(function(block) {
        const lines = block.innerHTML.split('\n');
        let numberedLines = '';
        
        for (let i = 0; i < lines.length; i++) {
            if (i === lines.length - 1 && lines[i].trim() === '') continue;
            numberedLines += `<span class="line-number">${i + 1}</span>${lines[i]}\n`;
        }
        
        block.innerHTML = numberedLines;
        block.parentNode.classList.add('line-numbers');
    });
}

/**
 * Добавление кнопок копирования к блокам кода
 */
function addCopyButtonToCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre');
    
    codeBlocks.forEach(function(block) {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Копировать';
        
        button.addEventListener('click', function() {
            const code = block.querySelector('code');
            if (code) {
                // Создаем временный элемент для копирования текста
                const textarea = document.createElement('textarea');
                textarea.value = code.textContent;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                
                // Изменяем текст кнопки для индикации успешного копирования
                button.textContent = 'Скопировано!';
                setTimeout(function() {
                    button.textContent = 'Копировать';
                }, 2000);
            }
        });
        
        // Добавляем кнопку к блоку кода
        block.appendChild(button);
    });
}