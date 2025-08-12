var synthetics = require('Synthetics');
require('SyntheticsLogger');

apiCanaryBlueprint = async function () {
    const validateSuccessful = async function(response) {
        return new Promise((resolve, reject) => {
            if (response.statusCode < 200 || response.statusCode > 299) {
                throw response.statusCode + ' ' + response.statusMessage;
            }
            let responseBody = '';
            response.on('data', (d) => { responseBody += d; });
            response.on('end', () => { resolve(); });
        });
    };

    let requestOptionsStep1 = {
        hostname: process.env.APP_ENDPOINT,
        method: 'POST',
        path: '/encrypt',
        port: '80',
        protocol: 'http:',
        body: JSON.stringify({ Name: "Test User", Text: "This Message is a Test!" }),
        headers: { "Content-Type": "application/json" }
    };

    requestOptionsStep1['headers']['User-Agent'] = [
      synthetics.getCanaryUserAgentString(), requestOptionsStep1['headers']['User-Agent']
    ].join(' ');

    let stepConfig1 = {
        includeRequestHeaders: true,
        includeResponseHeaders: true,
        includeRequestBody: true,
        includeResponseBody: true,
        restrictedHeaders: [],
        continueOnHttpStepFailure: true
    };

    await synthetics.executeHttpStep('Verify', requestOptionsStep1, validateSuccessful, stepConfig1);
};

exports.handler = async () => { return await apiCanaryBlueprint(); };