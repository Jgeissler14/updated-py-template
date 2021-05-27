import glob
import json
import os
import traceback
import boto3
from re import search
import re
import logging
from botocore.exceptions import ClientError
from s3_upload import upload_file


# Directory variables (root dir, data dir, etc.)
import pandas

DATA_DIR = os.path.join(os.getcwd(), 'data')
DIR = os.getcwd()

#Path to input file(s)
file_list = ["/Users/joshua.geissler/Documents/GitHub/updated-py-template/sample_1.csv", 
"/Users/joshua.geissler/Downloads/sample_4.csv", 
"https://discover-s3-testing.s3.amazonaws.com/sample_2.csv", 
"https://discover-s3-testing.s3.amazonaws.com/random/sample_3.csv"]

def main():
    # This script will be executed in a container in a batch environment.

    # ######### Parameters ##########
    # Do not pass variables on the command line, read all the required parameters
    # from the ENV variables. Discover UI will collect the parameters needed and set them as ENV variables
    # at run time.

    # Example: Read a float value for threshold and default to 0.75 if missing
    # threshold = float(os.getenv("AD_THRESHOLD", 0.75))

    message = os.getenv("AD_MESSAGE", "Running a Sample Python Script on Discover")
    print(message)

    df = pandas.read_csv(os.path.join(DATA_DIR, 'icd10cm_codes_2020.csv'))

    # Discover UI uses 'results.json' file to display the output to use
    # For information on results.json format see: ???
    output_results = {"data": [], "data_type": "generated"}

    # Results object
    results_dict = {}

    for input_file in file_list:
        #boolean variable to track if input_file is local
        local = True

        #Check whether file is in s3, if not assume its local
        if search("s3.amazonaws.com", input_file):
            local = False
            #Use Regex to find the bucket and key matches
            Regex = re.search('https://(.+?).s3.amazonaws.com/(.*)', input_file)

            #s3 bucket name
            bucket_name = Regex.group(1)
            #Path to file inside bucket
            key = Regex.group(2)

            #Initialize S3 and set bucket
            s3 = boto3.resource('s3')
            my_bucket = s3.Bucket(bucket_name)

            path, filename = os.path.split(key)
            my_bucket.download_file(key, filename)

            #Set input_file to reference new local copy of the file
            input_file = os.path.join(os.getcwd(), filename)

            DIR = os.getcwd()

        else:
            DIR = os.path.dirname(input_file)

        df_in = pandas.read_csv(input_file, header=None, names=['code'])

        for c in df_in['code']:
            # lookup the code in data file
            if c in list(df['code']):
                results_dict[c] = [df.loc[df.code == c].description.values[0]]
            else:
                results_dict[c] = "***NOT FOUND***"

        # Create results dataframe from results_dict
        results_df = pandas.DataFrame(results_dict).transpose()

        # Save results file to csv file
        print(f'Saving results to {DIR} directory ...')

        # extract the input filename for generating related result files
        input_filename = os.path.splitext(os.path.basename(input_file))[0]

        output_filename = f'{input_filename}_result.csv'
        results_df.to_csv(os.path.join(DIR, output_filename), header=False)

        # Note: Use filename to display the content of a file, and link to generate a link to download results
        output_results["data"].append({
            "title": "Results",
            # "filename": output_filename,
            "link": output_filename,
        })

        #Upload Results to S3 if the file originated from there
        if not local:
            #if the file is inside of any folders within the S3 bucket we have to add the path and "/"
            if path:
                upload_file(input_file, bucket_name, path + "/" + output_filename)
            else:
                upload_file(input_file, bucket_name, output_filename)

    with open(os.path.join(DIR, "results.json"), "w+") as f:
        print("Writing results.json file")
        json.dump(output_results, f)
        f.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc()

        with open(os.path.join(os.getcwd(), "results.json"), "w+") as f:
            print("Writing errors in results.json file")
            json.dump({
                "data_type": "generated",
                "data": [
                    {"error": str(tb), "title": "Error"}
                ]
            }, f)
            f.close()