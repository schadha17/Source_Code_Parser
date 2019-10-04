'''
SOURCE CODE PARSER

This code can be used to automate checks on the source code before merging into
the build pipeline. It performs the following checks. 

    1. When a file is checked in, scans the file to count the total number of lines
    2. Scans the file to identify comments and count the total lines of comments in the file. 
    3. After identifying the lines of comments, it scans to segregate the total number of single line
    comments and the total number of multi-line comments.

    4. Any line of code that has a trailing comment is counted both as lines of code
    and also a comment line.
    5. From all the comments in the file, identifies and count the total number of TODOs.
    6. The files that is being checked in could be any valid program file. Files
    checked in without an extension are ignored. It ignores file names that start with a ‘.’.
'''

import constant as ct
#Hash map that enables O(1) lookup for comment syntax in supported programming languages
supported_file_extentions = {".js": ["//", ["/*", "*/"]], ".py": ['#', ["'''", "'''"]], ".java": ["//", ["/*", "*/"]]} #Programming languages supported by parser
stats = {}

'''
Function Name: 
    print_stats
Purpose: 
    Prints different stats 
'''
def print_stats():

    print("Total # of lines: ", stats["total_lines"])
    print("Total # of comment lines: ", stats["num_single_comment_lines"] + stats["num_lines_within_block_comments"])
    print("Total # of single line comments: ", stats["num_single_comment_lines"])
    print("Total # of comment lines within block comments: ", stats["num_lines_within_block_comments"])
    print("Total # of block line comments: ", stats['num_block_line_comments'])
    print("Total # of TODO: ", stats["num_todos"])

'''
Function Name: 
    validate_file_name
Purpose: 
    Checks if the file name is valid before parsing it 
Param: 
    file_name: represents name of the file entered by the user (input parameter)
'''
def validate_file_name(file_name):

    dot_index = file_name.rfind(".") #Finds the index of the '.' just before the extention name
    '''
    If file name starts with a '.', it's a hidden file that is ignored 
    If file name has no extention, it is ignored
    NOTE: dot_index also includes the edge cases where file name is empty
    '''
    if((dot_index == -1) or (file_name[0] == ".")):
        return [ct.ERR_NO_EXT, None] if (dot_index == -1) else [ct.ERR_HIDDEN, None]

    extension = file_name[dot_index: ]
    if(extension not in supported_file_extentions):
        return [ct.ERR_INVAL_EXT, extension]

    return [ct.VALID, extension]

'''
Function Name: 
    check_single_line_comment
Purpose: 
    Checks if the line in source code has the single line comment of the language in which source code is written
Param: 
    line:   contains a line in the source code (input parameter)
    syntax: it stores syntax of the comments (input parameter)
'''
def check_single_line_comment(line, syntax):

    single_line_comment_syntax = syntax[0]
    '''
    If single line comment found
    Covers both cases
        1. When a line in source code starts with single line comment
        2. When code is followed by a single line comment
    '''
    if(single_line_comment_syntax in line):
        stats["num_single_comment_lines"]+= 1


'''
Function Name: 
    check_todos
Purpose: 
    Checks for todo's inside the line in a source code
Param:
    line: a single line in source code (input parameter)
'''
def check_todos(line):
    todo_syntax = "TODO"
    if(todo_syntax in line):
        stats["num_todos"]+= 1

'''
Function Name: 
    check_multi_line_comment
Purpose: 
    Checks for multi-line comments
Param:
    line: a single line in source code (input parameter)
    syntax: comment syntax for programming language of the source code (input parameter)
    multi_line_comment_started: flag indicating if multi-line comment has started (output parameter)
'''
def check_multi_line_comment(line, syntax, multi_line_comment_started):

    start_multi_line_comment_syntax = syntax[1][0] #Syntax for starting multi-line comment
    end_multi_line_comment_syntax = syntax[1][1] #Syntax for ending multi-line comment

    if(multi_line_comment_started): #Multi line comment started before
        stats['num_lines_within_block_comments'] += 1

        if(end_multi_line_comment_syntax in line): #Multi line comment ended
            stats['num_block_line_comments'] += 1
            multi_line_comment_started = False

    elif(start_multi_line_comment_syntax in line): #Multi line comment starts with this line
        stats['num_lines_within_block_comments'] += 1
        multi_line_comment_started = True

    return multi_line_comment_started
    
'''
Function Name: 
    parse_file_content
Purpose: 
    Takes a file name and analyses it to compute stats
Param:
    file_name: Name of the source file (input parameter)
    syntax: comment syntax for programming language of the source code (input parameter)
'''
def parse_file_content(file_name, extension):

    multi_line_comment_started = False
    comment_syntax = supported_file_extentions[extension]
    
    try:
        f = open(file_name, "r") #Opening the file in Read mode
        contents = f.readlines()
            
    except FileNotFoundError:
        print('Error: File {} does not exist'.format(file_name))
        return

    #iterate over every line in source code (that is stored in contents) and parses it
    for line in contents:
        check_single_line_comment(line, comment_syntax)
        check_todos(line)
        multi_line_comment_started =  check_multi_line_comment(line, comment_syntax, multi_line_comment_started)
        stats["total_lines"]+= 1

    print_stats()

'''
Purpose: 
    Initiates execution of the program. This is where the program starts. 
    This function takes the input from the user, validates it and passes the filename to parse_file_content
'''
def main():

    stats["total_lines"] = 0
    stats["num_single_comment_lines"] = 0
    stats["num_block_line_comments"]  = 0
    stats["num_lines_within_block_comments"] = 0
    stats["num_todos"] = 0

    file_name = input("Enter filename for the source code: ").strip(" ") #Inputting file name and stripping extra spaces
    is_valid, ext = validate_file_name(file_name) 
    
    if(is_valid!= ct.VALID):
        print("Ignoring {} ".format(file_name))

        if(is_valid == ct.ERR_NO_EXT):
            print("Please include extention in the file name")
            
        elif(is_valid == ct.ERR_HIDDEN):
            print("Please make sure that source code file {} is not hidden".format(file_name))
            
        else: #is_valid is set to ERR_INVAL_EXT
            print("List of supported extentions:")
            print(str(supported_file_extentions.keys()).strip("dict_keys ( ) ")) #printing supported extentions useful for user

            try:
                raise Exception("Source code extention {} is not supported by the parser!!".format(ext))
            except Exception as err:
                print("Exception: ", err)
        return

    parse_file_content(file_name, ext)

if (__name__ == "__main__"): #Means this file is not imported as a module
    main()

