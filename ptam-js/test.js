const { archive } = require('./src/index');
const fs = require('fs').promises;
const path = require('path');

async function runTest() {
    const testDir = 'test_project';
    const outputFile = 'test_project.ptam';

    // Create a dummy directory and a file
    await fs.mkdir(testDir, { recursive: true });
    await fs.writeFile(path.join(testDir, 'test.txt'), 'This is a test file.');

    // Run the archive function
    await archive(testDir, outputFile);

    // Check if the output file was created
    try {
        await fs.access(outputFile);
        console.log('Test passed: Output file created successfully.');
    } catch (error) {
        console.error('Test failed: Output file not created.');
    } finally {
        // Clean up
        await fs.rm(testDir, { recursive: true, force: true });
        await fs.unlink(outputFile);
    }
}

runTest();
