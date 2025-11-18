/**
 * Tokenizes the content of text files by replacing frequently used words with tokens.
 *
 * @param {object} textContents - An object where keys are file paths and values are file contents.
 * @returns {object} - An object containing the token map and the tokenized content.
 */
function tokenize(textContents) {
    const wordCounts = {};
    const allWords = [];

    // Find all words that are 5 or more letters long and count their occurrences.
    for (const content of Object.values(textContents)) {
        const words = content.match(/\\b[a-zA-Z]{5,}\\b/g) || [];
        for (const word of words) {
            wordCounts[word] = (wordCounts[word] || 0) + 1;
            allWords.push(word);
        }
    }

    // Create tokens for words that appear 5 or more times.
    const frequentWords = Object.keys(wordCounts).filter(word => wordCounts[word] >= 5).sort();
    const tokens = {};
    let tokenizedContents = { ...textContents };
    let tokenId = 1;
    for (const word of frequentWords) {
        tokens[word] = `$${String(tokenId++).padStart(2, '0')}`;
    }

    // Replace the frequent words with their tokens in the content.
    for (const [path, content] of Object.entries(tokenizedContents)) {
        let newContent = content;
        for (const [word, token] of Object.entries(tokens)) {
            const regex = new RegExp(`\\b${word}\\b`, 'g');
            newContent = newContent.replace(regex, token);
        }
        tokenizedContents[path] = newContent;
    }


    return { tokens, tokenizedContents };
}

module.exports = { tokenize };
