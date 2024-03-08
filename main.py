import sys
from os import path
import csv

def error(msg):
    print(f"Error: {msg}")
    sys.exit()

def get_ftype(fpath):
    return path.basename(fpath).split(".")[-1]

if __name__ == "__main__":
    inpath = sys.argv[1] 
    
    #################### 
    # input validation #
    #################### 
    if not inpath:
        error("no file to convert provided.")

    if not "." in path.basename(inpath):
        error("the file you provided has no file extension. Must be a .csv file.")

    if not get_ftype(inpath)=="csv":
        error(f"input must be a .csv file. You provided a .{get_ftype(inpath)} file.")

    try:
        f = open(inpath, "r")
    except:
        error(f"unable to access file '{inpath}'. Either it doesn't exist or it's currently open on your computer.")


    ################ 
    # parsing data #
    ################ 
    reader = csv.reader(f)
    email_courses = {}
    first_row = True
    for row in reader:
        if first_row:
            first_row=False
            continue

        row = [row[0].replace("ï»¿", "")] + row[1:] # fix weird UTF-8 encoding thing
        row = row[0:-1] + [row[-1].replace("\n", "")]
        if len(row)!=4:
            error(f"file of unexpected format. this row has {len(row)} cols when it should have 4.\n{row}")
        if row[3] in email_courses:
            email_courses[row[3]].append(row[1])
        else:
            email_courses[row[3]] = [row[1]]
    
    f.close()

    output = []
    for e, cs in email_courses.items():
        output.append([e]+cs)

    ################ 
    # writing data #
    ################ 
    assert get_ftype(inpath)=="csv"
    outpath = f"reformatted_{path.basename(inpath)}"
    
    try:
        f = open(outpath, "w", newline='')
    except:
        error(f"unable to write output. Close {outpath}!")
     
    csv.writer(f).writerows(output)
    f.close()
