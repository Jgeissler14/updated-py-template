import glob
import json
import os
import traceback

# Directory variables (root dir, data dir, etc.)
import pandas

DATA_DIR = os.path.join(os.getcwd(), 'data')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
INPUT_DIR = os.path.join(os.getcwd(), 'input')


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

    for input_file in glob.glob(os.path.join(INPUT_DIR, "*.csv")):
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
        print(f'Saving results to {OUTPUT_DIR} directory ...')

        # extract the input filename for generating related result files
        input_filename = os.path.splitext(os.path.basename(input_file))[0]

        output_filename = f'{input_filename}_result.csv'
        results_df.to_csv(os.path.join(OUTPUT_DIR, output_filename), header=False)

        # Note: Use filename to display the content of a file, and link to generate a link to download results
        output_results["data"].append({
            "title": "Results",
            # "filename": output_filename,
            "link": output_filename,
        })

    with open(os.path.join(OUTPUT_DIR, "results.json"), "w+") as f:
        print("Writing results.json file")
        json.dump(output_results, f)
        f.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc()

        with open(os.path.join(OUTPUT_DIR, "results.json"), "w+") as f:
            print("Writing errors in results.json file")
            json.dump({
                "data_type": "generated",
                "data": [
                    {"error": str(tb), "title": "Error"}
                ]
            }, f)
            f.close()
