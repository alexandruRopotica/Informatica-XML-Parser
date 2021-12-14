import io
import json
import os
import textwrap
import configs
from operator import itemgetter
import xml.etree.ElementTree as ET
from parsed_file import ParsedXML
from mapping import Mapping
from tabulate import tabulate
import checks as CK


def createDirectories():
    if not os.path.isdir(configs.JSON_PATH):
        os.mkdir(configs.JSON_PATH)
        print("\nCreated jsons directory.")
    else:
        print("\nJsons directory already exists.")
    if not os.path.isdir(configs.SUMMARY_PATH):
        os.mkdir(configs.SUMMARY_PATH)
        print("Created workflows summary directory.")
    else:
        print("Workflows summary directory already exists.")
    if not os.path.isdir(configs.TABLE_PATH):
        os.mkdir(configs.TABLE_PATH)
        print("Created tables directory.\n")
    else:
        print("Tables directory already exists.\n")


def parseXMLFile():
    workflow = ET.parse(configs.FILE_PATH)
    print(f"Parsing {configs.FILE_NAME} ...")
    parsed_xml = workflow.getroot()
    print("Parsing completed.\n")
    return parsed_xml


def createParsedXML(input_xml):
    parsed_xml = ParsedXML(input_xml)
    parsed_xml.createWorkflowField()
    parsed_xml.createAllKeys()
    parsed_xml.createRemainingFields()
    parsed_xml.createWorkflowName()
    return parsed_xml


def createMappings(field_list) -> list:
    mapping_list = []
    for mapping_name, fields in field_list:
        mapping = Mapping(mapping_name)
        message_checked = False
        for sub_field in fields:
            if sub_field.tag == 'parameters':
                mapping.createParameters(sub_field)
            if sub_field.tag == 'transformations':
                for abstract_transformation in sub_field:
                    if abstract_transformation.get('name') == 'Exp_INPUT_VALORI':
                        exp_fields = abstract_transformation[0][0][0]
                        mapping.createRuleKeys(exp_fields)
                    elif abstract_transformation.get('name') == 'Exp_OUTPUT_LKP_ATTIVAZ_CONTROLLO':
                        exp_fields = abstract_transformation[0][0][0]
                        mapping.createFlag(exp_fields)
                        mapping.createMessage(exp_fields)
                        if mapping.getMessage() is not None:
                            message_checked = True
                    elif abstract_transformation.get('name') == 'Expression' or \
                            abstract_transformation.get('name') == 'Exp_OUTPUT_LKP' or \
                            abstract_transformation.get('name') == 'Expression1':
                        exp_fields = abstract_transformation[0][0][0]
                        mapping.createFlag(exp_fields)
                    elif abstract_transformation.get(configs.TYPE_STRING) == 'source:SourceTx':
                        mapping.createSourceTables(abstract_transformation)
                    elif abstract_transformation.get(configs.TYPE_STRING) == 'target:TargetTx':
                        mapping.createTargetTables(abstract_transformation)
                    elif abstract_transformation.get(
                            configs.TYPE_STRING) == 'joiner:JoinerTx' and abstract_transformation.get(
                        'name') == 'Joiner':
                        join_interfaces = abstract_transformation[0]
                        mapping.createFirstJoiners(
                            abstract_transformation, join_interfaces)
                    elif abstract_transformation.get(
                            configs.TYPE_STRING) == 'joiner:JoinerTx' and abstract_transformation.get(
                        'name') == 'Joiner1':
                        join_interfaces = abstract_transformation[0]
                        mapping.createSecondJoiners(
                            abstract_transformation, join_interfaces)
                    elif abstract_transformation.get(
                            configs.TYPE_STRING) == 'lookup:LookupTx' and abstract_transformation.get(
                        'name') == configs.LKP_TABLE_NAME:
                        mapping.updateLookup(
                            abstract_transformation.get('name'))
                    if not message_checked and (
                            abstract_transformation.get(configs.TYPE_STRING) == 'expression:ExpressionTx' or
                            abstract_transformation.get('name').lower() == 'custom_message'):
                        exp_fields = abstract_transformation[0][0][0]
                        mapping.createMessage(exp_fields)
        mapping_list.append(mapping)
    return mapping_list


def addMappingsToJSON(mappings, output_file) -> dict:
    for mapping in mappings:
        output_file[mapping.getName()] = {"Parametri": mapping.getParameter(),
                                          "Chiavi controllo": mapping.getRuleKeys(),
                                          "Tabelle sorgenti": mapping.getSourceTables(),
                                          "Tabelle target": mapping.getTargetTables(),
                                          "Join": mapping.getJoiners(),
                                          "Messaggio": mapping.getMessage(),
                                          "Flag attivo": mapping.getFlag(),
                                          "Tabella lookup": mapping.getLookup()}
    return output_file


def sortJSONByRuleKeys(output_file) -> dict:
    sorted_output_file = {}
    dict_to_sort = {}
    for entry in output_file:
        key = (int(output_file.get(entry)['Chiavi controllo'][1][1]), int(
            output_file.get(entry)['Chiavi controllo'][2][1]))
        dict_to_sort[key] = entry
    sorted_keys = sorted(dict_to_sort, key=itemgetter(0, 1))
    for key in sorted_keys:
        mapping_name = dict_to_sort[key]
        sorted_output_file[mapping_name] = output_file.get(mapping_name)
    return sorted_output_file


def initializeParser() -> [str, str, str, dict, dict, str]:
    createDirectories()
    output_file = {}
    input_xml = parseXMLFile()
    parsed_xml = createParsedXML(input_xml)
    workflow_name = parsed_xml.getWorkflowName()
    json_path_file = os.path.join(configs.JSON_PATH, workflow_name + '.json')
    summary_path_file = os.path.join(
        configs.SUMMARY_PATH, workflow_name + '.txt')
    table_path_file = os.path.join(
        configs.TABLE_PATH, workflow_name + '_table.txt')
    for field_list in [parsed_xml.getFolderFields(), parsed_xml.getProjectFields(), parsed_xml.getMappingFields()]:
        mappings = createMappings(field_list)
        output_file = addMappingsToJSON(mappings, output_file)
    return json_path_file, summary_path_file, table_path_file, output_file, parsed_xml.getAllKeys(), workflow_name


def generateJSON(json_path, output_file, all_keys) -> None:
    with open(json_path, 'w') as f:
        try:
            sorted_output_file = sortJSONByRuleKeys(output_file)
        except:
            print(
                "Rule keys missing. Can't sort .json entries, the output file won't be sorted")
            json.dump(output_file, f, ensure_ascii=True, indent=4)
        else:
            if len(sorted_output_file.keys()) != len(all_keys):
                json.dump(output_file, f, ensure_ascii=True, indent=4)
            else:
                json.dump(sorted_output_file, f, ensure_ascii=True, indent=4)


def generateTXT(json_path, txt_path) -> None:
    with open(json_path) as json_file:
        with open(txt_path, 'a', encoding='utf-8') as txt_file:
            txt_file.seek(0, 0)
            txt_file.truncate()
            mappings = json.load(json_file)
            for mapping in mappings:
                output_mapping_info = io.StringIO()
                output_mapping_info.write('\n')
                output_mapping_info.write(mapping)
                output_mapping_info.write('\n')
                try:
                    dt_riferimento = mappings.get(mapping)['Parametri'][0][0]
                    dt_riferimento_value = mappings.get(mapping)[
                        'Parametri'][0][1]
                    abi = mappings.get(mapping)['Parametri'][1][0]
                    abi_value = mappings.get(mapping)[
                        'Parametri'][1][1]
                except:
                    output_mapping_info.write("Nessun parametro impostato")
                else:
                    output_mapping_info.write(
                        f"I parametri del mapping sono {dt_riferimento}={dt_riferimento_value} e {abi}={abi_value}")
                output_mapping_info.write('\n')
                try:
                    id_sistema = mappings.get(
                        mapping)['Chiavi controllo'][0][0]
                    id_progr_controllo = mappings.get(
                        mapping)['Chiavi controllo'][1][0]
                    id_progr_occorrenza = mappings.get(
                        mapping)['Chiavi controllo'][2][0]
                    id_sistema_value = mappings.get(
                        mapping)['Chiavi controllo'][0][1]
                    id_progr_controllo_value = mappings.get(
                        mapping)['Chiavi controllo'][1][1]
                    id_progr_occorrenza_value = mappings.get(
                        mapping)['Chiavi controllo'][2][1]
                except:
                    output_mapping_info.write(
                        "Non ci sono chiavi di controllo")
                else:
                    output_mapping_info.write(
                        f"Le chiavi di controllo sono {id_sistema}={id_sistema_value}, {id_progr_controllo}={id_progr_controllo_value} e {id_progr_occorrenza}={id_progr_occorrenza_value}")
                output_mapping_info.write('\n')
                output_mapping_info.write("Le tabelle sorgenti sono:")
                output_mapping_info.write('\n')
                count_string = 1
                for source_table in mappings.get(mapping)['Tabelle sorgenti']:
                    table_name = source_table[0]
                    table_filter = source_table[1]
                    output_mapping_info.write(
                        f"\t- {table_name} con filtro {table_filter}")
                    if count_string != len(mappings.get(mapping)['Tabelle sorgenti']):
                        output_mapping_info.write('\n')
                        count_string += 1
                    else:
                        count_string = 1
                output_mapping_info.write('\n')
                output_mapping_info.write("Le tabelle target sono:")
                output_mapping_info.write('\n')
                for target_table in mappings.get(mapping)['Tabelle target']:
                    table_name = target_table[0]
                    table_sql = target_table[1]
                    output_mapping_info.write(
                        f"\t- {table_name} con pre-SQL {table_sql}")
                    if count_string != len(mappings.get(mapping)['Tabelle target']):
                        output_mapping_info.write('\n')
                        count_string += 1
                    else:
                        count_string = 1
                output_mapping_info.write('\n')
                if len(mappings.get(mapping)['Join']) == 0:
                    output_mapping_info.write("Non ci sono Join nel mapping\n")
                else:
                    output_mapping_info.write("Le tabelle di Join sono:")
                    output_mapping_info.write('\n')
                    joiner_list = mappings.get(mapping)['Join']
                    detail_label = joiner_list[0][0]
                    if joiner_list[0][1] == "ABI":
                        detail_table = "Read_MAPPA_GRUPPO_CCB"
                    else:
                        detail_table = joiner_list[0][1]
                    master_label = joiner_list[1][0]
                    master_table = joiner_list[1][1]
                    first_join_key = joiner_list[2][1]
                    if len(mappings.get(mapping)['Join']) == 3:
                        output_mapping_info.write(
                            f"\t- {master_table} ({master_label}) e {detail_table} ({detail_label}) con chiave")
                        output_mapping_info.write('\n')
                        output_mapping_info.write(f"\t\t {first_join_key}")
                        output_mapping_info.write('\n')
                    elif len(mappings.get(mapping)['Join']) == 5:
                        second_detail_label = joiner_list[3][0]
                        second_detail_table = joiner_list[3][1]
                        second_join_key = joiner_list[4][1]
                        output_mapping_info.write(
                            f"\t- {master_table} ({master_label}) e {detail_table} ({detail_label}) con chiave")
                        output_mapping_info.write('\n')
                        output_mapping_info.write(f"\t\t {first_join_key}")
                        output_mapping_info.write('\n')
                        output_mapping_info.write(
                            f"\t- L'output del precedente Join e\' in join con {second_detail_table} ({second_detail_label}) con chiave")
                        output_mapping_info.write('\n')
                        output_mapping_info.write(f"\t\t {second_join_key}")
                        output_mapping_info.write('\n')
                try:
                    message = mappings.get(mapping)['Messaggio'].replace(
                        "\r", "").replace("\n", " ")
                except:
                    message = mappings.get(mapping)['Messaggio']
                if message is None:
                    output_mapping_info.write(
                        'Campo MESSAGGIO non valorizzato\n')
                else:
                    output_mapping_info.write(
                        'Il valore del campo MESSAGGIO e\':')
                    output_mapping_info.write('\n')
                    wrapped_text = textwrap.wrap(message, width=120)
                    for text in wrapped_text:
                        output_mapping_info.write(f'\t{text}\n')
                lookup_name = mappings.get(mapping)['Tabella lookup']
                flag = mappings.get(mapping)['Flag attivo']
                if flag == 1:
                    output_mapping_info.write(
                        f"FLG_ATTIVO collegato da {lookup_name}")
                else:
                    output_mapping_info.write(
                        f"FLG_ATTIVO potrebbe non essere collegato da {lookup_name}")
                output_mapping_info.write('\n')
                txt_file.write(output_mapping_info.getvalue())


def generateTable(json_path, table_path) -> None:
    table = [['Mapping', 'Parametri', 'Filtro',
              'Coerenza Chiavi e PRESQL', 'Link FLG_ATTIVO e LOOKUP', 'MESSAGGIO valido']]
    with open(json_path) as json_file:
        mappings = json.load(json_file)
        for mapping in mappings:
            param_checked = CK.check_parameters(
                mappings.get(mapping)['Parametri'])
            filter_checked = CK.check_filter(
                mappings.get(mapping)['Tabelle sorgenti'])
            keys_sql_checked = CK.check_keys_and_SQL(mappings.get(
                mapping)["Chiavi controllo"], mappings.get(mapping)['Tabelle target'])
            flag_checked = CK.check_flag(mappings.get(
                mapping)['Flag attivo'], mappings.get(mapping)['Tabella lookup'])
            message_checked = CK.check_message(
                mappings.get(mapping)['Messaggio'])
            table.append([mapping, param_checked, filter_checked,
                          keys_sql_checked, flag_checked, message_checked])
    with open(table_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write('La "X" su Filtro può essere dato da\n')
        txt_file.write('\t- La mancanza del campo ABI_BANCA su una vista\n')
        txt_file.write(f'\t- Il filtro su DATA_RIFERIMENTO non è scritto in questo modo \'{configs.DATE_STRING}\'\n')
        txt_file.write(
            'La "X" sul Coerenza Chiavi e PRESQL può essere dato da\n')
        txt_file.write('\t- La mancanza di ID_PROGR_OCCORRENZA nel pre-SQL\n')
        txt_file.write(
            f'\t- La condizione su ABI nel pre-SQL non è scritto in questo modo \'ABI IN {configs.ABI_STRING}\'\n\n')
        txt_file.write(tabulate(table, headers='firstrow',
                                tablefmt='fancy_grid', showindex=range(1, len(mappings.keys()) + 1)))
