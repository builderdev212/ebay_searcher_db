import re

data_set = ["1", "10", "100", "1,000", "10,000", "100,000", "1,000,000", "10,000,000", "100,000,000", "1,000,000,000", "10,000,000,000", "100,000,000,000", '[<h1 class="srp-controls__count-heading"><span class="BOLD">542,122</span> results for <span class="BOLD">gtx 970</span></h1>]']
output_set = []

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

current = 0
printProgressBar(current, 13,'Progress: [', ']')

for data in data_set:
    output_data = ""
    for num in re.findall(r">[,?\d+]+", data):
        output_data += num
    output_set.append(output_data)
    current += 1
    printProgressBar(current, 13,'Progress: [', ']')

print(output_set)
