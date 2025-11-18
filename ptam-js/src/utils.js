const crypto = require('crypto');
const fs = require('fs').promises;

/**
 * Checks if a buffer likely contains binary data by checking for a null byte.
 * @param {Buffer} buffer The buffer to check.
 * @returns {boolean} True if the buffer is likely binary.
 */
function isBinary(buffer) {
    const chunk = buffer.slice(0, 1024);
    return chunk.includes(0);
}

/**
 * Calculates the SHA-256 hash of a file.
 * @param {string} filepath The path to the file.
 * @returns {Promise<string>} The SHA-256 hash of the file.
 */
async function _get_file_hash(filepath) {
    const fileBuffer = await fs.readFile(filepath);
    const hash = crypto.createHash('sha256');
    hash.update(fileBuffer);
    return hash.digest('hex');
}

/**
 * Escapes special characters in file content.
 * @param {string} content The content to escape.
 * @returns {string} The escaped content.
 */
function _escape_content(content) {
    // Using replaceAll with simple strings is the safest way to handle this,
    // avoiding the double-escaping issues of regular expressions.
    // We must escape backslashes first.
    return content
        .replaceAll('\\', '\\\\') // Replace one literal backslash with two
        .replaceAll('(', '\\(')   // Replace a literal ( with \(
        .replaceAll(')', '\\)');  // Replace a literal ) with \)
}

module.exports = { isBinary, _get_file_hash, _escape_content };
