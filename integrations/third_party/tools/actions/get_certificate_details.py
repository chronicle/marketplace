# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import pprint
from collections import namedtuple
from datetime import datetime
from socket import socket

import idna
from cryptography import x509
from cryptography.x509.oid import NameOID
from OpenSSL import SSL
from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

HostInfo = namedtuple(field_names="cert hostname peername", typename="HostInfo")


def get_certificate(hostname, port):
    hostname_idna = idna.encode(hostname)
    sock = socket()

    sock.connect((hostname, port))
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.TLS_METHOD)
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()
    sock_ssl.close()
    sock.close()

    return HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)


def get_alt_names(cert):
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return None


def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        # cmp = cert.issuer.get_components()
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_json_result(hostinfo):
    common_name = get_common_name(hostinfo.cert)
    san = (get_alt_names(hostinfo.cert),)
    issuer = get_issuer(hostinfo.cert)

    now = datetime.now()
    delta = hostinfo.cert.not_valid_after - now
    days_to_expiration = delta.days
    is_expired = days_to_expiration < 0
    is_self_signed = common_name == issuer
    date_time = hostinfo.cert.not_valid_before.strftime("%m/%d/%Y")

    cert_details = {
        "hostname": hostinfo.hostname,
        "ip": hostinfo.peername[0],
        "commonName": common_name,
        "is_self_signed": is_self_signed,
        "SAN": san,
        "is_expired": is_expired,
        "issuer": issuer,
        "not_valid_before": hostinfo.cert.not_valid_before.strftime("%m/%d/%Y"),
        "not_valid_after": hostinfo.cert.not_valid_after.strftime("%m/%d/%Y"),
        "days_to_expiration": days_to_expiration,
    }

    return cert_details


@output_handler
def main():
    siemplify = SiemplifyAction()

    url = siemplify.extract_action_param("Url to check", print_value=True)
    hostinfo = get_certificate(url, 443)
    json_res = get_json_result(hostinfo)
    output_message = f"Url Certificate <{url}> was successfully analyzed."
    pprint.pprint(json_res)
    print(json_res)
    siemplify.result.add_result_json(json_res)

    siemplify.end(output_message, True, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
