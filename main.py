import sys
from os import path, listdir
import csv
from re import match

#########
# UTILS #
#########
def error(msg):
    print(f"Error: {msg}")
    sys.exit()

def get_ftype(fpath):
    return path.basename(fpath).split(".")[-1]

def get_inpaths(dpath):
    return  [path.join(dpath, fname) for fname in listdir(dpath) if fname[-4:]==".csv" and not match("reformatted_", fname)]



###########
# PROGRAM #
###########
def process_inpath(inpath):
    if not "." in path.basename(inpath) or not get_ftype(inpath)=="csv":
        error("the file you provided has no file extension or is not a csv file.")

    try:
        f = open(inpath, "r", encoding='utf-8')
        reader = csv.reader(f)
    except (PermissionError, FileNotFoundError):
        error(f"unable to access file '{inpath}'. Either it doesn't exist or it's currently open on your computer.")

    email_courses = {} # courses corresponding to each email
    email_names = {} # name corresponding with each email
    first_row = True
    important_cols = ["course_name", "email", "firstname", "lastname"]
    cols = {}
    # returns the value of the column 'colname' in the current row .colname must be in important_cols.
    def get(colname): return row[cols[colname]]

    for row in reader:
        # print(row)
        if first_row: # assign col indicies
            for i, v in enumerate(row):
                if v in important_cols: cols[v]=i
            if len(cols)!=len(important_cols): 
                error(f"the following column(s) not found: {[c for c in important_cols if c not in cols]}. Update file to contain this column name.")
            first_row=False
            continue
        row = [row[0].replace("ï»¿", "")] + row[1:] # fix weird UTF-8 encoding thing
        row = row[0:-1] + [row[-1].replace("\n", "")]
    
        # parse course
        if not get("email") in email_courses: # init dict value
            email_courses[get("email")] = ""
        email_courses[get("email")] += f"{get('course_name')}\n"
        
        # parse name
        if not get("email") in email_names:
            email_names[get("email")]=[get("firstname"), get("lastname")]
    
    f.close()
    assert len(email_courses)==len(email_names) # invarient
    output = [["email", "courses", "firstname", "lastname"]] # headers
    for e, cs in email_courses.items():
        name = email_names[e] # avoid double dict lookup
        output.append([e, cs[:-1], name[0], name[1]]) # removes trailing newline from final course in courses
    return output


if __name__ == "__main__":
    # argument validation 
    if len(sys.argv)<2:
        csvs = get_inpaths(".")
        suffix = "" if len(csvs)==0 else f" Did you mean to run: \n>> python {sys.argv[0]} {csvs[0][2:]}" # give them arbritrary relevant suggestion
        error("no file to convert provided."+suffix)
    if len(sys.argv)>2:
        error("too many arguments. Provide a directory to process multiple files.")

    inpaths = get_inpaths(sys.argv[1]) if path.isdir(sys.argv[1]) else [sys.argv[1]]    
    for inpath in inpaths:
        output = process_inpath(inpath)
        outpath = f"reformatted_{path.basename(inpath)}"    
        try:
            f = open(outpath, "w", newline='', encoding='utf-8')
            csv.writer(f).writerows(output)
            f.close()
        except PermissionError:
            error(f"unable to write output. Close {outpath}!")

    print(f"Finished - processed {len(inpaths)} file{'' if len(inpaths)==1 else 's'}.")
