# config

These configuration classes define how to connect to a Zeebe instance.

Keys given in description must be used if you prefer to set up
connection using environmental variables.

In addition, you must set `CAMUNDA_CONNECTION_TYPE` to either
`SECURE`, `INSECURE` or `CAMUNDA_CLOUD`.

Example Cloud config:

``` py
from python_camunda_sdk import CloudConfig

config = CloudConfig(
    client_id='jYsgv.SryJYQlcpobk-tZZP~2R60xpNY',
    client_secret='55kddTbk~yZBFb2NH5GtebWHkSoK1z.TG7G1Hn-n.mH_f4ihpZAUop1-sryxHnyV',
    cluster_id='7bc802fc-7bf4-4800-b84a-596628d1ed08',
    region='bru-2'
)
```

Example Insecure config:

``` py
from python_camunda_sdk import InsecureConfig

config = InsecureConfig(
    host='127.0.0.1',
    port=26500
)
```

Example secure config:

```py
config = SecureConfig(
    host='127.0.0.1',
    port=26500,
    root_certificates='''
    -----BEGIN CERTIFICATE-----
    xxx
    -----BEGIN CERTIFICATE-----
    '''
    private_key='''
    -----BEGIN RSA PRIVATE KEY-----
    xxx
    -----BEGIN RSA PRIVATE KEY-----
    '''
    certificate_chain=''
)
```

::: python_camunda_sdk.runtime.config