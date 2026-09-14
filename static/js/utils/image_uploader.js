/**
 * ImageUploader - Componente reutilizable para subida de imágenes
 * ✅ NOTIFICACIONES UNIFICADAS: usa Notify global
 */
class ImageUploader {
    constructor(config = {}) {
        this.config = Object.assign({
            previewId: null, placeholderId: null, inputId: null,
            removeBtnId: null, infoId: null, wrapperId: null,
            maxFileSize: 5 * 1024 * 1024,
            acceptedTypes: ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'],
            loggerPrefix: '[ImageUploader]'
        }, config);

        this.selectedFile = null;
        this.currentImageUrl = null;
        this.removed = false;

        this.els = {
            preview: document.getElementById(this.config.previewId),
            placeholder: document.getElementById(this.config.placeholderId),
            input: document.getElementById(this.config.inputId),
            removeBtn: document.getElementById(this.config.removeBtnId),
            info: document.getElementById(this.config.infoId),
            wrapper: document.getElementById(this.config.wrapperId)
        };

        this._handlers = {};
        Logger.setPrefix(this.config.loggerPrefix);
        this.#init();
    }

    #init() {
        if (!this.els.preview || !this.els.input) {
            Logger.error('Elementos DOM requeridos no encontrados');
            return;
        }
        this.#bindEvents();
        Logger.info('Componente ImageUploader inicializado');
    }

    #bindEvents() {
        this._handlers.fileChange = (e) => this.#handleFileChange(e);
        this.els.input.addEventListener('change', this._handlers.fileChange);

        if (this.els.removeBtn) {
            this._handlers.remove = () => this.removeImage();
            this.els.removeBtn.addEventListener('click', this._handlers.remove);
        }

        if (this.els.wrapper) {
            this._handlers.dragOver = (e) => { e.preventDefault(); this.els.wrapper.classList.add('drag-over'); };
            this._handlers.dragLeave = () => this.els.wrapper.classList.remove('drag-over');
            this._handlers.drop = (e) => {
                e.preventDefault();
                this.els.wrapper.classList.remove('drag-over');
                if (e.dataTransfer.files.length > 0) {
                    this.els.input.files = e.dataTransfer.files;
                    this.els.input.dispatchEvent(new Event('change'));
                }
            };
            this._handlers.wrapperClick = (e) => {
                if (e.target.tagName !== 'BUTTON' && !e.target.closest('button'))
                    this.els.input.click();
            };
            this.els.wrapper.addEventListener('dragover', this._handlers.dragOver);
            this.els.wrapper.addEventListener('dragleave', this._handlers.dragLeave);
            this.els.wrapper.addEventListener('drop', this._handlers.drop);
            this.els.wrapper.addEventListener('click', this._handlers.wrapperClick);
        }
    }

    #handleFileChange(e) {
        const file = e.target.files[0];
        if (!file) return;

        if (!this.config.acceptedTypes.includes(file.type)) {
            // ✅ UNIFICADO: usa Notify en lugar de Noty directo
            this.#notify('Tipo de archivo no permitido. Use: PNG, JPG, GIF o WEBP', 'error');
            this.els.input.value = '';
            return;
        }

        if (file.size > this.config.maxFileSize) {
            const mb = (this.config.maxFileSize / (1024 * 1024)).toFixed(1);
            // ✅ UNIFICADO
            this.#notify(`La imagen es demasiado grande. Máximo ${mb}MB`, 'error');
            this.els.input.value = '';
            return;
        }

        this.selectedFile = file;
        this.removed = false;

        const reader = new FileReader();
        reader.onload = (ev) => {
            this.els.preview.src = ev.target.result;
            this.els.preview.style.display = 'block';
            if (this.els.placeholder) this.els.placeholder.style.display = 'none';
        };
        reader.readAsDataURL(file);

        if (this.els.info) {
            this.els.info.innerHTML = `<i class="bi bi-file-earmark-image"></i> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            this.els.info.style.display = 'block';
        }

        if (this.els.removeBtn) this.els.removeBtn.style.display = 'inline-block';

        Logger.success('Imagen seleccionada', { name: file.name, size: `${(file.size / 1024).toFixed(1)} KB` });
    }

    // ✅ UNIFICADO: usa Notify global en lugar de Noty directo
    #notify(msg, type) {
        Notify.alert(msg, type);
    }

    loadExisting(imageUrl) {
        if (!imageUrl || imageUrl.trim() === '') { this.reset(); return; }
        this.currentImageUrl = imageUrl;
        this.selectedFile = null;
        this.removed = false;
        this.els.preview.src = imageUrl;
        this.els.preview.style.display = 'block';
        if (this.els.placeholder) this.els.placeholder.style.display = 'none';
        if (this.els.info) this.els.info.style.display = 'none';
        if (this.els.removeBtn) this.els.removeBtn.style.display = 'inline-block';
        Logger.info('Imagen existente cargada', { url: imageUrl });
    }

    removeImage() {
        const hadImage = this.currentImageUrl || this.selectedFile;
        this.selectedFile = null;
        this.currentImageUrl = null;
        this.removed = hadImage ? true : false;
        this.els.input.value = '';
        this.els.preview.style.display = 'none';
        if (this.els.placeholder) this.els.placeholder.style.display = 'flex';
        if (this.els.removeBtn) this.els.removeBtn.style.display = 'none';
        if (this.els.info) this.els.info.style.display = 'none';
        Logger.info('Imagen quitada', { removed: this.removed });
        // ✅ UNIFICADO
        this.#notify('Imagen quitada. Se guardará al confirmar.', 'info');
    }

    getSelectedFile() { return this.selectedFile; }
    hasChanges() { return this.selectedFile !== null || this.removed; }
    wasRemoved() { return this.removed; }

    reset() {
        this.selectedFile = null;
        this.currentImageUrl = null;
        this.removed = false;
        this.els.input.value = '';
        this.els.preview.style.display = 'none';
        if (this.els.placeholder) this.els.placeholder.style.display = 'flex';
        if (this.els.removeBtn) this.els.removeBtn.style.display = 'none';
        if (this.els.info) this.els.info.style.display = 'none';
    }

    destroy() {
        if (this.els.input && this._handlers.fileChange)
            this.els.input.removeEventListener('change', this._handlers.fileChange);
        if (this.els.removeBtn && this._handlers.remove)
            this.els.removeBtn.removeEventListener('click', this._handlers.remove);
        this._handlers = {};
    }
}

window.ImageUploader = ImageUploader;