from code_dumper import dump
import sys

import_from_str = sys.argv[1]+'.'+sys.argv[2]
import_import_str = sys.argv[3]
#Please Change below path while running the testcases
BASEPATH='/Users/ritanshukeshari/Desktop/razorsdk-code-dumper/tests/test_code_dump'

mod = __import__(import_from_str, fromlist=[import_import_str])
klass = getattr(mod, import_import_str)


input_file_path=BASEPATH+'/'+sys.argv[1]+'/'+sys.argv[2]+'.py'
output_file_path=BASEPATH+'/'+(sys.argv[1]).replace('input','output')+'/'+sys.argv[2].replace('input','output')+'.py'

with open(output_file_path, "w") as f1:
    #INPUT_CODE
    ip_str= '#'*25 + ' '*5 + 'INPUT' + ' '*5 + '#'*30 + '\n'
    f1.write(ip_str)

    with open(input_file_path) as f:
        for line in f:
            f1.write(line)

    #INPUT_OBJECT_TO_DUMP
    ip_obj_str = '\n\n## Input Object to dump function : ' + sys.argv[3] + '\n\n'
    f1.write(ip_obj_str)

    ip_end_str = '#' * 25 + ' ' * 5 + 'INPUT ENDS HERE' + ' ' * 5 + '#' * 30 + '\n\n\n'
    f1.write(ip_end_str)

    #OUTPUT_CODE
    op_str = '#' * 25 + ' ' * 5 + 'OUTPUT' + ' ' * 5 + '#' * 30+ '\n'
    f1.write(op_str)

    try:
        output_str = dump(klass)
        f1.write(output_str)
    except:
        f1.write('\n\n ## Please check dump function not able to handle above code ## \n\n')
    op_end_str = '#' * 25 + ' ' * 5 + 'OUTPUT ENDS HERE' + ' ' * 5 + '#' * 30 + '\n'
    f1.write(op_end_str)










