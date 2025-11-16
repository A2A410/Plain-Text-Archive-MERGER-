const fs = require('fs').promises;
const path = require('path');
const { isBinary } = require('./utils');

/**
 * Recursively walks a directory and gathers information about all files and subdirectories.
 *
 * @param {string} baseDir - The absolute path to the base directory to start the walk from.
 * @returns {Promise<object>} - An object containing lists of all paths and text file contents.
 */
async function walkDirectory(baseDir) {
    const allPaths = new Set();
    const textContents = {};
    const binaryFiles = new Set();

    async function walk(directory) {
        const relativeDir = path.relative(baseDir, directory);
        // Normalize path separators to forward slashes for consistency.
        const normalizedRelativeDir = relativeDir.replace(/\\\\/g, '/');
        if (normalizedRelativeDir) {
            allPaths.add(normalizedRelativeDir + '/');
        }


        const entries = await fs.readdir(directory, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(directory, entry.name);
            if (entry.isDirectory()) {
                await walk(fullPath);
            } else if (entry.isFile()) {
                if ((await fs.stat(fullPath)).size === 0) {
                    continue; // Skip empty files, they'll be handled separately
                }
                const buffer = await fs.readFile(fullPath);
                if (isBinary(buffer)) {
                    binaryFiles.add(fullPath);
                } else {
                    try {
                        textContents[fullPath] = buffer.toString('utf-8');
                    } catch (e) {
                        // If it fails to decode, treat it as binary
                        binaryFiles.add(fullPath);
                    }
                }
            }
        }
    }

    await walk(baseDir);

    return {
        allPaths: Array.from(allPaths),
        textContents,
        binaryFiles: Array.from(binaryFiles),
    };
}

/**
 * Processes the virtualFiles input to create a consistent data structure.
 *
 * @param {object|string[]} virtualFiles - The virtual files to process.
 * @returns {object} - An object containing the paths and content of the virtual files.
 */
function processVirtualFiles(virtualFiles) {
    const allPaths = new Set();
    const textContents = {};
    let randomFileCounter = 0;

    if (Array.isArray(virtualFiles)) {
        for (const content of virtualFiles) {
            const filename = `random_${randomFileCounter++}.txt`;
            textContents[filename] = content;
        }
    } else if (typeof virtualFiles === 'object' && virtualFiles !== null) {
        for (const [filePath, content] of Object.entries(virtualFiles)) {
            const normalizedPath = path.normalize(filePath).replace(/\\\\/g, '/');
            textContents[normalizedPath] = content;
            const dirname = path.dirname(normalizedPath);
            if (dirname !== '.') {
                allPaths.add(dirname + '/');
            }
        }
    }

    return {
        allPaths: Array.from(allPaths),
        textContents,
        binaryFiles: [], // Virtual files are always text
    };
}


module.exports = { walkDirectory, processVirtualFiles };
