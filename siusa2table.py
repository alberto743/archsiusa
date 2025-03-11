#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2025 Alberto Previti
#
# SPDX-License-Identifier: MPL-2.0

'''Convert SIUSA XML database to tabular format'''

import argparse
import xml.etree.ElementTree as ET
import html
import pandas as pd


namespaces = {
    'icar-import': "http://www.san.beniculturali.it/icar-import",
    'xlink': "http://www.w3.org/1999/xlink",
    'dc': "http://purl.org/dc/elements/1.1/",
    'mets': "http://www.loc.gov/METS/",
    'metsrights': "http://cosimo.stanford.edu/sdr/metsrights/",
    'mix': "http://www.loc.gov/mix/v20",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'ead': "http://ead3.archivists.org/schema/",
    'eac': "urn:isbn:1-931666-33-4",
    'scons': "http://www.san.beniculturali.it/scons2"
}


def parse_scons(elem, xmlns):
    denominazione_data = elem.find('scons:denominazione', xmlns).text
    denominazione = html.unescape(denominazione_data)
    tipologia = elem.find('scons:tipologia', xmlns).text
    localizzazione = elem.find('scons:localizzazioni/scons:localizzazione', xmlns)
    indirizzo = localizzazione.find('scons:indirizzo', xmlns)
    paese = indirizzo.attrib['paese']
    provincia = indirizzo.attrib['provincia']
    comune = indirizzo.attrib['comune']
    cap = indirizzo.attrib['cap']
    via = indirizzo.text
    telefono_elem = localizzazione.find('scons:contatto/[@tipo="telefono"]', namespaces)
    telefono = telefono_elem.text if telefono_elem is not None else None
    fax_elem = localizzazione.find('scons:contatto/[@tipo="fax"]', namespaces)
    fax = fax_elem.text if fax_elem is not None else None
    sitoweb_elem = localizzazione.find('scons:contatto/[@tipo="sitoweb"]', namespaces)
    sitoweb = sitoweb_elem.text if sitoweb_elem is not None else None
    mail_elem = localizzazione.find('scons:contatto/[@tipo="mail"]', namespaces)
    mail = mail_elem.text if mail_elem is not None else None
    return {
        'denominazione': denominazione,
        'tipologia': tipologia,
        'paese': paese,
        'provincia': provincia,
        'comune': comune,
        'cap': cap,
        'via': via,
        'telefono': telefono,
        'fax': fax,
        'sitoweb': sitoweb,
        'mail': mail
    }


def extract_table(dbxml, xmlns):
    tree = ET.parse(dbxml)
    root = tree.getroot()

    records = root.find('icar-import:listRecords', xmlns)
    records_data = list()

    for record in records.findall('icar-import:record', xmlns):
        record_type = record.find('icar-import:recordHeader', xmlns).attrib['type']
        record_body = record.find('icar-import:recordBody', xmlns)

        if record_type == 'scons':
            records_data.append(parse_scons(record_body.find('scons:scons', xmlns), xmlns))

    return pd.DataFrame(records_data)


def main(namespacesxml):
    argparser = argparse.ArgumentParser(description='Extract table from a text file')
    argparser.add_argument('siusaxml', help='SIUSA database XML')
    argparser.add_argument('outtable', help='Table filename')
    args = argparser.parse_args()

    df = extract_table(args.siusaxml, namespacesxml)
    df.to_excel(f"{args.outtable}.xlsx")
    df.to_csv(f"{args.outtable}.csv")


if __name__ == '__main__':
    main(namespaces)
