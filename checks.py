import configs


def check_parameters(parameters):
    if len(parameters) != 2:
        return 'X'
    else:
        return 'OK'


def check_filter(source_tables):
    all_source_tables_checked = True
    for source_table in source_tables:
        filter = source_table[1]
        if filter is None:
            all_source_tables_checked = False
        elif configs.DATE_STRING not in filter or configs.ABI_STRING not in filter:
            all_source_tables_checked = False
    if not all_source_tables_checked:
        return 'X'
    else:
        return 'OK'


def check_keys_and_SQL(keys, target_tables):
    string_keys = (
        f'ID_SISTEMA="{keys[0][1]}"', f'ID_PROGR_CONTROLLO="{keys[1][1]}"', f'ID_PROGR_OCCORRENZA="{keys[2][1]}"')
    abi_string = f'ABI in {configs.ABI_STRING}'
    preSQLs = []
    for i in range(2):
        preSQLs.append(target_tables[i][1])
    for preSQL in preSQLs:
        try:
            tokens = preSQL.split(' ')
        except:
            return 'X'
        else:
            if string_keys[0] in tokens and string_keys[1] in tokens and abi_string in tokens:
                try:
                    last_token = string_keys[2] in tokens
                except:
                    if not last_token:
                        return 'X'
    return 'OK'


def check_flag(flag, lkp_table_name):
    if flag == 1 or lkp_table_name == configs.LKP_TABLE_NAME:
        return 'OK'
    else:
        return 'X'


def check_message(message):
    if message is not None:
        return 'OK'
    else:
        return 'X'
