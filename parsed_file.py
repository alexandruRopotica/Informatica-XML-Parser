import configs


class ParsedXML():

    def __init__(self, input_xml):
        self._parsed_xml = input_xml
        self._workflow_name = None
        self._folder_fields = []
        self._project_fields = []
        self._mapping_fields = []
        self._workflow_field = None
        self._all_keys = {}
        self._keys_to_mapping = {}

    def createWorkflowField(self):
        for field in self._parsed_xml:
            field_name = field.tag.split("}")[1]
            if field_name == "Workflow":
                self._workflow_field = field

    def createRemainingFields(self):
        for key in self._all_keys:
            for field in self._parsed_xml:
                field_name = field.tag.split("}")[1]
                if field_name == "Folder":
                    contents_field = field[0]
                    for io_object in contents_field:
                        if io_object.get(configs.ID_STRING) == key:
                            self._folder_fields.append(
                                (self._all_keys.get(key), io_object))
                elif field_name == "Mapping":
                    if field.get(configs.ID_STRING) == key:
                        self._mapping_fields.append(
                            (self._all_keys.get(key), field))
                elif field_name == "Project":
                    contents_field = field[2]
                    for id_object in contents_field:
                        if configs.IDREF_STRING not in id_object.attrib.keys():
                            if id_object.get('name') in configs.DIR_NAME:
                                id_obj_contents = id_object[0]
                                for id_obj_content in id_obj_contents:
                                    if configs.IDREF_STRING not in id_obj_content.attrib.keys():
                                        if id_obj_content.get(configs.ID_STRING) == key:
                                            self._project_fields.append(
                                                (self._all_keys.get(key), id_obj_content))

    def createWorkflowName(self):
        self._workflow_name = self._workflow_field.get('name')

    def createAllKeys(self):
        for sub_field in self._workflow_field:
            if sub_field.tag == "taskInstances":
                task_instances = sub_field
                for task_instance in task_instances:
                    if task_instance.get('name')[0] == 'm':
                        key = task_instance[0].get('mapping')
                        value = task_instance.get('name')
                        self._all_keys[key] = value

    def getFolderFields(self):
        return self._folder_fields

    def getMappingFields(self):
        return self._mapping_fields

    def getProjectFields(self):
        return self._project_fields

    def getWorkflowFields(self):
        return self._workflow_fields

    def getWorkflowName(self):
        return self._workflow_name

    def getAllKeys(self):
        return self._all_keys
