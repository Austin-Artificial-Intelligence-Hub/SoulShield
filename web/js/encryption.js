/**
 * SoulShield Client-Side Encryption Module
 * Uses AES-256-GCM with PBKDF2 key derivation for zero-knowledge encryption
 */
(function() {
    'use strict';

    class ChatEncryption {
        constructor() {
            this.encoder = new TextEncoder();
            this.decoder = new TextDecoder();
        }

        /**
         * Derive encryption key from user password
         * Uses PBKDF2 with 100,000 iterations
         */
        async deriveKey(password, salt) {
            const keyMaterial = await crypto.subtle.importKey(
                'raw',
                this.encoder.encode(password),
                'PBKDF2',
                false,
                ['deriveBits', 'deriveKey']
            );

            return crypto.subtle.deriveKey(
                {
                    name: 'PBKDF2',
                    salt: salt,
                    iterations: 100000,
                    hash: 'SHA-256'
                },
                keyMaterial,
                { name: 'AES-GCM', length: 256 },
                false,
                ['encrypt', 'decrypt']
            );
        }

        /**
         * Encrypt a message
         * Returns: { ciphertext: base64, iv: base64, salt: base64 }
         */
        async encryptMessage(message, password) {
            const salt = crypto.getRandomValues(new Uint8Array(16));
            const iv = crypto.getRandomValues(new Uint8Array(12));
            const key = await this.deriveKey(password, salt);

            const ciphertext = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv: iv },
                key,
                this.encoder.encode(message)
            );

            return {
                ciphertext: this.arrayBufferToBase64(ciphertext),
                iv: this.arrayBufferToBase64(iv),
                salt: this.arrayBufferToBase64(salt)
            };
        }

        /**
         * Decrypt a message
         */
        async decryptMessage(encryptedData, password) {
            const salt = this.base64ToArrayBuffer(encryptedData.salt);
            const iv = this.base64ToArrayBuffer(encryptedData.iv);
            const ciphertext = this.base64ToArrayBuffer(encryptedData.ciphertext);
            const key = await this.deriveKey(password, salt);

            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv: iv },
                key,
                ciphertext
            );

            return this.decoder.decode(decrypted);
        }

        /**
         * Encrypt conversation history
         */
        async encryptHistory(messages, password) {
            const jsonString = JSON.stringify(messages);
            return this.encryptMessage(jsonString, password);
        }

        /**
         * Decrypt conversation history
         */
        async decryptHistory(encryptedData, password) {
            const jsonString = await this.decryptMessage(encryptedData, password);
            return JSON.parse(jsonString);
        }

        // Helper methods
        arrayBufferToBase64(buffer) {
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        }

        base64ToArrayBuffer(base64) {
            const binary = atob(base64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) {
                bytes[i] = binary.charCodeAt(i);
            }
            return bytes.buffer;
        }
    }

    // Export to global scope
    window.SoulShieldEncryption = ChatEncryption;
})();

