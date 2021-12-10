import utils


if __name__ == '__main__':
    json_path_file, summary_path_file, table_path_file, output_file, all_keys, workflow_name = utils.initializeParser()
    utils.generateJSON(json_path_file, output_file, all_keys)
    print(f"Generated {workflow_name}.json file.")
    utils.generateTXT(json_path_file, summary_path_file)
    print(f"Generated {workflow_name}.txt summary file.")
    utils.generateTable(json_path_file, table_path_file)
    print(f"Generated {workflow_name}_table.txt table file.\n")
