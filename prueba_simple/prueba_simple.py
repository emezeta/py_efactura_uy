#!/usr/bin/python
# coding: utf-8


import datetime
import xml.dom.minidom
from pysimplesoap.client import SoapClient, SimpleXMLElement
from pysimplesoap.wsse import BinaryTokenSignature
from pysimplesoap import xmlsec


fechacfe = lambda *x: datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-03:00")

LOCATION = "https://efactura.dgi.gub.uy:6443/ePrueba/ws_eprueba?wsdl"
ACTION = "http://dgi.gub.uyaction/"


with open("documento.xml") as f:
    dataCFE = f.read()

cfe = SimpleXMLElement(dataCFE)

caratula = cfe("DGICFE:Caratula")
setattr(caratula, "DGICFE:Fecha", fechacfe())


# leer el certificado (PEM) del emisor y agregarlo
cert_lines = open("certificado.crt").readlines()
cert_fmt = [line for line in cert_lines if not line.startswith("---")]
cert_pem =  ''.join(cert_fmt)
setattr(caratula, "DGICFE:X509Certificate", cert_pem)


cfeXML = cfe("ns0:CFE")

# preparar la plantilla para la info de firma con los namespaces padres (CFE)

plantilla = SimpleXMLElement(xmlsec.SIGN_ENV_TMPL)
plantilla["xmlns:DGICFE"] = plantilla["xmlns:ns0"] = "http://cfe.dgi.gub.uy"

vars = xmlsec.rsa_sign(cfeXML.write_c14n(), '', "private.key", 'la passphrase',
                   sign_template=plantilla.as_xml(), c14n_exc=False,
                   cert=''.join(cert_lines),
                   key_info_template=xmlsec.KEY_INFO_X509_TMPL,
                   #key_info_template=xmlsec.KEY_INFO_RSA_TMPL,
                  )

firma_xml = (xmlsec.SIGNATURE_TMPL % vars)
cfeXML.import_node(SimpleXMLElement(firma_xml))

# guardo el xml firmado para depuración
open("cfe_firmado.xml", "w").write(cfe.as_xml())

# serializar CDATA según el ejemplo
cdata = xml.dom.minidom.CDATASection()
cdata.data = cfeXML.as_xml()

# construir los parámetros de la llamada al webservice (requerimiento):
cabezal = """<dgi:WS_eFactura.EFACRECEPCIONSOBRE xmlns:dgi="http://dgi.gub.uy"/>"""
param = SimpleXMLElement( cabezal,
                          namespace="http://dgi.gub.uy",
                          prefix="dgi" )

data_in = param.add_child("Datain", ns=True)
data_in.add_child("xmlData", cdata, ns=True)

# Instancio el cliente para consumir el webservice
client = SoapClient(LOCATION, ACTION,
                    namespace="http://dgi.gub.uy",
                    ns="dgi",
                    soap_ns="soapenv", trace=True)

# agregar seguridad WSSE (mensaje firmado digitalmente para autenticacion)
#     usar el certificado unico asociado al RUT emisor emitidos por la
#     Administración Nacional de Correos (CA: autoridad certificadora actual)

plugin = BinaryTokenSignature(certificate="certificado.crt",
                              private_key="private.key",
                              password=None,
                              cacert="CorreoUruguayoCA.crt",
                              )
client.plugins += [plugin]

# llamar al método remoto
ret = client.call("AWS_EFACTURA.EFACRECEPCIONSOBRE", param)
