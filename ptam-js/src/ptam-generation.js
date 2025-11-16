const fs = require('fs').promises;
const path = require('path');
const { _get_file_hash, _escape_content } = require('./utils');

/**
 * Generates the .ptam file from the collected data.
 * @param {object} data - The data collected from the traversal and tokenization steps.
 */
async function generatePtamFile(data) {
    const {
        outputPtamFile,
        sourceDirectory,
        allPaths,
        textContents,
        binaryFiles,
        tokens,
    } = data;

    const useTokenization = Object.keys(tokens).length > 0;
    const hasMediaReferences = binaryFiles.length > 0;

    // Build the header
    const headerParts = [
        '[header]',
        '# PTAM Archive v1.1',
        `# tokenization: ${useTokenization}`,
        `# media_references: ${hasMediaReferences}`,
        ''
    ];

    // Build the structure section
    const structureParts = ['[structure]'];
    const allDirs = new Set(['/', ...allPaths.filter(p => p.endsWith('/')).map(p => `/${p.slice(0, -1)}/`)]);
    for (const dir of [...allDirs].sort()) {
        structureParts.push(dir);
    }
    structureParts.push('');

    // Build the tokens section
    const tokensParts = [];
    if (useTokenization) {
        tokensParts.push('[tokens]');
        const sortedTokens = Object.entries(tokens).sort((a, b) => {
            return parseInt(a[1].substring(1)) - parseInt(b[1].substring(1));
        });
        for (const [word, token] of sortedTokens) {
            tokensParts.push(`${token}="${word}"`);
        }
        tokensParts.push('');
    }

    // Build the archive body
    const archiveBodyParts = [];
    const allArchivePaths = new Set(['/']);
    Object.keys(textContents).forEach(p => {
        const dirname = path.dirname(p);
        if (dirname !== '.') allArchivePaths.add(`/${dirname}/`);
    });
    binaryFiles.forEach(p => {
        const dirname = path.dirname(path.relative(sourceDirectory, p));
        if (dirname !== '.') allArchivePaths.add(`/${dirname}/`);
    });


    for (const dir of [...allArchivePaths].sort()) {
        archiveBodyParts.push(`[path:${dir}]`);
        const currentPath = dir === '/' ? '.' : dir.slice(1, -1);

        const itemsInDir = {
            dirs: new Set(),
            files: new Set()
        };

        Object.keys(textContents).forEach(p => {
            const dirname = path.dirname(p);
            if (dirname === currentPath) {
                itemsInDir.files.add(path.basename(p));
            }
        });
        binaryFiles.forEach(p => {
            const relativePath = path.relative(sourceDirectory, p);
            const dirname = path.dirname(relativePath);
            if (dirname === currentPath) {
                itemsInDir.files.add(path.basename(p));
            }
        });

        // Add subdirectories.
        for (const p of allPaths) {
            if (p.endsWith('/') && path.dirname(p.slice(0, -1)) === currentPath) {
                itemsInDir.dirs.add(path.basename(p));
            }
        }


        for (const d of [...itemsInDir.dirs].sort()) {
            archiveBodyParts.push(`${d}/`);
        }

        for (const f of [...itemsInDir.files].sort()) {
             const fullPath = sourceDirectory ? path.join(sourceDirectory, currentPath, f) : null;
             const virtualPath = path.join(currentPath, f);
            if (textContents[virtualPath]) {
                const escapedContent = _escape_content(textContents[virtualPath]);
                archiveBodyParts.push(f);
                archiveBodyParts.push(`(${escapedContent})`);
            } else if (binaryFiles.includes(fullPath)) {
                const fileHash = await _get_file_hash(fullPath);
                archiveBodyParts.push(`${f} (skipped_binary:sha256:${fileHash})`);
            } else {
                 archiveBodyParts.push(`${f}//`); // Empty file
            }
        }
        archiveBodyParts.push('');
    }


    const finalArchive = [
        ...headerParts,
        ...structureParts,
        ...tokensParts,
        ...archiveBodyParts,
        '[g-end]'
    ].join('\n');

    await fs.writeFile(outputPtamFile, finalArchive.trim() + '\n', 'utf-8');
}

module.exports = { generatePtamFile };
