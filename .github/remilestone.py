import sys

import re
import os
import math
import sys
from itertools import groupby
import openiti.helper.ara as ara
from collections import Counter


def milestones(file, length, last_ms_cnt, log_file):
    print("adding milestones to", file)
    # ara_regex = re.compile("^[ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ]+$")
    # new char list without ZERO WIDTH NON-JOINER and ZERO WIDTH JOINER
    # ara_regex = re.compile("[ءآأؤإئابةتثجحخدذرزسشصضطظعغـفقكلمنهوىيًٌٍَُِّْ٠١٢٣٤٥٦٧٨٩ٮٰٹپچژکگیے۱۲۳۴۵]+")
    splitter = "#META#Header#End#"
    file_name = re.split("-[a-z]{3}\d{1}(\.(mARkdown|inProgress|completed))?$", file.split("/")[-1])[0]
    #print(file_name)
    if re.search("[A-Z]{1}$", file_name):
        continuous = True
    else:
        continuous = False

    with open(file, "r", encoding="utf8") as f:
        data = f.read()

        # splitter test
        if splitter in data:
            data_parts = re.split("\n*#META#Header#End#\n*", data)
            head = data_parts[0]
            # remove the final new line and spaces to avoid having the milestone tag in a new empty line
            text = data_parts[1].rstrip()
            # remove old milestone ids. Fixed strings, until we make them as user input, if required!
            text = re.sub(" *Milestone300", "", text)
            text = re.sub(" *ms[A-Z]?\d+", "", text)
            ms_remaining = re.findall("ms[A-Z]?\d+", text)
            ms_remaining2 = re.findall("Milestone300", text)
            if len(ms_remaining) > 1:
                log_file.write("\t\tremainig ids in %s \n" % file)
                log_file.write("\t\t\t", ms_remaining)
                return -1

            if len(ms_remaining2) > 1:
                log_file.write("\t\tremainig ids in %s \n" % file)
                log_file.write("\t\t\t", ms_remaining2)
                return -1

            # insert Milestones
            ara_toks_count = ara.ar_tok_cnt(text)
            # ara_toks_count = len(ara_regex.findall(text))

            ms_tag_str_len = len(str(math.floor(ara_toks_count / length)))
            # find all tokens to check the Arabic tokens in their positions
            all_toks = re.findall(r"\w+|\W+", text)

            token_count = 0
            ms_count = last_ms_cnt

            new_data = []
            for i in range(0, len(all_toks)):
                # check each token at its position
                # if ara.ar_tok.search(all_toks[i]):
                # if ara_regex.search(all_toks[i]):
                if re.search(ara.ar_tok, all_toks[i]):
                    token_count += 1
                    new_data.append(all_toks[i])
                else:
                    new_data.append(all_toks[i])

                if token_count == length or i == len(all_toks) - 1:
                    ms_count += 1
                    if continuous:
                        milestone = " ms" + file_name[-1] + str(ms_count).zfill(ms_tag_str_len)
                    else:
                        milestone = " ms" + str(ms_count).zfill(ms_tag_str_len)
                    new_data.append(milestone)
                    token_count = 0

            ms_text = "".join(new_data)

            test = re.sub(" ms[A-Z]?\d+", "", ms_text)
            if test == text:
                # print("\t\tThe file has not been damaged!")
                # Milestones TEST
                ms = re.findall("ms[A-Z]?\d+", ms_text)
                #print("\t\t%d milestones (%d words)" % (len(ms), length))
                dictOfIds = dict(Counter(ms))
                # Remove elements from dictionary whose value is 1, i.e. non duplicate items
                dictOfIds = { key:value for key, value in dictOfIds.items() if value > 1}
                #for key, value in dictOfIds.items():
                #    print('ID = ' , key , ' :: Repeated Count = ', value)
                if len(dictOfIds) == 0:
                    ms_text = head.rstrip() + "\n\n" + splitter + "\n\n" + ms_text
                    with open(file, "w", encoding="utf8") as f9:
                        f9.write(ms_text)
                    return ms_count
                else:
                    log_file.write("\t\tduplicate ids in %s \n" % file)
                    for key, value in dictOfIds.items():
                        log_file.write('ID = %s  :: Repeated Count = %d'  % (key, value))
            else:
                log_file.write("\t\tSomething got messed up... in %s \n" % file)
                return -1

        else:
            log_file.write("The %s is missing the splitter! \n" % file)
            return -1


if __name__ == "__main__":
    with open(".github/milestone_log.txt", "a") as log_f:
        milestones(sys.argv[1].strip(), 300, 0, log_f)
        
