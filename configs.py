import os
import sys

SYS_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
JSON_PATH = os.path.join(SYS_DIR_PATH, 'GENERATED_FILES/JSONS')
SUMMARY_PATH = os.path.join(SYS_DIR_PATH, 'GENERATED_FILES/WORKFLOW_SUMMARIES')
TABLE_PATH = os.path.join(SYS_DIR_PATH, 'GENERATED_FILES/TABLES')
FILE_NAME = sys.argv[1]
FILE_PATH = os.path.join(SYS_DIR_PATH, FILE_NAME)
ID_STRING = "{http://com.informatica.imx}id"
IDREF_STRING = "{http://com.informatica.imx}idref"
TYPE_STRING = "{http://www.w3.org/2001/XMLSchema-instance}type"
DIR_NAME = ['ANAGRAFE', 'BANCHE', 'CONTI_CORRENTI_DEPOSITI', 'CREDITI',
            'ESTERO', 'GARANZIE', 'PORTAFOGLIO', 'SIB2000', 'SOFFERENZE', 'TITOLI']
DATE_STRING = 'to_date($DT_RIFERIMENTO,"YYYY-MM-DD")'
ABI_STRING = '($ABI)'
LKP_TABLE_NAME = 'Lookup_ANAEDQODSTB00001N'
PRE_SQL_TABLES = ['"EDQSTGTB00001N"', '"EDQSTGTB00002N"']
