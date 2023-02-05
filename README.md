# docker-selenium-lambda

This is minimum demo of headless chrome and selenium on container image on AWS Lambda

This image goes with these versions. [These are automatically updated and tested everyday. ![CircleCI](https://circleci.com/gh/umihico/docker-selenium-lambda/tree/circleci.svg?style=svg)](https://circleci.com/gh/umihico/docker-selenium-lambda/tree/circleci)

- Python 3.9.16
- chromium 109.0.5414.0
- chromedriver 109.0.5414.74
- selenium 4.7.2


## Running the demo

```bash
$ npm install -g serverless # skip this line if you have already installed Serverless Framework
$ export AWS_REGION=us-east-2 # You can specify region or skip this line. us-east-1 will be used by default.
$ sls create --template-url "https://github.com/umihico/docker-selenium-lambda/tree/main" --path docker-selenium-lambda-status-pay-sii && cd $_
$ sls deploy
$ sls invoke --function demo # Yay! You will get texts of example.com
```

## Public image is available

If you want your image simplier and updated automatically, rewrite the Dockerfile with the following commands:

```Dockerfile
FROM umihico/aws-lambda-selenium-python:latest

COPY main.py ./
CMD [ "main.handler" ]
```

Available tags are listed [here](https://hub.docker.com/r/umihico/aws-lambda-selenium-python/tags)

## Side Project

If you don't want to create functions each time for each purpose, Please check out [pythonista-chromeless](https://github.com/umihico/pythonista-chromeless)

Request URL: https://www4.sii.cl/rfiInternet/sdiFacade
Payload
7|0|6|https://www4.sii.cl/rfiInternet/|5354C0180C1194509A67D5791F548F89|cl.sii.sdi.core.web.client.service.SdiFacade|getMessage|java.lang.String/2004016611|Opciones|1|2|3|4|1|5|6|

Request URL: https://www4.sii.cl/rfiInternet/sdiFacade
7|0|6|https://www4.sii.cl/rfiInternet/|5354C0180C1194509A67D5791F548F89|cl.sii.sdi.core.web.client.service.SdiFacade|getMessage|java.lang.String/2004016611|Opciones|1|2|3|4|1|5|6|

Request URL: https://www4.sii.cl/rfiInternet/formularioFacade
7|0|17|https://www4.sii.cl/rfiInternet/|E86EB53FD057A52547AE8380EDAB209A|cl.sii.sdi.dim.rfi.web.client.service.FormularioFacade|findBorradorCnFecha|java.lang.String/2004016611|cl.sii.sdi.dim.rfi.to.Formulario/1008995664|cl.sii.sdi.dim.rfi.to.Periodo/4231800438|10480522|java.lang.Boolean/476441737|0|029|Formulario 29 - Banco en Línea|java.lang.Integer/3438268394|java.sql.Timestamp/3040052672|Formulario 29|M|7761892\!77777777|1|2|3|4|3|5|6|7|8|6|9|0|-2|-2|-2|-2|-2|-2|-2|9|1|10|11|12|0|13|2|14|F$EFxuA|0|15|16|14|TTYdDqY|0|-3|-2|-3|-3|-3|10|-3|17|0|1|7|13|2022|13|6|

7|0|4|https://www4.sii.cl/rfiInternet/|5354C0180C1194509A67D5791F548F89|cl.sii.sdi.core.web.client.service.SdiFacade|isAutenticationAvailable|1|2|3|4|0|