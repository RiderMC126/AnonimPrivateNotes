function copyToClipboard(text, element) {
    navigator.clipboard.writeText(text).then(function() {
        const copyHint = element.closest('.crypto-card').querySelector('.copy-hint');
        const originalContent = copyHint.textContent;
        copyHint.textContent = 'Адрес скопирован!';
        copyHint.style.color = '#4CAF50';
                
        setTimeout(() => {
            copyHint.textContent = originalContent;
            copyHint.style.color = '#999';
        }, 2000);
    }).catch(function(err) {
        console.error('Ошибка копирования: ', err);
    });
}

document.querySelectorAll('.crypto-card').forEach(card => {
    card.addEventListener('click', function() {
        const address = this.querySelector('.crypto-address').textContent;
        copyToClipboard(address, this);
    });
});