// Счётчик символов
        const textarea = document.querySelector('.text-area');
        const counter = document.querySelector('.char-counter');

        textarea.addEventListener('input', function() {
            const count = this.value.length;
            counter.textContent = `${count} / 5000`;
        });

        // Закрытие информационной карточки
        document.querySelector('.close-btn').addEventListener('click', function() {
            document.querySelector('.info-card').style.display = 'none';
        });

        // Обработка загрузки файла
        const fileInput = document.querySelector('.file-input');
        const filePlaceholder = document.querySelector('.file-placeholder');

        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                filePlaceholder.textContent = `Выбран файл: ${this.files[0].name}`;
            } else {
                filePlaceholder.textContent = 'Выберите файл ⚡ Файл не выбран';
            }
        });

        // Анимация кнопки создания
        const createBtn = document.querySelector('.create-btn');
        createBtn.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        createBtn.addEventListener('mouseup', function() {
            this.style.transform = '';
        });