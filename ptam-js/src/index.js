const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

const { walkDirectory, processVirtualFiles } = require('./file-traversal');
const { tokenize } = require('./tokenization');
const { generatePtamFile } = require('./ptam-generation');

/**
 * Archives a source directory and/or virtual files into a human-readable .ptam file.
 *
 * @param {string | null} sourceDirectory - The path to the directory to archive. Can be null if only using virtual files.
 * @param {string} outputPtamFile - The path where the .ptam file will be saved.
 * @param {object} [options={}] - Optional parameters.
 * @param {boolean} [options.useTokenization=false] - Whether to use word tokenization.
 * @param {object|string[]} [options.virtualFiles=null] - In-memory files to add to the archive.
 */
async function archive(sourceDirectory, outputPtamFile, { useTokenization = false, virtualFiles = null } = {}) {
    if (!sourceDirectory && !virtualFiles) {
        throw new Error('Either a source directory or virtual files must be provided.');
    }

    try {
        let fileSystemData = { allPaths: [], textContents: {}, binaryFiles: [] };
        if (sourceDirectory) {
            const sourcePath = path.resolve(sourceDirectory);
            fileSystemData = await walkDirectory(sourcePath);
        }

        const virtualFileData = processVirtualFiles(virtualFiles);

        const allPaths = [...new Set([...fileSystemData.allPaths, ...virtualFileData.allPaths])];
        let textContents = { ...fileSystemData.textContents, ...virtualFileData.textContents };
        const binaryFiles = fileSystemData.binaryFiles;

        let tokens = {};
        if (useTokenization) {
            const tokenizationResult = tokenize(textContents);
            tokens = tokenizationResult.tokens;
            textContents = tokenizationResult.tokenizedContents;
        }

        await generatePtamFile({
            outputPtamFile,
            sourceDirectory,
            allPaths,
            textContents,
            binaryFiles,
            tokens,
        });

        console.log('Archiving process complete.');

    } catch (error) {
        console.error(`Error during archiving process: ${error.message}`);
        throw error;
    }
}

module.exports = { archive };
