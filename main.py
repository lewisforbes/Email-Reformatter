import sys
from os import path, listdir
import csv
from re import match

def error(msg):
    print(f"Error: {msg}")
    sys.exit()

def get_ftype(fpath):
    return path.basename(fpath).split(".")[-1]

def get_inpaths(dpath):
    return  [path.join(dpath, fname) for fname in listdir(dpath) if fname[-4:]==".csv" and not match("reformatted_", fname)]

# returns the value of the column 'colname' in the current row
global_row = ""
def get(colname): # colname must be in important_cols.
    return global_row[cols[colname]]

if __name__ == "__main__":
    #################### 
    # input validation #
    #################### 
    if len(sys.argv)<2:
        csvs = get_inpaths(".")
        suffix = "" if len(csvs)==0 else f" Did you mean to run: \n>> python {sys.argv[0]} {csvs[0][2:]}" # give them arbritrary relevant suggestion
        error("no file to convert provided."+suffix)

    if len(sys.argv)>2:
        error("too many arguments. Provide a directory to process multiple files.")

    raw_in = sys.argv[1]

    inpaths = get_inpaths(raw_in) if path.isdir(raw_in) else [raw_in]
    
    for inpath in inpaths:
        if not "." in path.basename(inpath):
            error("the file you provided has no file extension. Must be a .csv file.")

        if not get_ftype(inpath)=="csv":
            error(f"input must be a .csv file. You provided a .{get_ftype(inpath)} file.")

        try:
            f = open(inpath, "r", encoding='utf-8')
        except:
            error(f"unable to access file '{inpath}'. Either it doesn't exist or it's currently open on your computer.")


        ################ 
        # parsing data #
        ################ 
        reader = csv.reader(f)
        email_courses = {} # courses corresponding to each email
        email_names = {} # name corresponding with each email
        first_row = True

        important_cols = ["course_name", "email", "firstname", "lastname"]
        cols = {}

        c_n = 0
        for row in reader:
            # print(row)
            global_row = row # for get()
            if first_row: # assign col indicies
                for i, v in enumerate(row):
                    if v in important_cols: cols[v]=i
                if len(cols)!=len(important_cols): 
                    error(f"the following column(s) not found: {[c for c in important_cols if c not in cols]}. Update file to contain this column name.")
                first_row=False
                continue
            c_n+=1
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

        ################ 
        # writing data #
        ################ 
        assert get_ftype(inpath)=="csv"
        outpath = f"reformatted_{path.basename(inpath)}"
        
        try:
            f = open(outpath, "w", newline='', encoding='utf-8')
        except:
            error(f"unable to write output. Close {outpath}!")
        
        csv.writer(f).writerows(output)
        f.close()

    print(f"Finished! Created rows for {len(email_courses)} people and {c_n} courses.")
