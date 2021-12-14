import configs


def check_parameters(parameters) -> str:
    if len(parameters) != 2:
        return 'X'
    else:
        return 'OK'


def check_filter(source_tables) -> str:
    all_source_tables_checked = True
    for source_table in source_tables:
        table_filter = source_table[1]
        if table_filter is None:
            all_source_tables_checked = False
        elif configs.DATE_STRING not in table_filter or configs.ABI_STRING not in table_filter:
            all_source_tables_checked = False
        else:
            table_filter_tokens = table_filter.upper().split('AND')
            if len(table_filter_tokens) < 2:
                all_source_tables_checked = False
    if not all_source_tables_checked:
        return 'X'
    else:
        return 'OK'


def check_keys_and_SQL(keys, target_tables) -> str:
    string_keys = (
        f'ID_SISTEMA="{keys[0][1]}"', f'ID_PROGR_CONTROLLO="{keys[1][1]}"', f'ID_PROGR_OCCORRENZA="{keys[2][1]}"')
    abi_string = f'ABI IN {configs.ABI_STRING}'.lower()
    preSQLs = []
    presqls_checked = True
    for i in range(2):
        preSQLs.append(target_tables[i][1])
    for preSQL in preSQLs:
        try:
            tokens = preSQL.split(' ')
            abi_condition = preSQL.split('AND')[-1].lower()
        except:
            return 'X'
        else:
            if string_keys[0] not in tokens or string_keys[1] not in tokens or string_keys[
                2] not in tokens or abi_string not in abi_condition:
                presqls_checked = False
    if presqls_checked:
        return 'OK'
    else:
        return 'X'


def check_flag(flag, lkp_table_name) -> str:
    if flag == 1 or lkp_table_name == configs.LKP_TABLE_NAME:
        return 'OK'
    else:
        return 'X'


def check_message(message) -> str:
    if message is not None:
        return 'OK'
    else:
        return 'X'
