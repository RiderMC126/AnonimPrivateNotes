document.addEventListener('DOMContentLoaded', () => {
    const infoCard = document.querySelector('.info-card');
    const closeBtn = document.querySelector('.close-btn');
    const dontShowCheckbox = document.getElementById('dontShow');

    if (localStorage.getItem('hideInfoCard') === 'true') {
        infoCard.style.display = 'none';
    }

    closeBtn.addEventListener('click', () => {
        infoCard.style.display = 'none';
        if (dontShowCheckbox.checked) {
            localStorage.setItem('hideInfoCard', 'true');
        }
    });

    const optionsToggle = document.querySelector('.options-toggle');
    const expiryContainer = document.querySelector('.expiry-container');
    const fileUpload = document.querySelector('.file-upload');

    expiryContainer.style.display = 'none';
    fileUpload.style.display = 'none';

    optionsToggle.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = expiryContainer.style.display === 'none';
        expiryContainer.style.display = isHidden ? 'block' : 'none';
        fileUpload.style.display = isHidden ? 'block' : 'none';
        optionsToggle.textContent = isHidden ? '⚙ Скрыть параметры ⚙' : '⚙ Дополнительные параметры ⚙';
    });

    const textarea = document.querySelector('.text-area');
    const charCounter = document.querySelector('.char-counter');
    
    textarea.addEventListener('input', () => {
        charCounter.textContent = `${textarea.value.length} / 5000`;
    });

    const fileInput = document.querySelector('.file-input');
    const filePlaceholder = document.querySelector('.file-placeholder');
    
    fileInput.addEventListener('change', () => {
        filePlaceholder.textContent = fileInput.files.length > 0
            ? `Выбран файл: ${fileInput.files[0].name} (будет доступен для скачивания)`
            : 'Выберите файл ⚡ Файл не выбран';
    });

    const modal = document.getElementById('success-modal');
    const noteUrlLink = document.getElementById('note-url');
    const closeModalBtn = document.getElementById('close-modal');

    closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    const form = document.querySelector('.form-container');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        modal.style.display = 'none';
        
        const formData = new FormData(form);
        
        const textValue = textarea.value.trim();
        const fileValue = fileInput.files[0];
        
        if (!textValue && !fileValue) {
            alert('Пожалуйста, введите текст или выберите файл');
            return;
        }
        
        if (!fileValue && textValue) {
            formData.set('text', textValue);
        }
        
        if (!formData.get('expiry_time')) {
            formData.set('expiry_time', '1 день');
        }

        console.log('Form submission:');
        for (let [key, value] of formData.entries()) {
            if (key === 'file_upload') {
                console.log(`${key}: ${value ? value.name : 'No file'}`);
            } else {
                console.log(`${key}: ${value}`);
            }
        }

        try {
            const response = await fetch('/create', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                const url = `${window.location.origin}${data.note_url}`;
                noteUrlLink.textContent = url;
                noteUrlLink.href = url;
                modal.style.display = 'flex';
                
                form.reset();
                charCounter.textContent = '0 / 5000';
                filePlaceholder.textContent = 'Выберите файл ⚡ Файл не выбран';
                expiryContainer.style.display = 'none';
                fileUpload.style.display = 'none';
                optionsToggle.textContent = '⚙ Дополнительные параметры ⚙';
            } else {
                const errorData = await response.json();
                alert(`Ошибка: ${errorData.detail || 'Не удалось создать записку. Проверьте данные и попробуйте снова.'}`);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            alert('Ошибка при отправке формы: Проверьте подключение к серверу или попробуйте снова позже.');
        }
    });
});