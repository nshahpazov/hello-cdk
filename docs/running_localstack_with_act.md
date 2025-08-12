# Running localstack with act

You need to run localstack docker container
```bash
docker run --rm -it --network my_network -p 4566:4566 \
    -v /var/run/docker.sock:/var/run/docker.sock \ 
    localstack/localstack \
    --privileged
```

- It needs to be run in privileged mode to allow localstack to run docker containers.
- It needs to share the same network as the act container to allow localstack to communicate with the act container.

After that we run act with the following command:
```bash
act --network my_network -j deploy
```
- The `--network` flag is used to specify the network that the act container should use to communicate with the localstack container.

Sometimes you need to restart the localstack container to make sure it is running properly as it can be a bit flaky.
Also, hwn specifying the endpoint url, make sure to use the ip address of the localstack container, not localhost.
