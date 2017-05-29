py_efactura_uy error al enviar cfe
==================================

Ejecutando el código en modo normal, se recibe este error:

```
    DEBUG:pysimplesoap.client:status: 500
    x-backside-transport: FAIL FAIL
    connection: close
    content-type: text/xml; charset="UTF-8"
    DEBUG:pysimplesoap.client:

    <?xml version='1.0' ?>
        <env:Envelope xmlns:env='http://schemas.xmlsoap.org/soap/envelope/'>
            <env:Body>
                <env:Fault>
                    <faultcode>env:Client</faultcode>
                    <faultstring>Internal Error</faultstring>
                </env:Fault>
            </env:Body>
        </env:Envelope>
```


En cambio, puesto en debug aparece esto otro.

```
    .... /pysimplesoap/client.py(257)call()
        255         import ipdb;ipdb.set_trace()
        256         self.xml_request = request.as_xml()
    --> 257         self.xml_response = self.send(method, self.xml_request)
        258         response = SimpleXMLElement(self.xml_response,
    namespace=self.namespace,
        259                                     jetty=self.__soap_server in
    ('jetty',))

    ipdb> n
    RelativeURIError: Relative...Action',)

    ipdb> n
    --Return--
    None

    RelativeURIError: Only absolute URIs are allowed. uri = SOAPAction

```








