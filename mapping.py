from urllib.parse import unquote_plus
import configs


class Mapping:

    def __init__(self, name) -> None:
        self._name = name
        self._parameter = []
        self._rule_keys = []
        self._source_tables = []
        self._target_tables = []
        self._joiners = []
        self._message = None
        self._flag = None
        self._lookup = None

    def createParameters(self, parameter_field) -> None:
        for parameter in parameter_field:
            self._parameter.append(
                (parameter.get('name'), parameter[0].get('valueLiteral')))

    def createRuleKeys(self, exp_fields) -> None:
        for exp_field in exp_fields:
            if exp_field.get('name') == "ID_SISTEMA" or \
                    exp_field.get('name') == "ID_PROGR_CONTROLLO" or \
                    (exp_field.get('name') == "ID_PROGR_OCCORRENZA" or exp_field.get('name') == "ID_PROGR_OCCORENZA"):
                expression = exp_field.get('expression')
                if expression is None:
                    self._rule_keys.append((None, None))
                else:
                    decoded_exp = unquote_plus(
                        expression).replace("'", "")
                    if exp_field.get('name') == "ID_PROGR_OCCORRENZA" or exp_field.get('name') == "ID_PROGR_OCCORENZA":
                        self._rule_keys.append(
                            ("ID_PROGR_OCCORRENZA", decoded_exp))
                    else:
                        self._rule_keys.append(
                            (exp_field.get('name'), decoded_exp))

    def createFlag(self, exp_fields) -> None:
        flag = None
        for exp_field in exp_fields:
            if (exp_field.get('name') == 'FLG_ATTIVO' or
                exp_field.get('name') == 'FLG_ATTIVO_LKP' or
                exp_field.get('name') == 'FLG_ATTIVO1') and \
                    exp_field.get('input') == 'true':
                flag = 1
            if (exp_field.get('name') == 'FLG_ATTIVO1' or exp_field.get(
                    'name') == 'FLG_ATTIVO') and 'input' not in exp_field.keys():
                flag = 0
                break
        if flag is None:
            flag = 0
        self._flag = flag

    def createSourceTables(self, abstract_transformation) -> None:
        filter_condition = abstract_transformation[0].get(
            'filterCondition')
        if filter_condition is None:
            source_table = (abstract_transformation.get('name'), None)
        else:
            decoded_filter = unquote_plus(
                filter_condition).replace("\'", '"')
            source_table = (abstract_transformation.get(
                'name'), decoded_filter)
        self._source_tables.append(source_table)

    def createTargetTables(self, abstract_transformation) -> None:
        pre_sql = abstract_transformation[0].get('preSQL')
        if pre_sql is None:
            target_table = (abstract_transformation.get('name'), None)
        else:
            decoded_sql = unquote_plus(
                pre_sql).replace("\'", '"')
            target_table = (abstract_transformation.get('name'), decoded_sql)
        self._target_tables.append(target_table)

    def createFirstJoiners(self, abstract_transformation, join_interfaces) -> None:
        table_name = ""
        for join_interface in join_interfaces:
            if join_interface.get(configs.TYPE_STRING) == 'joiner:JoinerDataInterface' and \
                    (join_interface.get('name') == 'Detail' or join_interface.get('name') == 'Master'):
                table_type = join_interface.get('name')
                join_fields = join_interface[0]
                for join_field in join_fields:
                    table_name = join_field.get('name')
                    if 'Sorter' not in table_name:
                        self._joiners.append((table_type, table_name))
        if 'Sorter' not in table_name:
            join_condition = abstract_transformation.get('joinCondition')
            if join_condition is None:
                self._joiners.append(None)
            else:
                decoded_join_condition = unquote_plus(
                    join_condition).replace("\'", '"')
                self._joiners.append(
                    ("Prima condizione di join", decoded_join_condition))

    def createSecondJoiners(self, abstract_transformation, join_interfaces) -> None:
        len_join_fields = 0
        table_name = ""
        for join_interface in join_interfaces:
            if join_interface.get(configs.TYPE_STRING) == 'joiner:JoinerDataInterface' and join_interface.get(
                    'name') == 'Detail':
                table_type = join_interface.get('name')
                join_fileds = join_interface[0]
                len_join_fields = len(join_fileds)
                if len_join_fields == 1:
                    for join_field in join_fileds:
                        table_name = join_field.get('name')
                        if 'Sorter' not in table_name:
                            self._joiners.append((table_type, table_name))
        if 'Sorter' not in table_name:
            join_condition = abstract_transformation.get('joinCondition')
            if join_condition is None:
                self._joiners.append(None)
            else:
                if len_join_fields == 1:
                    decoded_join_condition = unquote_plus(
                        join_condition).replace("\'", '"')
                    self._joiners.append(
                        ("Seconda condizione di join", decoded_join_condition))

    def createMessage(self, exp_fields) -> None:
        message = None
        for exp_field in exp_fields:
            if exp_field.get('name') == 'MESSAGGIO':
                expression = exp_field.get('expression')
                if expression is None:
                    message = None
                else:
                    decoded_exp = unquote_plus(
                        expression).replace("'", "")
                    message = decoded_exp
        self._message = message

    def getName(self) -> str:
        return self._name

    def getParameter(self) -> list:
        return self._parameter

    def getRuleKeys(self) -> list:
        return self._rule_keys

    def getSourceTables(self) -> list:
        return self._source_tables

    def getTargetTables(self) -> list:
        return self._target_tables

    def getJoiners(self) -> list:
        return self._joiners

    def getMessage(self) -> str:
        return self._message

    def getFlag(self) -> str:
        return self._flag

    def getLookup(self) -> str:
        return self._lookup

    def updateParameter(self, parameter) -> None:
        self._parameter = parameter

    def updateRuleKeys(self, rule_keys) -> None:
        self._rule_keys = rule_keys

    def updateSourceTables(self, source_tables) -> None:
        self._source_tables = source_tables

    def updateTargetTables(self, target_tables) -> None:
        self._target_tables = target_tables

    def updateJoiners(self, joiners) -> None:
        self._joiners = joiners

    def updateMessage(self, message) -> None:
        self._message = message

    def updateFlag(self, flag) -> None:
        self._flag = flag

    def updateLookup(self, lookup) -> None:
        self._lookup = lookup
