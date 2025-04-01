import aws_cdk.aws_s3 as s3
from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import CfnOutput, Duration, RemovalPolicy
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class HelloCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create an sns service
        # create a lambda function that says hello world

        bucket = s3.Bucket(
            self,
            "MyFirstBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        my_function = _lambda.Function(
            self, "HelloWorldFunction", 
            runtime=_lambda.Runtime.NODEJS_20_X,  # Provide any supported Node.js runtime
            handler="index.handler",
            code=_lambda.Code.from_inline(
                f"""
                const {{ S3Client, PutObjectCommand }} = require("@aws-sdk/client-s3"); // Importing S3Client and PutObjectCommand

                const s3 = new S3Client(); // Initializing the S3 client

                exports.handler = async (event) => {{
                    const bucketName = "{bucket.bucket_name}"; // Dynamically interpolated bucket name
                    const fileName = "output.txt";
                    const fileContent = "Hello Nikola! This is a file written to S3.";

                    try {{
                        // Write a new file to the S3 bucket
                        await s3.send(new PutObjectCommand({{
                            Bucket: bucketName,
                            Key: fileName,
                            Body: fileContent,
                        }}));

                        console.log(`File written to bucket: ${{bucketName}}, key: ${{fileName}}`);

                        return {{
                            statusCode: 200,
                            body: JSON.stringify('File successfully written to S3!'),
                        }};
                    }} catch (error) {{
                        console.error("Error writing to S3:", error);
                        return {{
                            statusCode: 500,
                            body: JSON.stringify('Failed to write to S3.'),
                        }};
                    }}
                }};
                """
            ),
        )

        # we add a function URL to the stack output
        my_function_url = my_function.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.AWS_IAM,
        )

        # we need to grant the lambda function permissions to write to the bucket
        bucket.grant_write(my_function)
        bucket.grant_put(my_function)

        # create a second lambda which reads from the s3 bucket and prints the contents
        lambda_function2 = _lambda.Function(
            self, "HelloWorldFunctionReader",
            runtime=_lambda.Runtime.NODEJS_20_X,  # Provide any supported Node.js runtime
            handler="index.handler",
            code=_lambda.Code.from_inline(
                f"""
                const {{ S3Client, GetObjectCommand }} = require("@aws-sdk/client-s3"); // Importing S3Client and GetObjectCommand

                const s3 = new S3Client(); // Initializing the S3 client

                exports.handler = async (event) => {{
                    const bucketName = "{bucket.bucket_name}"; // Dynamically interpolated bucket name
                    const fileName = "output.txt";

                    try {{
                        // Read the file from the S3 bucket
                        const data = await s3.send(new GetObjectCommand({{
                            Bucket: bucketName,
                            Key: fileName,
                        }}));
                        // Convert the stream to a string
                        const streamToString = (stream) => {{
                            return new Promise((resolve, reject) => {{
                                const chunks = [];
                                stream.on('data', (chunk) => {{
                                    chunks.push(chunk);
                                }});
                                stream.on('end', () => {{
                                    resolve(Buffer.concat(chunks).toString('utf-8'));
                                }});
                                stream.on('error', reject);
                            }});
                        }};


                        console.log(`File read from bucket: ${{bucketName}}, key: ${{fileName}}`);

                        return {{
                            statusCode: 200,
                            // print the data from the file
                            body: JSON.stringify({{
                                message: 'File successfully read from S3!',
                                data: await streamToString(data.Body),
                            }}),
                        }};
                    }} catch (error) {{
                        console.error("Error reading from S3:", error);
                        return {{
                            statusCode: 500,
                            body: JSON.stringify('Failed to read from S3.'),
                        }};
                    }}
                }};
                """
            ),
        )

        bucket.grant_read(lambda_function2)

        my_function2_url = lambda_function2.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.AWS_IAM,
        )
        # print the url to the console when cdksynth
        print("Function URL: ", my_function2_url.url)
        # output the function url to the console

