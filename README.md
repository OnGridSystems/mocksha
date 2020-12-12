# Mocksha - Lightweight mock for HTTP services

Self-adjusting and easy to setup and use mock based on aiohttp that replaces external webservices in CI/CD environment. Makes it easy to emulate third-party resources like API endpoints, microservices, sites, gateways.

Mocksha has two modes of oparation: record and replay.

## Record mode - intercepts ans saves HTTP requests to YAML files

install required packages

```
pip install -r requirements.txt
```

Provide the external server URI via env 

`export UPSTREAM=https://centrobank:1234/api/exchange/`

Start the server on the given port 

`python -m aiohttp.web -H localhost -P 8080 app:init_func`

Interact with it

```
curl http://localhost:8080/usd_eur
curl http://localhost:8080/eur_usd
```

The requests and responses are recorded to human-readable and editable YAML files

```
ls -la
0001_req.yml
0001_resp.yml
0002_req.yml
0003_resp.yml
```

Stop the server and adapt the YAML (remove unneccessary fields, add your own)


## Replay mode

In replay mode mocksha acts as a standalone webserver for the tested application and serves requests locally from the YAML files.

We don't need upstream URL anymore. 

`unset UPSTREAM`

Since it’s intended to emulate external resource in CI auto-tests, we made its execution limitable by time.

`export MAX_IDLE=60` defines the total amount of time in seconds allowed to be idle. Thes counter resets on each request. Default value is 0 - indefinite.

# Limitations

* Supports only HTTP
* Tested only on plaintext data

## Test

To run tests

`./run_tests.sh`

